"""
RabbitMQ (AMQP) client work distribution system
"""

import pika
import logging
import traceback
#from __main__ import traceback


class BaseMQService:

    def __init__(self, config, input_topic, output_topic=None):
        self.config = config
        self.input_topic  = input_topic
        self.output_topic = output_topic 
        self.logger = logging.getLogger(type(self).__name__)

    def connect(self):
        """Connect the MQ client to the broker"""

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host=self.config['SAPIENTA_MQ_HOST'],
                    connection_attempts=10,
                    retry_delay=5))

        self.channel = self.connection.channel()

        self.logger.info("Connecting to MQ server on %s",
                self.config['SAPIENTA_MQ_HOST'] )

        # declare exchange
        self.channel.exchange_declare(
                exchange=self.config['SAPIENTA_MQ_EXCHANGE'],
                type='topic')

        self.logger.info("Subscribing to topic '%s'", self.input_topic)
        
        # subscribe to incoming topic
        result = self.channel.queue_declare(self.input_topic, durable=True)

        self.queue = result.method.queue

        self.channel.queue_bind(exchange=self.config['SAPIENTA_MQ_EXCHANGE'],
                       queue=self.queue,
                       routing_key=self.input_topic)

        self.channel.basic_consume(self.on_message, queue=self.queue)
        self.channel.start_consuming()



    def run(self, properties, body):
        """This should be overridden, throws error"""
        raise NotImplementedError("Please override this class")

    def close(self):
        self.connection.close()

    def on_message(self, ch, method, properties, body):
        """Handler function for mq service"""

        self.logger.info("Received message ")

        #do a thing
        try:
            properties, payload = self.run(properties, body)
        except Exception as exc:
            self.logger.error("Failed to process payload")
            tb = traceback.format_exc()
            self.logger.error(tb)
            
            properties.headers['error'] = True
            
            ch.basic_ack(delivery_tag = method.delivery_tag)
            
            #send the failure back to the user
            ch.basic_publish(exchange='',
                routing_key=properties.reply_to,
                properties = pika.BasicProperties(
                    headers = properties.headers,
                    correlation_id=properties.correlation_id),
                body = tb)
            
            return
        
        #do an ack
        ch.basic_ack(delivery_tag = method.delivery_tag)

        if "exit_after" in properties.headers:
            exit_after = properties.headers["exit_after"]
        else:
            exit_after = None

        if (self.output_topic == None) | (exit_after == self.input_topic):

            self.logger.info("Processing complete. Exiting the pipeline")

            #send completed operation back to client
            ch.basic_publish(exchange='',
                routing_key=properties.reply_to,
                properties = pika.BasicProperties(
                    headers = properties.headers,
                    correlation_id=properties.correlation_id),
                body = payload)
        else:
            
            self.logger.info("Passing the message along to %s ", self.output_topic)

            ch.basic_publish(exchange=self.config['SAPIENTA_MQ_EXCHANGE'],
                    routing_key=self.output_topic,
                   properties = pika.BasicProperties(
                    headers = properties.headers,
                    reply_to = properties.reply_to,
                    correlation_id=properties.correlation_id),
                body = payload)

