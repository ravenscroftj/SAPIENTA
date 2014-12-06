package uk.ac.aber.sssplit;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

import org.apache.log4j.BasicConfigurator;
import org.custommonkey.xmlunit.Diff;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttPersistenceException;
import org.junit.AfterClass;
import org.junit.Assert;
import org.junit.BeforeClass;
import org.junit.Test;
import org.xml.sax.SAXException;

import com.rabbitmq.client.AMQP.BasicProperties;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.QueueingConsumer;

/**
 * Simple test that will check the MQTT interface for SSSPlit works properly
 * 
 * @author James Ravenscroft
 *
 */
public class TestSplitServer {

	private static Properties config = null;

	private static SplitServer server = null;

	private static Thread serverThread = null;

	private static Connection connection;
	private static Channel channel;

	@BeforeClass
	public static void setupServer() throws InterruptedException, IOException {
		// start a split server
		// Set up a simple configuration that logs on the console.
		BasicConfigurator.configure();

		config = new Properties();
		try {
			config.load(new FileReader(new File("sssplit.properties")));

		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		// set up MQTT client
		ConnectionFactory factory = new ConnectionFactory();
		factory.setHost(config.getProperty(SplitServer.PROPERTY_BROKER));
		
		connection = factory.newConnection();
		
		channel = connection.createChannel();
		
		// create split server and start it running
		server = new SplitServer(config);
		serverThread = new Thread(server);
		serverThread.start();

		// wait 1 second for connections to come up
		Thread.sleep(1000);
	}

	@Test
	public void testSplitServer() throws InterruptedException, IOException,
			MqttPersistenceException, MqttException, SAXException {
		
		// set up input filenames
		File noSentFile = new File("b103844n_nosents.xml");
		File outFile = new File("b103844n_nosents_mode2.xml");
		File refFile = new File("b103844n_mode2_reference.xml");
		
		//set up unique id for this task
		String corrId = java.util.UUID.randomUUID().toString();

		// subscribe to replies topic perhaps unintuitive naming but this is the
		// outgoing topic for the /server/ i.e. where it sends replies
		channel.exchangeDeclare(SplitServer.PROPERTY_EXCHANGE_NAME, "topic");
		String returnQueue = channel.queueDeclare().getQueue();
		
		QueueingConsumer consumer = new QueueingConsumer(channel);
		channel.basicConsume(returnQueue, true, consumer);

		//read xml file into string buffer to be sent to server
		FileReader fr = new FileReader(noSentFile);

		StringBuffer sb = new StringBuffer();
		char[] buffer = new char[2048];

		for (int i = fr.read(buffer); i >= 0; i = fr.read(buffer)) {
			sb.append(buffer, 0, i);
		}
		
		fr.close();
		
		
		String name = noSentFile.getName();
		name = name.substring(0, name.lastIndexOf("."));
		
		Map<String,Object> headers = new HashMap<>();
		headers.put("docname", name);

		BasicProperties props = new BasicProperties().builder()
				.replyTo(returnQueue)
				.correlationId(corrId)
				.headers(headers)
				.build();
		
		channel.basicPublish(config.getProperty(SplitServer.PROPERTY_EXCHANGE_NAME), 
				config.getProperty(SplitServer.PROPERTY_TOPIC_INCOMING), props, sb.toString().getBytes());
		
		byte[] response = null;
		
		//blocking call waits for the next incoming delivery to the consumer
		while(true) {
	        QueueingConsumer.Delivery delivery = consumer.nextDelivery();
	        
	        if (corrId.equals(delivery.getProperties().getCorrelationId())) {
	            response = delivery.getBody();
	            break;
	        }
		}
		
		//make sure a response was received
		Assert.assertNotNull(response);

		FileWriter fw = new FileWriter(outFile);
		fw.write(new String(response));
		fw.close();
		
		
		FileReader    refInput  = new FileReader(refFile);
		FileReader    testInput = new FileReader(outFile);
		
        Diff diff = new Diff(refInput, testInput);
        System.out.println("Similar? " + diff.similar());
        Assert.assertTrue("The XML is not identical", diff.identical());
        System.out.println("Identical? " + diff.identical());


	}

	@AfterClass
	public static void shutdownServer() throws  IOException, InterruptedException {
		server.shutdown();
		serverThread.join();
		channel.close();
		connection.close();
	}

}
