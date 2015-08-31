"""
MQ-based microservice that splits incoming papers and returns split XML
"""

import logging
import os
import tempfile

from sapienta import app

from sapienta.tools.sssplit import SSSplit
from sapienta.service.mq import BaseMQService

class SentenceSplitterService(BaseMQService):

    def run(self, properties, body):

        headers = properties.headers
        self.logger.info("Handling Sentence Splitting on {docname}".format(**headers))
        
        #store file data payload
        fd, fname = tempfile.mkstemp()
        od, outname = tempfile.mkstemp()

        self.logger.debug("Setting output filename to {}".format(outname))

        with open(fname,'wb') as f:
            f.write(body)

        self.logger.debug("Running splitter on {docname}".format(**headers))
        sssplit = SSSplit()
        sssplit.split(fname, outname)

        self.logger.info("Splitting of {} complete.".format(
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
    pdf = SentenceSplitterService(config, "sapienta.service.splitq", "sapienta.service.annotateq")
    pdf.connect()
