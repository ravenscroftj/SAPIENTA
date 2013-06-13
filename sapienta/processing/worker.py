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

from multiprocessing import Pool, Queue, Process
from Queue import Empty

from optparse import OptionParser

from sapienta.tools.converter import PDFXConverter
from sapienta.tools.annotate import Annotator
from sapienta.tools.split import SentenceSplitter

from sapienta import app

config = app.config

#-------------------------------------------------------------------------------


def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)

class WorkerClient:
    """Main class that deals with the Coordinator module"""
    def __init__(self, evt, coord_addr=None, processes=None):
        """Set up a worker object """
        if coord_addr != None:
            self.remote_addr = coord_addr
        else:
            self.remote_addr = (config['COORD_ADDRESS'], config['COORD_PORT'])
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

        self.logger.info("Starting worker with %d threads", len(p._pool))

        results = Queue()

        while not self.evt.is_set():

            #process and return any results
            while not results.empty():
                self.logger.debug("Get an item off the queue")
                try:
                    r = results.get(block=False)
                    result_data = zlib.compress(cPickle.dumps(r))
                    qm.return_result(xmlrpclib.Binary(result_data))
                except Empty:
                    self.logger.debug("Couldn't get an item off the results queue, retry")
                    continue;


            try:
                self.logger.debug("Trying to get something to do...")
                
                job = cPickle.loads(zlib.decompress(qm.get_work().data))

                if(job == None):
                    self.logger.debug("Nothing to do, sleeping...")
                    time.sleep(1)
                else:
                    p.apply_async(process_paper, [job], callback=lambda x: results.put(x))
             
            except KeyboardInterrupt as e:
                self.logger.warn("Interrupted client")
                break

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


def process_paper( incoming ):

    import threading

    tstart = time.time()

    jobid, filename, data = incoming

    workdir = tempfile.mkdtemp()
    
    logger = logging.getLogger(__name__ + ":" + threading.currentThread().name
)

    w = PaperWorker(logger,workdir)

    name = os.path.join(workdir,os.path.basename(filename))

    with open(name, 'wb') as f:
        f.write(data)

    r = None

    try:
        resultfile = w.process(name)

        with open(resultfile,'rb') as f:
            data = f.read()

        r = jobid, filename, data

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

    logger.info("Took %d seconds to process paper",tdiff) 

    return r, tdiff



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
