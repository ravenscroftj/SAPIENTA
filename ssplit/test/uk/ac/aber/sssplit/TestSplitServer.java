package uk.ac.aber.sssplit;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.StringReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Properties;

import org.apache.log4j.BasicConfigurator;
import org.custommonkey.xmlunit.Diff;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.MqttPersistenceException;
import org.json.simple.JSONObject;
import org.json.simple.JSONValue;
import org.junit.AfterClass;
import org.junit.Assert;
import org.junit.BeforeClass;
import org.junit.Test;
import org.xml.sax.SAXException;

/**
 * Simple test that will check the MQTT interface for SSSPlit works properly
 * 
 * @author James Ravenscroft
 *
 */
public class TestSplitServer implements MqttCallback {

	private static Properties config = null;

	private static SplitServer server = null;

	private static Thread serverThread = null;

	private static MqttClient client;

	private static List<MqttMessage> receivedMessages = new ArrayList<>();

	@BeforeClass
	public static void setupServer() throws MqttException, InterruptedException {
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
		client = new MqttClient(
				config.getProperty(SplitServer.PROPERTY_BROKER),
				MqttClient.generateClientId());
		client.connect();

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

		// subscribe to replies topic perhaps unintuitive naming but this is the
		// outgoing topic for the /server/ i.e. where it sends replies
		client.subscribe(config
				.getProperty(SplitServer.PROPERTY_TOPIC_OUTGOING));
		client.setCallback(this);

		//set up the job request and send to broker/splitserver
		HashMap<String, String> messageContent = new HashMap<>();

		FileReader fr = new FileReader(noSentFile);

		StringBuffer sb = new StringBuffer();
		char[] buffer = new char[2048];

		for (int i = fr.read(buffer); i >= 0; i = fr.read(buffer)) {
			sb.append(buffer, 0, i);
		}

		String name = noSentFile.getName();
		name = name.substring(0, name.lastIndexOf("."));
		
		messageContent.put("filedata", sb.toString());
		messageContent.put("docname", name);

		JSONObject json = new JSONObject(messageContent);
		MqttMessage message = new MqttMessage(json.toJSONString().getBytes());

		client.publish(config.getProperty(SplitServer.PROPERTY_TOPIC_INCOMING),
				message);

		// wait for a response (give it 30 seconds to be safe)
		System.out.println("Waiting 10s for processing");
		Thread.sleep(10000);

		//make sure we received a message and run an XML comparison on it
		Assert.assertEquals(1, receivedMessages.size());
		MqttMessage msg = receivedMessages.remove(0);

		ByteArrayInputStream bin = new ByteArrayInputStream(msg.getPayload());
		JSONObject value = (JSONObject)JSONValue.parse(new InputStreamReader(bin));
		
		FileWriter fw = new FileWriter(outFile);
		fw.write((String)value.get("filedata"));
		fw.close();
		
		
		FileReader    refInput  = new FileReader(refFile);
		FileReader    testInput = new FileReader(outFile);
		
        Diff diff = new Diff(refInput, testInput);
        System.out.println("Similar? " + diff.similar());
        Assert.assertTrue("The XML is not identical", diff.identical());
        System.out.println("Identical? " + diff.identical());


	}

	@AfterClass
	public static void shutdownServer() throws MqttPersistenceException,
			MqttException, InterruptedException {
		server.shutdown();
		serverThread.join();
		client.disconnect();
		client.close();
	}

	@Override
	public void connectionLost(Throwable cause) {
		// TODO Auto-generated method stub

	}

	@Override
	public void messageArrived(String topic, MqttMessage message)
			throws Exception {

		if (topic.equals(config
				.getProperty(SplitServer.PROPERTY_TOPIC_OUTGOING))) {
			receivedMessages.add(message);
		}

	}

	@Override
	public void deliveryComplete(IMqttDeliveryToken token) {
		// TODO Auto-generated method stub

	}

}
