"""
Class that serves the coordinator and annotates/splits
"""
import os
import sys
import traceback
import time
import tempfile
import logging
import zlib
import cPickle
import signal
import logging
import xmlrpclib
import threading

from multiprocessing import Pool, Process
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

from optparse import OptionParser

from sapienta.tools.converter import PDFXConverter
from sapienta.tools.annotate import Annotator
from sapienta.tools.split import SentenceSplitter

from sapienta import app

config = app.config


def test(*args):
   print args

#-------------------------------------------------------------------------------

class WorkerServerHandler:
    """XMLRPC methods for the worker"""

    def __init__(self, pool, coord):
        self.pool = pool
        self.coord = coord

#------------------------------------------------------------------------------------------------
            
    def _dispatch(self, method, params):
         try: 
             return getattr(self, method)(*params)
         except:
             import traceback
             traceback.print_exc()
             raise

#------------------------------------------------------------------------------------------------
    def do_job(self, jobblob):
        job = cPickle.loads(zlib.decompress(jobblob.data))
        coord = self.coord
        #process_paper(job,coord)
        pool = self.pool
        self.pool.apply_async(process_paper, [job,self.coord])
        return 1
        

def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)

class WorkerClient:
    """Main class that deals with the Coordinator module"""

    def __init__(self, evt, coord_addr=None, listen_addr=None, processes=None):
        """Set up a worker object """
        if coord_addr != None:
            self.remote_addr = coord_addr
        else:
            self.remote_addr = (config['COORD_ADDRESS'], config['COORD_PORT'])

        if listen_addr != None:
            self.listen_addr = listen_addr
        else:
            self.listen_addr = (config['WORKER_ADDRESS'], config['WORKER_PORT'])


        self.processes = processes

        if self.processes != None:
            self.processes = int(self.processes) 

        self.logger = logging.getLogger(__name__)
        self.evt = evt

    def run(self):
        """Run the worker object and process papers"""
        
        p = Pool(processes=self.processes, initializer=init_worker)

        uri = "http://%s:%d/" % (self.remote_addr[0],int(self.remote_addr[1]))

        self.logger.info("Connecting to XML-RPC server on '%s'", uri)

        qm = xmlrpclib.ServerProxy(uri)

        self.server = SimpleXMLRPCServer(self.listen_addr, 
                logRequests=False,allow_none=True)

        workerhandler = WorkerServerHandler(p, self.remote_addr)
        worker_id = self.server.register_instance(workerhandler)

        self.logger.info("Starting worker with %d threads", len(p._pool))

        qm.register_worker(self.listen_addr[0], self.listen_addr[1], len(p._pool))

        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.logger.warn("Interrupted by keyboard...")

        qm.unregister_worker(worker_id)

        #now kill off the processes
        p.close()
        p.join()
        

#-------------------------------------------------------------------------------

class PaperWorker:
    
    def __init__(self, logger, outdir):
        self.logger = logger
        self.outdir = outdir
    
    def process(self, filename):
        basename = os.path.basename(filename)
        self.name,ext = os.path.splitext(basename)

        infile = filename

        #if pdf, convert
        if ext == ".pdf":
            infile = self.convertPDF(infile)

        #run XML splitter
        infile = self.splitXML(infile)

        #run XML annotation
        infile = self.annotateXML(infile)


        with open(infile,'rb') as f:
            data = f.read()

        return infile
        #return infile, type

    def annotateXML(self, infile):
        """Routine to start the SAPIENTA process call"""
        
        outfile = os.path.join(self.outdir,  self.name + "_final.xml")
        
        self.logger.info("Annotating paper %s", infile)

        a = Annotator()
        a.annotate( infile, outfile )

        return outfile

    def convertPDF(self, infile):
        """Small routine for starting the PDF conversion call
        """

        self.logger.info("Converting %s to xml", infile)

        p = PDFXConverter()

        outname = os.path.join(self.outdir,self.name + ".xml")

        p.convert(infile, outname)

        return outname

    def splitXML(self, infile):
        """Routine for starting XML splitter call"""

        self.logger.info("Splitting sentences in %s",  infile)
        
        outfile = os.path.join(self.outdir,  self.name + "_split.xml")

        s = SentenceSplitter()
        s.split(infile, outfile)

        return outfile

    def convertPDF(self, infile):
        """Small routine for starting the PDF conversion call
        """

        self.logger.info("Converting %s to xml", infile)

        p = PDFXConverter()
        outfile = os.path.join(self.outdir, self.name + ".xml")
        p.convert(infile, outfile)

        return outfile

#---------------------------------------------------------------------


class PreprocessingException(Exception):

    #exc_type, exc_obj, exc_tb = sys.exc_info()
    jobid = ""
    files = []
    traceback = None
    pdf = False

#---------------------------------------------------------------------


def process_paper( incoming, server ):

    import traceback
    import threading

    try:

        tstart = time.time()

        jobid, filename, data = incoming

        workdir = tempfile.mkdtemp()
        
        logger = logging.getLogger(__name__ + ":" + threading.currentThread().name
    )
        logger.info("Starting worker...")

        w = PaperWorker(logger,workdir)

        name = os.path.join(workdir,os.path.basename(filename))

        with open(name, 'wb') as f:
            f.write(data)

        r = None

        try:
            resultfile = w.process(name)

            with open(resultfile,'rb') as f:
                data = f.read()

            r = jobid, os.path.basename(resultfile), data

        except Exception as e:

            #get exception information and dump to user
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error processing paper %s: %s",
                filename,e)
            
            for line in traceback.format_tb(exc_tb):
                logger.error(line)

            p = PreprocessingException(e)
            p.traceback = traceback.format_exc()
            p.jobid = jobid
            r = p

        finally:
            logger.info("Cleaning up work directory %s", workdir)
            for root,dirs,files in os.walk(workdir):
                for file in files:
                    os.unlink(os.path.join(root,file))

                for dir in dirs:
                    os.rmdir(os.path.join(root,dir))

            os.rmdir(workdir)

        tend = time.time()

        tdiff = tend - tstart

        logger.info("Took %d seconds to process job %d",tdiff, jobid) 
        uri = "http://%s:%d/" % server
        logger.info("Connecting to XML-RPC server on '%s'", uri)

        qm = xmlrpclib.ServerProxy(uri)

        result_data = zlib.compress(cPickle.dumps( (r,tdiff) ))
        logger.info("Returning results to server at %s", uri)
        qm.return_result(xmlrpclib.Binary(result_data))
        logger.info("Returned result to server...")
    except:
        logger.info(traceback.format_exc())


#--------------------------------------------------------------------------

def main():

    usage = "usage: %prog [options] <server> <port>"

    parser = OptionParser(usage=usage)

    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
        help="If set, run the client in verbose mode")

    parser.add_option("-p", "--processes", action="store", dest="processes",
        default=None, help="Number of threads to run, defaults to number of cores on your CPU")


    (options, args) = parser.parse_args()


    if(options.verbose):
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if(len(args) < 2):
        parser.print_help()
        sys.exit(1)
    else:
        server   = args[0]
        port     = args[1]

    pevt = threading.Event()

    try:
        w = WorkerClient(pevt, (server,port), processes = options.processes)
        p = Process(target=lambda:w.run())
        p.start()
        while 1:
            raw_input()
    except KeyboardInterrupt:
        pevt.set()

#--------------------------------------------------------------------------

if __name__ == "__main__":
    main()
