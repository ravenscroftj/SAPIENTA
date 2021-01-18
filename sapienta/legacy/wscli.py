"""Websockets CLI client for sapienta """
import progressbar
import argparse
import logging
import os
import sys

from base64 import b64encode,b64decode

from socketIO_client import SocketIO, LoggingNamespace, BaseNamespace

ongoing = {}

def on_jobid_response(response):

    print "Received jobid %(jobid)s for file %(filename)s " % response
    ongoing[response['jobid']] = response['filename']


def on_finished_response(response):

    global ongoing

    print "Job %s is finished " % response['jobid']

    filename = ongoing[response['jobid']]


    headers = response['headers']
    body = response['body']
    name,ext = os.path.splitext(filename)


    print "Saving to %s" % (name+"_annotated.xml")

    with open(name+"_annotated.xml", "wb") as f:
        f.write(b64decode(body))

    print "All done"

    del ongoing[response['jobid']]

    if len(ongoing) < 1:
        print "All jobs have returned. Exiting"
        sys.exit()

def main():
    
    parser = argparse.ArgumentParser(description="Process some papers using SAPIENTA")

    parser.add_argument("--host", action="store", dest="host", 
            default="localhost",help="Host for websocket to connect to")

    parser.add_argument("-p","--port", action="store", dest="port",
            default="5000", type=int, help="Port for socketio connection")

    parser.add_argument("-s", "--split-sent", action="store_true", dest="split",
        help="If true, split sentences using NLTK sentence splitter")

    parser.add_argument("-a", "--annotate", action="store_true", dest="annotate",
        help="If true, annotate the sentence-split XML with CoreSC labels")

    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
        help="If set, provides more verbose output")

    parser.add_argument("papers", nargs="+")
 
    options = parser.parse_args()

    if(options.verbose):
        logging.basicConfig(level=logging.DEBUG)
        logging.debug("Verbose mode on.")
    else:
        logging.basicConfig(level=logging.INFO)


    logging.info("Connectiong to socket.io server at %s:%d", options.host, options.port)

    #connect websocket
    with SocketIO(options.host, options.port, LoggingNamespace) as socketIO:

        for paper in options.papers:
            logging.info("Submitting paper %s", paper)

            with open(paper,'rb') as f:
                data = f.read()

            message =  {"filename" : paper, 'body' : b64encode(data) }
            
            message['split'] = options.split
            message['annotate'] = options.annotate


            socketIO.on('jobid', on_jobid_response)
            socketIO.on('finished', on_finished_response)
            socketIO.emit("work",message)

        socketIO.wait()


if __name__ == "__main__":
    main()
