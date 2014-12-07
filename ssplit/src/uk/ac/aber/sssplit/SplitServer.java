package uk.ac.aber.sssplit;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.Properties;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import org.apache.log4j.BasicConfigurator;
import org.apache.log4j.Logger;

import com.rabbitmq.client.AMQP.BasicProperties;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.ConsumerCancelledException;
import com.rabbitmq.client.QueueingConsumer;
import com.rabbitmq.client.ShutdownSignalException;

public class SplitServer implements Runnable {

	public static final String PROPERTY_SHUTDOWN_TOPIC = "sssplit.topic.shutdown";
	public static final String PROPERTY_TOPIC_INCOMING = "sssplit.topic.incoming";
	public static final String PROPERTY_TOPIC_OUTGOING = "sssplit.topic.outgoing";
	public static final String PROPERTY_BROKER = "sssplit.broker";
	public static final String PROPERTY_CLIENTID = "sssplit.clientid";
	public static final String PROPERTY_EXCHANGE_NAME = "sssplit.exchange_name";

	Properties properties;
	private boolean terminated;
	private Logger logger;
	private ExecutorService dispatcher;

	private Connection connection;
	private Channel channel;

	public SplitServer(Properties properties) {
		this.properties = properties;
		logger = Logger.getLogger(SplitServer.class);
		dispatcher = Executors.newFixedThreadPool(5);

	}

	public void shutdown() throws IOException {
		channel.basicPublish(properties.getProperty(PROPERTY_EXCHANGE_NAME),
				properties.getProperty(PROPERTY_SHUTDOWN_TOPIC), null,
				"".getBytes());
	}

	public void run() {

		try {
			splitServerLoop();
		} catch (IOException e) {
			e.printStackTrace();
		} catch (ShutdownSignalException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (ConsumerCancelledException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

	}

	private void splitServerLoop() throws IOException, ShutdownSignalException,
			ConsumerCancelledException, InterruptedException {
		terminated = false;

		logger.info("Starting MQ Connection...");

		ConnectionFactory factory = new ConnectionFactory();
		factory.setHost(properties.getProperty(PROPERTY_BROKER));

		connection = factory.newConnection();

		channel = connection.createChannel();

		channel.exchangeDeclare(properties.getProperty(PROPERTY_EXCHANGE_NAME),
				"topic");

		// set up queue and bind to exchange
		String queue = channel.queueDeclare(
				properties.getProperty(PROPERTY_TOPIC_INCOMING), true, false,
				false, null).getQueue();

		// subscribe to incoming and shutdown topics
		channel.queueBind(queue,
				properties.getProperty(PROPERTY_EXCHANGE_NAME),
				properties.getProperty(PROPERTY_TOPIC_INCOMING));

		channel.queueBind(queue,
				properties.getProperty(PROPERTY_EXCHANGE_NAME),
				properties.getProperty(PROPERTY_SHUTDOWN_TOPIC));

		logger.info("Subscribing to incoming workloads on "
				+ properties.getProperty(PROPERTY_TOPIC_INCOMING));

		logger.info("Subscribed and ready to go.");

		QueueingConsumer consumer = new QueueingConsumer(channel);

		// set up consumer with auto ACK off
		channel.basicConsume(queue, false, consumer);

		String shutdown_topic = properties.getProperty(PROPERTY_SHUTDOWN_TOPIC);

		// do the loop
		while (!terminated) {
			QueueingConsumer.Delivery delivery = consumer.nextDelivery();

			if (delivery.getEnvelope().getRoutingKey().equals(shutdown_topic)) {
				terminated = true;
			} else {
				String docname = delivery.getProperties().getHeaders()
						.get("docname").toString();
				logger.info("Received workload '" + docname
						+ "' dispatching to workers...");
				dispatcher.submit(new SplitTask(this, delivery));
			}

			channel.basicAck(delivery.getEnvelope().getDeliveryTag(), true);
		}

		logger.info("Unsubscribing from new incoming work...");

		logger.info("Waiting up to 30 seconds for existing jobs to finish...");
		try {
			dispatcher.shutdown();
			dispatcher.awaitTermination(30, TimeUnit.SECONDS);
		} catch (InterruptedException e) {
			logger.warn("Could not wait for work to finish... shutting down");
		}

		logger.info("Closing MQ Connection...");

		channel.close();
		connection.close();

		logger.info("Night night...");

	}

	public static void main(String[] args) {

		// Set up a simple configuration that logs on the console.
		BasicConfigurator.configure();

		Properties config = new Properties();
		try {
			config.load(new FileReader(new File("sssplit.properties")));

		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		SplitServer server = new SplitServer(config);
		Thread serverThread = new Thread(server);
		serverThread.start();

	}

	public synchronized void sendResult(byte[] message, BasicProperties msgProps)
			throws IOException {

		if (channel != null && channel.isOpen()) {

			Object exitAfter = msgProps.getHeaders().get("exit_after");

			if (properties.getProperty(PROPERTY_TOPIC_OUTGOING) == null
					|| (exitAfter != null && exitAfter.toString().equals(
							properties.getProperty(PROPERTY_TOPIC_INCOMING)))) {

				// return to sender
				channel.basicPublish("", msgProps.getReplyTo(), msgProps,
						message);
			} else {

				// return to sender
				channel.basicPublish(
						properties.getProperty(PROPERTY_EXCHANGE_NAME),
						properties.getProperty(PROPERTY_TOPIC_OUTGOING),
						msgProps, message);
			}

		} else {
			logger.warn("Cannot send message, client is not connected");
		}

	}

}
