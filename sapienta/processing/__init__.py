from sapienta.processing.server import Coordinator
from sapienta.processing.worker import WorkerClient
from multiprocessing import Process

import threading
import logging

def main():
    """Run a coordinator server and some workers"""

    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Verbose mode on.")
    
    pevt = threading.Event()
    c = Coordinator()
    w = WorkerClient(pevt)

    c_process = Process(target=lambda: c.run())
    w_process = Process(target=lambda: w.run())

    c_process.start()
    w_process.start()


    raw_input("Running... press any key to quit...")
    pevt.set()

if __name__ == "__main__":
    main()
