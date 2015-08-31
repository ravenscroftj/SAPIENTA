import sys
import os
import logging
import uuid
import base64
import json
import pika

from optparse import OptionParser

from sapienta import app

config = app.config

class MQCLIClient:
    """MQ CLI handler"""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(type(self).__name__)
        self.jobs = {}

    def connect(self):

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host=self.config['SAPIENTA_MQ_HOST']))

        self.channel = self.connection.channel()

        self.logger.info("Connecting to MQ server on %s", self.config['SAPIENTA_MQ_HOST'] )

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)


    def queue_job(self, inpipe, file, exit_after=None):
        
        jobid = str(uuid.uuid4())

        headers = { 'docname' : os.path.basename(file), "exit_after" : exit_after}

        props = pika.BasicProperties(headers=headers, 
                reply_to=self.callback_queue,
                correlation_id=jobid)

        with open(file,'rb') as f:
            body = f.read()

        self.jobs[jobid] = file

        self.channel.basic_publish(exchange=self.config['SAPIENTA_MQ_EXCHANGE'],
                routing_key=inpipe,
                properties=props,
                body = body)


    def on_response(self, ch, method, properties, body):

        if properties.correlation_id in self.jobs:
            self.on_job_complete(properties,body)

    
    def wait_for_jobs(self):

        while len(self.jobs) > 0:
            self.connection.process_data_events()

        self.logger.info("All CLI work done, shutting down...")
        self.connection.close()


    def on_job_complete(self, properties, body):
        headers = properties.headers
        self.logger.info("Work is complete for " + headers['docname'])
        
        name,ext = os.path.splitext(self.jobs[properties.correlation_id])

        outname = name + "_done.xml"

        self.logger.info("Saving to %s", outname)

        with open(outname,'wb') as f:
            f.write(body)

        self.logger.info("Marking job %s as done", properties.correlation_id)
        del self.jobs[properties.correlation_id]

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
 

    #connect the client to the broker
    client = MQCLIClient(config)
    client.connect()

    for infile in args:
        name,ext = os.path.splitext(infile)

        if not(os.path.exists(infile)):
            print "Input file %s does not exist" % infile
            continue

        outfile = name + ".xml"

        #annotation requires splitting
        if(options.annotate):
            options.split = True

        
        inqueue = "sapienta.service.pdfx"
        exit_after = inqueue
                
        if(ext == ".pdf"):

            logging.info("Converting %s", infile)
            
        elif( ext == ".xml"):
            logging.info("No conversion needed on %s" , infile)
            inqueue    = "sapienta.service.splitq"
        else:
            logging.info("Unrecognised format for file %s", infile)
            sys.exit(0)

        if(options.split):
            logging.info("Splitting sentences in %s", infile)
            exit_after = "sapienta.service.splitq"
            
        if(options.annotate):
            #build annotated filename
            logging.info("Annotating file and saving to %s", outfile)
            exit_after = "sapienta.service.annotateq"

        #do the queue
        client.queue_job(inqueue, infile, exit_after)

    #wait for jobs to complete
    client.wait_for_jobs()


    
if __name__ == "__main__":
    main()
