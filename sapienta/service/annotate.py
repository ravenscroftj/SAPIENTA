"""MQ-based annotate processing system
"""

import logging
import tempfile
import os
import traceback

from sapienta import app

from sapienta.service.mq import BaseMQService
from sapienta.tools.annotate import Annotator


class AnnotateMQService(BaseMQService):

    def run(self, properties, body):

        headers = properties.headers
        self.logger.info("Handling paper annotation on {docname}".format(**headers))
        
        #store file data payload
        fd, fname = tempfile.mkstemp()
        od, outname = tempfile.mkstemp()

        self.logger.debug("Dumping XML data to {}".format(outname))

        with open(fname,'wb') as f:
            f.write(body)

        self.logger.debug("Running annotator on {docname}".format(**headers))
        anno = Annotator()
        try:
            anno.annotate(fname,outname)
        except Exception as e:
            self.logger.error(e)
            raise e

        self.logger.info("Annotation of {}  XML complete.".format(
            headers['docname']
            ))

        with open(outname, 'rb') as f:
            payload = f.read()

        outsock = os.fdopen(fd,'w')
        outsock.close()
        outsock = os.fdopen(od,'w')
        outsock.close()

        self.logger.info("Removing temporary file %s", fname)
        os.remove(fname)
        self.logger.info("Removing temporary file %s", outname)
        os.remove(outname)

        return properties, payload

    config = app.config

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    a = AnnotateMQService(app.config, "sapienta.service.annotateq")
    a.connect()
