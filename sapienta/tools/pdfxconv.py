#!/usr/bin/env python
'''
This script enables the conversion of a PDF document to XML recognised by Sapienta via pdfx

'''
import sys
import os
import logging

from optparse import OptionParser
from sapienta.tools.converter import PDFXConverter
from sapienta.tools.annotate import Annotator
from sapienta.tools.split import SentenceSplitter


def main():
    
    usage = "usage: %prog [options] file1.pdf [file2.pdf] "
    
    parser = OptionParser(usage=usage)
    parser.add_option("-s", "--split-sent", action="store_true", dest="split",
        help="If true, split sentences using NLTK sentence splitter")
    parser.add_option("-a", "--annotate", action="store_true", dest="annotate",
        help="If true, annotate the sentence-split XML with CoreSC labels")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
        help="If set, provides more verbose output")
    parser.add_option("--blacklist", help="Add elements to blacklisted splitter elements", 
            dest="extra_blacklist", default="")
    
    (options, args) = parser.parse_args()

    if(options.verbose):
        logging.basicConfig(level=logging.DEBUG)
        logging.debug("Verbose mode on.")
    else:
        logging.basicConfig(level=logging.INFO)

    if( len(args) < 1):
        parser.print_help()
        sys.exit(1)
 
    for infile in args:
        name,ext = os.path.splitext(infile)

        if not(os.path.exists(infile)):
            print "Input file %s does not exist" % infile
            continue

        outfile = name + ".xml"

        p = PDFXConverter()

        #annotation requires splitting
        if(options.annotate):
            options.split = True

                
        if(ext == ".pdf"):

            logging.info("Converting %s", infile)
            
            p.convert(infile, outfile)
            split_infile = outfile
            
        elif( ext == ".xml"):
            print "No conversion needed on %s" % infile
            split_infile = infile

        else:
            logging.info("Unrecognised format for file %s", infile)
            sys.exit(0)

        if(options.split):
            logging.info("Splitting sentences in %s", infile)
            
            s = SentenceSplitter()
            outfile = name + "_split" + ext
            
            eb = options.extra_blacklist.split(",")

            s.split(split_infile, outfile, extra_blacklist=eb)

            anno_infile = outfile

        if(options.annotate):
            a = Annotator()

            #build annotated filename
            outfile = name + "_annotated" + ext
            logging.info("Annotating file and saving to %s", outfile)
            a.annotate( anno_infile, outfile )



if __name__ == "__main__":
    main()
