from sapienta.processing.server import Coordinator
from sapienta.processing.worker import WorkerClient, init_worker
from sapienta import app

from optparse import OptionParser
from multiprocessing import Process

import threading
import logging

config = app.config

def main():
    """Run a coordinator server and some workers"""

    usage = "usage: %prog [options]\n\nThe system will try to determine as many config values as possible from sapienta.cfg"

    parser = OptionParser(usage=usage)

    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
        help="If set, run the client in verbose mode")

    parser.add_option("--port", action="store", dest="port", default=config['COORD_PORT'],
            help="Port that the XMLRPCServer should listen on")

    parser.add_option("--host",  action="store", dest="host", default=config['COORD_ADDRESS'],
            help="Host name that the XMLRPCServer should listen on")

    parser.add_option("-w", "--workers", action="store", dest="processes",
        default=None, help="Number of worker threads to instantiate, defaults to number of cores on your CPU")


    (options, args) = parser.parse_args()

    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug("Verbose mode on.")
    else:
        logging.basicConfig(level=logging.INFO)

    addr = (options.host,options.port)
    
    pevt = threading.Event()
    c = Coordinator(addr=addr)
    c_process = Process(target=lambda: c.run())
    c_process.start()
    
    if (options.processes != None) and (int(options.processes) < 1):
        logging.warn("Workers set to zero, no workers will be started...")
    else:
        w = WorkerClient(pevt, coord_addr=addr, processes = options.processes)
        w_process = Process(target=lambda: w.run())
        w_process.start()

    try:
        while 1:
            raw_input()
    except KeyboardInterrupt:
        pevt.set()

    logging.info("Shutting down all worker threads...")
    pevt.set()

if __name__ == "__main__":
    main()
