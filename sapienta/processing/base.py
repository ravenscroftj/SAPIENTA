"""
Base MQTT client/service 
"""

import json
import logging
import paho.mqtt.client as mqtt

from multiprocessing import Pool

from sapienta import app

config = app.config

class BaseService(object):
    """This class provides a base MQTT service and an example
    """

    def __init__(self):
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.addHandler(MQTTLogHandler(logging.INFO, config))

    def __call__(self,*args, **kwargs):
        self.logger.info("Moo")
        self.run(*args,**kwargs)

    def run(self, config, message):
        raise Exception("Unimplemented. Please extend this class")

class HelloWorldService(BaseService):

    def run(self, config, msg):
        self.logger.info("message on topic {} says {}".format(msg.topic,msg.payload))

class MQTTLogHandler(logging.Handler):

    def __init__(self, level, config):
        super(MQTTLogHandler,self).__init__(level)
        self.config = config
        self.client = mqtt.Client()

        self.client.connect(self.config['SAPIENTA_MQTT_HOST'], 
                self.config['SAPIENTA_MQTT_PORT'], 60)

    def emit(self, record):

        topic = "{}/{}/{}".format(self.config['SAPIENTA_LOGGING_PREFIX'],
                record.levelname, record.name)

        payload = json.dumps(record.__dict__)

        self.client.publish(topic,payload)


def run_service(servicetype, config, message):
    service = servicetype()
    service.run(config,message)

class MQTTServiceBroker:

    def __init__(self, name, config):
        self.logger = logging.getLogger(name)
        self.logger.addHandler(MQTTLogHandler(logging.INFO, config))
        self.services = {}
        self.config = config
        self.workers = Pool()

    def start(self):

        #connect MQTT 
        self.client = mqtt.Client()
 
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect


        self.logger.info("Connecting to MQTT Broker on {}:{}".format(self.config['SAPIENTA_MQTT_HOST'], 
                self.config['SAPIENTA_MQTT_PORT']))

        self.client.connect(self.config['SAPIENTA_MQTT_HOST'], 
                self.config['SAPIENTA_MQTT_PORT'], 60)

        #start main loop
        self.client.loop_forever()

    def on_message(self, client,userdata,message):
        #handle the message or discard it
        if message.topic in self.services:
            self.logger.info("Handing incoming message on {} to handler".format(message.topic))

            self.workers.apply_async(run_service,
                    (self.services[message.topic],config,message))

        elif message.topic.startswith(self.config['SAPIENTA_LOGGING_PREFIX']):
            print message.payload
        elif message.topic == self.config['SAPIENTA_SHUTDOWN_TOPIC']:
            self.shutdown()

    def on_work_done(self, result):
        self.logger.info(result)

    def on_connect(self, client, userdata, flags, rc):
        #subscribe for logging
        client.subscribe(self.config['SAPIENTA_LOGGING_PREFIX'] + "#")
        
        #subscribe to topics
        for subscription in self.services:
            client.subscribe(subscription)   
            self.logger.info("Subscribed to topic '{}'".format(subscription))

        #subscribe for shutdown topic
        self.logger.info("Subscribed to topic {} for shutdown requests"
                .format(self.config['SAPIENTA_SHUTDOWN_TOPIC']))

        client.subscribe(self.config['SAPIENTA_SHUTDOWN_TOPIC'])

    def shutdown(self):
        self.logger.info("I've been asked to shut down...")
        self.client.disconnect()

        self.logger.info("Waiting for any remaining work...")
        self.workers.close()
        self.workers.join()
        self.logger.info("Shutting down...")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    service_broker = MQTTServiceBroker("SapientaService", config)
    service_broker.services['sapienta/service/hello'] = HelloWorldService
    service_broker.start()
