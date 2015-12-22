#!/usr/bin/env python
'''
This script enables the conversion of a PDF document to XML recognised by Sapienta via pdfx

'''
import time
import sys
import os
import logging
import signal

from multiprocessing import Pool,Queue,current_process

import sapienta

from optparse import OptionParser
from sapienta.tools.converter import PDFXConverter
from sapienta.tools.annotate import Annotator


#from sapienta.tools.split import SentenceSplitter as Splitter
from sapienta.tools.sssplit import SSSplit as Splitter

#these are globals that are populated by each worker process
my_anno = None
my_pdfx = None
my_splitter = None
logger  = None
options = None
resultq = None

def init_worker(q, rq=None):
    global my_anno, my_pdfx, logger, my_splitter, resultq


    signal.signal(signal.SIGINT, signal.SIG_IGN)

    i,config = q.get()
    resultq = rq
    logger = logging.getLogger("pdfxconv:worker%d" % i )

    logger.info("Initializing PDF splitter")
    my_pdfx = PDFXConverter()

    logger.info("Initialising sentence splitter")
    my_splitter = Splitter()

    logger.info("Initialising annotator %d", i)
    my_anno = Annotator(config=config, logger=logger)

    logger.info("Using C&C server %s", config['SAPIENTA_CANDC_SOAP_LOCATION'])


def anno_e(work):
    try:
        annotate(work)
    except KeyboardInterrupt, e:
        pass

def annotate(work):
    global my_anno, my_pdfx, my_splitter, logger, resultq

    infile, options = work

    name,ext = os.path.splitext(infile)

    bmk = {}

    if not(os.path.exists(infile)):
        logger.warning("Input file %s does not exist", infile)
        return

    if options.benchmark:
        bmk['paper'] = name
        bmk['start'] = time.clock()
        bmk['size']  = os.path.getsize(infile)



    outfile = name + ".xml"


    #annotation requires splitting
    if(options.annotate):
        options.split = True

            
    if(ext == ".pdf"):

        logging.info("Converting %s", infile)


        if options.benchmark:
            bmk['pdfx_start'] = time.clock()
       
        p.convert(infile, outfile)
        split_infile = outfile

        if options.benchmark:
            bmk['pdfx_stop'] = time.clock()
       

        
    elif( ext == ".xml"):
        logging.info("No conversion needed on %s", infile)
        split_infile = infile

    else:
        logging.info("Unrecognised format for file %s", infile)
        return

    if(options.split):
        logging.info("Splitting sentences in %s", infile)

        outfile = name + "_split.xml"
        
        if options.benchmark:
            bmk['split_start'] = time.clock()
       
        my_splitter.split(split_infile, outfile)


        if options.benchmark:
            bmk['split_stop'] = time.clock()
       

        anno_infile = outfile

    if(options.annotate):

        #build annotated filename
        outfile = name + "_annotated.xml"
        logging.info("Annotating file and saving to %s", outfile)


        if options.benchmark:
            bmk['anno_start'] = time.clock()

        my_anno.annotate( anno_infile, outfile )

        if options.benchmark:
            bmk['anno_start'] = time.clock()

    if options.benchmark:
        resultq.put(bmk)




def main():
    
    usage = "usage: %prog [options] file1.pdf [file2.pdf] "
    
    parser = OptionParser(usage=usage)
    parser.add_option("-s", "--split-sent", action="store_true", dest="split",
        help="If true, split sentences using NLTK sentence splitter")

    parser.add_option("--splitter", dest="splitter", default="sssplit", 
            help="Choose which sentence splitter to use [sssplit,textsentence]")
    parser.add_option("-a", "--annotate", action="store_true", dest="annotate",
        help="If true, annotate the sentence-split XML with CoreSC labels")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
        help="If set, provides more verbose output")
    parser.add_option("--blacklist", help="Add elements to blacklisted splitter elements", 
            dest="extra_blacklist", default="")

    parser.add_option("--benchmark", help="Record results of annotations", dest="benchmark",
            action="store_true")

    parser.add_option("--parallel", help="Specify how many cpus to use", dest="cpus", type=int, default=1)

    parser.add_option("--candc-hosts", help="List of URLS that C&C is running on", dest="candc", default="http://localhost:9004/")
    
    (options, args) = parser.parse_args()

    candc_hosts = options.candc.split(",")

    if(options.verbose):
        logging.basicConfig(level=logging.DEBUG)
        logging.debug("Verbose mode on.")
    else:
        logging.basicConfig(level=logging.INFO)

    if( len(args) < 1):
        parser.print_help()
        sys.exit(1)

    if options.cpus > 0:
        q = Queue()
        rq = Queue()
        for i in range(0, options.cpus):
            myconf = dict(**sapienta.app.config)

            if i < len(candc_hosts):
                myconf['SAPIENTA_CANDC_SOAP_LOCATION'] = candc_hosts[i]
            else:
                x = i % len(candc_hosts)
                myconf['SAPIENTA_CANDC_SOAP_LOCATION'] = candc_hosts[x]

            q.put((i,myconf))

        p = Pool(processes=options.cpus, initializer=init_worker, initargs=[q,rq])

        try:
            p.map(anno_e, [ (x,options) for x in args] )
        except KeyboardInterrupt:
            print "Killing workers"
            p.terminate()
            p.join()

    if options.benchmark:
        logging.info("Storing benchmark data")
        import csv

        with open("benchmark.csv", "wb") as f:
            w = csv.writer(f)
            w.writerow(["file","size", "pdftime", "splittime", "annotime"])

            while not rq.empty():
                bmk = q.get()
    
                result = [bmk['paper'], bmk['size']]

                if 'pdfx_start' in bmk:
                    result.append(bmk['pdfx_start'] - bmkpdf['pdfx_stop'])
                else:
                    result.append(0)


                if 'split_start' in bmk:
                    result.append(bmk['split_start'] - bmkpdf['split_stop'])
                else:
                    result.append(0)


                if 'anno_start' in bmk:
                    result.append(bmk['anno_start'] - bmkpdf['anno_stop'])
                else:
                    result.append(0)

                w.writerow(result)

if __name__ == "__main__":
    main()
