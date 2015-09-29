import logging
import os
import tempfile

from sapienta import app

from sapienta.tools.converter import PDFXConverter
from sapienta.service.mq import BaseMQService

class PDFConverterService(BaseMQService):

    def run(self, properties, body):

        headers = properties.headers
        self.logger.info("Handling PDF conversion on {docname}".format(**headers))
        
        #store file data payload
        fd, fname = tempfile.mkstemp()
        od, outname = tempfile.mkstemp()

        self.logger.debug("Dumping PDF data to {}".format(outname))

        with open(fname,'wb') as f:
            f.write(body)

        self.logger.debug("Running PDF converter on {docname}".format(**headers))
        pdfx = PDFXConverter()
        pdfx.convert(fname, outname)

        self.logger.info("Conversion of {} from PDF to XML complete.".format(
            headers['docname']
            ))

        with open(outname, 'rb') as f:
            payload = f.read()

        self.logger.info("Removing temporary file %s", fname)
        os.remove(fname)
        self.logger.info("Removing temporary file %s", outname)
        os.remove(outname)

        return properties, payload

if __name__ == "__main__":

    config = app.config

    logging.basicConfig(level=logging.INFO)
    pdf = PDFConverterService(config, "sapienta.service.pdfx", "sapienta.service.splitq")
    pdf.connect()
