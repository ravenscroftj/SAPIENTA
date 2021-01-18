"""
Base MQTT client/service 
"""

import json
import uuid
import importlib
import logging

from multiprocessing import Pool, Process, Queue

from sapienta import app

config = app.config

class ServiceCoordinator:
    """Service coordinator loads sapienta mq services and starts/stops them"""

    def __init__(self, *args,**kwargs):
        self.config = config
        self.services = {}
        self.logger = logging.getLogger(type(self).__name__)

    def start(self):
        #if any services are configured, start them now
        if 'SAPIENTA_SERVICES' in self.config:

            for servicedef in self.config['SAPIENTA_SERVICES']:

                self.logger.info("Starting service '%(name)s' " +
                        "%(input_topic)s->%(output_topic)s",servicedef)

                mod = importlib.import_module(servicedef['module'])
                service = mod.__dict__[servicedef['class']](config=self.config, 
                        input_topic=servicedef['input_topic'], 
                        output_topic=servicedef['output_topic'])

                serviceid = uuid.uuid4()
                self.services[str(serviceid)] = service
                p = Process(target=service.connect)
                p.start()

    def shutdown(self):
        for key in self.services:
            self.services[key].close()

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    svc = ServiceCoordinator(config=config)

    try:
        svc.start()
    except KeyboardInterrupt:
        svc.shutdown()
