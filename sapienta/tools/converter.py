'''
Library for converting PDF to minimal sapienta xml

'''

import os
import codecs
import requests

from xml.dom import minidom


PDFX_URL = "http://pdfx.cs.man.ac.uk"
GROBID_URL = os.environ.get("GROBID_HOST", "http://localhost:8070") + "/api/processFulltextDocument"


class PDFXConverter:

    # -------------------------------------------------------------------------
    def convert(self, filename, outfile):

        pdfsize = os.path.getsize(filename)

        header = ["Content-Type: application/pdf",
                  "Content-length: " + str(pdfsize)]

        f = open(filename, 'rb')

        response = requests.post(PDFX_URL, headers={"Content-Type": "application/pdf"}, data=f)


        print("Uploading %s..." % filename)

        f.close()

        print("Saving XML from %s..." % filename)

        self.indoc = minidom.parseString(response.text)

        print("Writing result to %s" % outfile)
        # write resulting xml file
        with codecs.open(outfile, 'w', encoding='utf-8') as f:
            self.indoc.writexml(f)


class GrobidConverter:

    def convert(self, filename, outfile):
        
        f = open(filename,'rb')

        response = requests.post(GROBID_URL, files={'input':f})


        print("Uploading %s..." % filename)

        f.close()

        print("Saving XML from %s..." % filename)

        self.indoc = minidom.parseString(response.text)

        print("Writing result to %s" % outfile)
        # write resulting xml file
        with codecs.open(outfile, 'w', encoding='utf-8') as f:
            self.indoc.writexml(f)