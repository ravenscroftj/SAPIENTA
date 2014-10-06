"""
Base MQTT client/service 
"""

import logging
import paho.mqtt.client as mqtt

from multiprocessing import Pool

from sapienta import app

config = app.config


class MQTTService:

    def __init__(self, name, config):
        self.logger = logging.getLogger(name)
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
            
            self.workers.apply_async(self.services[message.topic], 
                    (client, userdata, message))
        elif message.topic == self.config['SAPIENTA_SHUTDOWN_TOPIC']:
            self.shutdown()

    def on_connect(self, client, userdata, flags, rc):
        #subscribe to topics
        for subscription in self.services:
            client.subscribe(subscription)   
            self.logger.info("Subscribed to topic '{}'".format(subscription))

        #subscribe for shutdown topic
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
    service = MQTTService("SapientaService", config)
    service.start()
