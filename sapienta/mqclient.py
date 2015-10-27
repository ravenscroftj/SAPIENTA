import pika
import uuid
import logging

"""SAPIENTA web interface MQ client"""

class MQClient:

    def __init__(self, socketio, app):
        self.connection = pika.SelectConnection(pika.ConnectionParameters(
                    host=app.config['SAPIENTA_MQ_HOST'],
                    connection_attempts=10,
                    retry_delay=5), self._on_connection)

    def submit(self, job):
            pass

    def _on_connection(self, conn):
        logging.info("Connected to MQ host")
        self.connection.channel(self._on_channel)

    def _on_channel(self, channel):
        logging.info("channel established")
        self.channel = channel
        logging.info("Establishing listener queue on channel")
        self.channel.queue_declare(self._on_queue, exclusive=True)

    def _on_queue(self, q):
        self.callback_q = q
        

    def connect(self):
        self.connection.ioloop.start()

    def disconnect(self):
        self.connection.close()
        self.connection.ioloop.start()

