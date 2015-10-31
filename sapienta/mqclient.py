import pika
import uuid
import logging
import threading
import json
import uuid
import base64

logger = logging.getLogger(__name__)

"""SAPIENTA web interface MQ client"""

class MQClient(threading.Thread):

    def __init__(self, socketio, app):
        self.app = app
        self.socketio = socketio
        super(MQClient, self).__init__()


    def run(self):
        self.connection = self.connect()
        self.connection.ioloop.start()

    def submit(self, job):
            pass

    def _on_connection(self, conn):
        logger.info("Connected to MQ host")
        self.connection.channel(self._on_channel)

    def _on_channel(self, channel):
        logger.info("channel established")
        self._channel = channel
        logger.info("Establishing listener queue on channel")
        self._channel.queue_declare(self._on_queue, exclusive=True)

    def _on_queue(self, q):
        self.QUEUE = q.method.queue
        self.start_consuming()

    def start_consuming(self):
        logger.info('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                         self.QUEUE)


    def acknowledge_message(self, delivery_tag):
        """Acknowledge the message delivery from RabbitMQ by sending a
        Basic.Ack RPC method for the delivery tag.

        :param int delivery_tag: The delivery tag from the Basic.Deliver frame

        """
        logger.info('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.

        """
        logger.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        logger.warning('Channel %i was closed: (%s) %s',
                       channel, reply_code, reply_text)
        self._connection.close()

    def add_on_cancel_callback(self):
        logger.info('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        logger.info('Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()

    def connect(self):

        return pika.SelectConnection(pika.ConnectionParameters(
                    host=self.app.config['SAPIENTA_MQ_HOST'],
                    connection_attempts=10,
                    retry_delay=5), self._on_connection)



    def add_on_connection_close_callback(self):
        logger.info('Adding connection close callback')
        self.connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):

        self._channel = None
        if self.stopping:
            self._connection.ioloop.stop()
        else:
            logger.warning('Connection closed, reopening in 5 seconds: (%s) %s',
                           reply_code, reply_text)
            self.connection.add_timeout(5, self.reconnect)

    def reconnect(self):

        # This is the old connection IOLoop instance, stop its ioloop
        self.connection.ioloop.stop()

        if not self.closing:

            # Create a new connection
            self.connection = self.connect()

            # There is now a new connection, needs a new ioloop to run
            self.connection.ioloop.start()

    def stop_consuming(self):

        if self._channel:
            logger.info('Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def on_cancelok(self, unused_frame):

        logger.info('RabbitMQ acknowledged the cancellation of the consumer')
        self.close_channel()

    def close_channel(self):

        logger.info('Closing the channel')
        self._channel.close()
        logger.info('Closing connection')
        self.close_connection()


    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        logger.info('Closing connection')
        self.connection.close()

    def stop(self):
        logger.info("Stopping MQClient")
        self.stopping = True
        self.stop_consuming()
        self.connection.ioloop.start()
        logger.info("Stopped MQ client")

    def submit_job(self, inpipe, filename, body, exit_after=None):
        
        jobid = str(uuid.uuid4())

        headers = { 'docname' : filename, "exit_after" : exit_after}

        props = pika.BasicProperties(headers=headers, 
                reply_to=self.QUEUE,
                correlation_id=jobid)

        self._channel.basic_publish(exchange=self.app.config['SAPIENTA_MQ_EXCHANGE'],
                routing_key=inpipe,
                properties=props,
                body = body)

        return jobid

    def on_message(self, unused_channel, basic_deliver, properties, body):

        logger.info('Received message # %s from %s',
                    basic_deliver.delivery_tag, properties.app_id)

        self.acknowledge_message(basic_deliver.delivery_tag)

        logger.info("Broadcasting event to room %s ", properties.correlation_id)

        self.socketio.emit("finished",{"jobid" : properties.correlation_id, 
            "headers" : properties.headers,
            "body" : base64.b64encode(body)})

