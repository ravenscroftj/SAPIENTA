"""
This module is used to coordinate jobs between workers
"""
import sqlite3
import logging
import zlib
import cPickle
import os

from SimpleXMLRPCServer import SimpleXMLRPCServer
from multiprocessing import Lock

from sapienta import app

config = app.config

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class Coordinator:

    def __init__(self):
        """Set up the coordinator object"""
        self.logger = logging.getLogger(__name__)
        self.outdir = config['OUTPUT_DIRECTORY']
        
    def _initdb(self):
        """Set up temporary database for jobs"""
        self.dblock = Lock()
        
        self.dbconn = sqlite3.connect(':memory:')
        self.dbconn.row_factory = dict_factory

        self.logger.info("Setting up job management database...")

        with self.dbconn:
            self.dbconn.execute("""CREATE TABLE jobs(jobid INTEGER PRIMARY KEY, 
                    filename VARCHAR, 
                    status VARCHAR, 
                    error VARCHAR)""")

    def _initserver(self):
        """Set up XMLRPC server"""
        self.logger.info("Establishing job server")
        self.server = SimpleXMLRPCServer((config['COORD_ADDRESS'], config['COORD_PORT']), 
                logRequests=False,allow_none=True)

        self.server.register_function(lambda filename: self.queue_job(filename),
                "queue_job")

        self.server.register_function(lambda: self.get_work(), "get_work")
        self.server.register_function(lambda x: self.return_result(x), "return_result")

        self.server.register_function(lambda jobid: self.get_result(jobid), "get_result")


    def run(self):
        """Initialise and run the xmlrpcserver"""
        self._initserver()
        self._initdb()
        self.logger.info("Listening for clients and workers on %s:%d", 
                config['COORD_ADDRESS'], config['COORD_PORT'])
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()

    def return_result(self, incoming):
        """Save a processed paper to the database"""
        self.logger.info("Incoming result...")
        result, tdiff = cPickle.loads(zlib.decompress(incoming.data))

        from sapienta.processing.worker import PreprocessingException

        if(isinstance(result, PreprocessingException)):
            #process failure
            self.logger.info("Job %d failed to process", result.jobid)

            self.dblock.acquire()
            curr = self.dbconn.cursor()
            curr.execute("UPDATE JOBS SET status='FAILED', error=? WHERE jobid=?",(
                result.traceback, jobid))
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
            curr.execute("UPDATE jobs SET filename=?, status=? WHERE jobid=?",
                    (outpath, "DONE", jobid))

            self.dblock.release()


    def get_work(self):
        """Get a job from the database"""

        import xmlrpclib

        self.logger.debug("Worker has requested a job")

        self.dblock.acquire()

        curr = self.dbconn.cursor()

        with self.dbconn:
            curr.execute("SELECT * FROM jobs WHERE status='PENDING' LIMIT 1")

            r = curr.fetchone()

            if r != None:
                print r
                self.logger.info("Assigning job %d to worker", r['jobid'])
                curr.execute("UPDATE jobs SET status='WORKING' WHERE jobid=?", (r['jobid'],))
            else:
                rval = None

        self.dblock.release()

        
        if r != None:
            #get file data
            with open(r['filename'],'rb') as f:
                data = f.read()

            rval = r['jobid'], r['filename'], data

        return xmlrpclib.Binary(zlib.compress(cPickle.dumps(rval)))
        
        

    def queue_job(self, filename):
        """Enqueue a new processing job and return a unique ID"""

        self.dblock.acquire()
        curr = self.dbconn.cursor()

        with self.dbconn:
            curr.execute("INSERT INTO jobs(filename, status) VALUES(?,?)", (filename, 'PENDING'))

        id = curr.lastrowid
        
        self.dblock.release()

        return id

    def get_result(self, job_id):
        """Get the current status of job ID
        
        This method will return a dict:
        status   - either 'pending', 'working' or 'done'
        filename - a value for filename is only provided when status=done
        """

        self.dblock.acquire()
        curr = self.dbconn.cursor()

        with self.dbconn:
            curr.execute("SELECT * FROM jobs WHERE jobid=?", (job_id,) )
            result = curr.fetchone()

            if result['status'] == "DONE":
                curr.execute("DELETE FROM jobs WHERE jobid=?", (job_id,))

        self.dblock.release()
        return {x: result[x] for x in result.keys() if result[x] != None }

