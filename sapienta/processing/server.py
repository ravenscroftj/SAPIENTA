"""
This module is used to coordinate jobs between workers
"""
import sqlite3
import logging
import zlib
import cPickle
import os
import xmlrpclib


from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from multiprocessing import Lock

from sapienta import app

config = app.config

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

DEFAULT_LISTEN_ADDRESS = (config['COORD_ADDRESS'], config['COORD_PORT'])

class CoordinatorServerHandler:
    """Handler for calls to the coordinator XML-RPC server"""

#------------------------------------------------------------------------------------------------

    def __init__(self, outdir):
        self.dbconn = sqlite3.connect(':memory:')
        self.dbconn.row_factory = dict_factory
        self.dblock = Lock()
        self.logger = logging.getLogger(__name__)
        self.logger.info("Setting up job management database...")

        self.outdir = outdir

        with self.dbconn:
            self.dbconn.execute("""CREATE TABLE jobs(jobid INTEGER PRIMARY KEY, 
                    filename VARCHAR, 
                    status VARCHAR, 
                    error VARCHAR)""")

            self.dbconn.execute("""CREATE TABLE workers(workerid INTEGER PRIMARY KEY,
                    host VARCHAR,
                    port INTEGER)""")

            self.dbconn.execute("""CREATE TABLE slots(slotid INTEGER PRIMARY KEY,
                    workerid INTEGER,
                    jobid INTEGER)""")

#------------------------------------------------------------------------------------------------
            
    def _dispatch(self, method, params):
        
        if hasattr(self,method):
             try: 
                 return getattr(self, method)(*params)
             except:
                 import traceback
                 traceback.print_exc()
                 raise

#------------------------------------------------------------------------------------------------

    def register_worker(self, host, port, slots):
        """Method called when a worker comes online"""
        self.logger.info("Registering worker at %s:%d with %d slots", host,port,slots)
        self.dblock.acquire()

        curr = self.dbconn.cursor()

        with self.dbconn:
            curr.execute("INSERT INTO workers(host,port) VALUES(?,?)", (host,port))
            worker_id = curr.lastrowid
            
            self.logger.debug("Registered worker %s:%d with ID %d",
                    host,port, worker_id)

            for i in range(0,slots):
                self.logger.debug("Created worker slot for worker with ID %d", worker_id)
                curr.execute("INSERT INTO slots(workerid, jobid) VALUES(?,?)", 
                        (worker_id,-1))

        self.dblock.release()

        return worker_id

#------------------------------------------------------------------------------------------------

    def unregister_worker(self, workerid):
        """Method called when a worker goes offline"""

        self.dblock.acquire()
        curr = self.dbconn.cursor()

        with self.dbconn:
            curr.execute("SELECT host,port FROM workers WHERE workerid=?", (workerid,))

            r = curr.fetchone()

            if r != None:
                self.logger.info("Unregistering %s:%d as worker", r['host'], r['port'])
                curr.execute("DELETE FROM workers WHERE workerid=?", (workerid,))
                curr.execute("DELETE FROM slots WHERE workerid=?", (workerid,))
            else:
                self.logger.warn("No such worker with ID %d", workerid)
        self.dblock.release()
        return r != None

#------------------------------------------------------------------------------------------------

    def get_stats(self):
        """Return status information (used by web frontend)"""

        self.dblock.acquire()

        curr = self.dbconn.cursor()

        stats = {}

        with self.dbconn:
            curr.execute("SELECT COUNT(*) as count FROM workers")
            
            stats['workers'] = curr.fetchone()['count']

            curr.execute("SELECT COUNT(*) as count FROM slots")

            stats['slots'] = curr.fetchone()['count']

            curr.execute("SELECT COUNT(*) as count FROM jobs WHERE status='PENDING'")
            stats['pending'] = curr.fetchone()['count']

            curr.execute("SELECT COUNT(*) as count FROM jobs WHERE status='WORKING'")
            stats['working'] = curr.fetchone()['count']

        self.dblock.release()

        return stats


#------------------------------------------------------------------------------------------------
    def return_result(self, incoming):
        """Save a processed paper to the database"""

        self.logger.info("Incoming result...")
        result, tdiff = cPickle.loads(zlib.decompress(incoming.data))

        from sapienta.processing.worker import PreprocessingException

        if(isinstance(result, PreprocessingException)):
            jobid = result.jobid
            #process failure
            self.logger.info("Job %d failed to process", jobid)

            self.dblock.acquire()
            curr = self.dbconn.cursor()
            curr.execute("UPDATE JOBS SET status='FAILED', error=? WHERE jobid=?",(
                result.traceback, result.jobid))
            self.dblock.release()

        else:
            jobid, filename, data = result

            self.logger.info("Writing result to %s", os.path.basename(filename))
            #write the data to output directory
            outpath = os.path.join(self.outdir, os.path.basename(filename))
            with open(outpath, 'wb') as f:
                f.write(data)

            #store result in database
            self.dblock.acquire()

            curr = self.dbconn.cursor()
            with self.dbconn:
                curr.execute("UPDATE jobs SET filename=?, status=? WHERE jobid=?",
                    (outpath, "DONE", jobid))

            self.dblock.release()

         #now restore worker slot and get more work
        self.dblock.acquire()
        self.logger.info("Freeing up worker slot for jobid=%s", jobid)
         
        curr = self.dbconn.cursor()

        with self.dbconn:
            curr.execute("UPDATE slots SET jobid=-1 WHERE jobid=?", (jobid,))
        
        self.dblock.release()

        self.get_work()



    def get_work(self):
        """Get a job from the database"""


        self.dblock.acquire()

        #first we need to try and find a worker slot
        curr = self.dbconn.cursor()

        self.logger.info("Attempting to allocate a job to a worker...")

        r = None

        with self.dbconn:
            curr.execute("SELECT * FROM slots")
            curr.execute("SELECT * FROM slots WHERE jobid=-1")
            slot = curr.fetchone()

            if slot != None:

                self.logger.info("Found free work slot...")

                curr.execute("SELECT * FROM workers WHERE workerid=?", (slot['workerid'],))
                worker = curr.fetchone()

                self.logger.info("Finding a pending job...")

                with self.dbconn:
                    curr.execute("SELECT * FROM jobs WHERE status='PENDING' LIMIT 1")

                    r = curr.fetchone()

                    if r != None:
                        self.logger.info("Assigning job %d to worker %d", r['jobid'], slot['workerid'])
                        curr.execute("UPDATE jobs SET status='WORKING' WHERE jobid=?", (r['jobid'],))
                        curr.execute("UPDATE slots SET jobid=? WHERE slotid=?", (r['jobid'], slot['slotid']))
                    else:
                        rval = None

        self.dblock.release()

        
        if r != None:
            #get file data
            with open(r['filename'],'rb') as f:
                data = f.read()

            rval = r['jobid'], r['filename'], data

            uri = "http://%s:%d/" % (worker['host'], worker['port'])
            w = xmlrpclib.ServerProxy(uri)
            jobblob = xmlrpclib.Binary(zlib.compress(cPickle.dumps(rval)))
            w.do_job(jobblob)


    def queue_job(self, fname, datablob):
        """Enqueue a new processing job and return a unique ID"""

        self.dblock.acquire()
        curr = self.dbconn.cursor()

        data = zlib.decompress(datablob.data)

        filename = os.path.join(self.outdir, os.path.basename(fname))

        with open(filename,'wb') as f:
            f.write(data)

        with self.dbconn:
            curr.execute("INSERT INTO jobs(filename, status) VALUES(?,?)", (filename, 'PENDING'))

        id = curr.lastrowid

        self.dblock.release()

        self.get_work()

        return id

    def get_status(self, job_id):
        """Get the current status of job ID
        
        This method will return a dict:
        status   - either 'pending', 'working' or 'done'
        """

        self.dblock.acquire()
        curr = self.dbconn.cursor()

        with self.dbconn:
            curr.execute("SELECT * FROM jobs WHERE jobid=?", (job_id,) )
            result = curr.fetchone()

        self.dblock.release()
        return {x: result[x] for x in result.keys() if result[x] != None }

    def get_result(self, job_id):
        """If a job is done, return the output, else return None
        
        You should use get_status to find out if the job is done or not
        """

        self.dblock.acquire()
        curr = self.dbconn.cursor()

        with self.dbconn:
            curr.execute("SELECT * FROM jobs WHERE jobid=? AND status='DONE'",(job_id,))
            result = curr.fetchone()
        self.dblock.release()

        if result != None:
            with open(result['filename'], 'rb') as f:
                data = f.read()
            
            return xmlrpclib.Binary(zlib.compress(data))
        else:
            return None

#---------------------------------------------------------------------------------


class Coordinator:

    def __init__(self,addr=DEFAULT_LISTEN_ADDRESS, outdir = config['OUTPUT_DIRECTORY'] ):
        """Set up the coordinator object"""
        self.outdir = outdir
        self.addr = addr
        self.logger = logging.getLogger(__name__)

    def _initserver(self):
        """Set up XMLRPC server"""
        self.logger.info("Establishing job server")
        self.server = SimpleXMLRPCServer(self.addr, 
                logRequests=False,allow_none=True)

        self.server.register_instance(CoordinatorServerHandler(self.outdir))

    def run(self):
        """Initialise and run the xmlrpcserver"""
        self._initserver()
        self.logger.info("Listening for clients and workers on %s:%d", 
                config['COORD_ADDRESS'], config['COORD_PORT'])
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.logger.warn("Interrupted by keyboard...")




#-------------------------------------------------------------------------------
