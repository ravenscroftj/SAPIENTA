"""Websockets CLI client for sapienta """
import progressbar
import argparse
import logging

from base64 import b64encode

from socketIO_client import SocketIO, LoggingNamespace, BaseNamespace

class SapientaNamespace(BaseNamespace):

    def on_work_response(self, *args):
        print "Response"


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

            socketIO.emit("work", {"filename" : paper, 'data' : b64encode(data) })

        socketIO.wait(seconds=1)


if __name__ == "__main__":
    main()
