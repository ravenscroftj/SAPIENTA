package uk.ac.aber.sssplit;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.Properties;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import org.apache.log4j.BasicConfigurator;
import org.apache.log4j.Logger;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.MqttPersistenceException;

public class SplitServer implements Runnable,MqttCallback{
	
	public static String PROPERTY_SHUTDOWN_TOPIC  = "sssplit.topic.shutdown";
	public static String PROPERTY_TOPIC_INCOMING  = "sssplit.topic.incoming";
	public static String PROPERTY_TOPIC_OUTGOING  = "sssplit.topic.outgoing";
	public static String PROPERTY_BROKER = "sssplit.broker"; 
	public static String PROPERTY_CLIENTID = "sssplit.clientid";
	
	Properties properties;
	private boolean terminated;
	private Logger logger;
	private ExecutorService dispatcher;
	private MqttClient client = null;
	
	public SplitServer(Properties properties) {
		this.properties = properties;
		logger = Logger.getLogger(SplitServer.class);
		dispatcher = Executors.newFixedThreadPool(5);
		
	}
	
	public void run(){

		try {
			splitServerLoop();
		} catch (MqttException e) {
			e.printStackTrace();
		}
		
	}
	
	private void splitServerLoop() throws MqttException{
		terminated = false;
		
		client = new MqttClient(properties.getProperty(PROPERTY_BROKER), 
				properties.getProperty(PROPERTY_CLIENTID));
		
		client.connect();
		
		//subscribe to incoming and shutdown topics
		client.subscribe(properties.getProperty(PROPERTY_TOPIC_INCOMING));
		client.subscribe(properties.getProperty(PROPERTY_SHUTDOWN_TOPIC));
		
		client.setCallback(this);
		while(!terminated) {
			//sleep 
			try {
				Thread.sleep(200);
			} catch (InterruptedException e) {
				logger.error("Sleep loop interrupted", e);
			}
		}
		
		logger.info("Closing MQTT Connection...");
		client.disconnect();
		client.close();
		
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

	@Override
	public void connectionLost(Throwable cause) {
		logger.error("Lost connection to MQTT broker", cause);
		terminated = true;
	}

	@Override
	public void messageArrived(String topic, MqttMessage message)
			throws Exception {
		
		if (topic.equals(properties.getProperty(PROPERTY_SHUTDOWN_TOPIC))) {
			terminated = true;
			logger.info("Shutdown request received, stopping server...");
		}else{
			//if its not a shutdown request, its a splitter request.
			dispatcher.submit(new SplitTask(this, message));
		}
		
	}

	@Override
	public void deliveryComplete(IMqttDeliveryToken token) {
		// TODO Auto-generated method stub
		
	}
	
	public synchronized void sendResult(MqttMessage message) throws MqttPersistenceException, MqttException {
		
		if( client != null && client.isConnected()){
			
			client.publish(properties.getProperty(PROPERTY_TOPIC_OUTGOING), message);
			
		}else{
			logger.warn("Cannot send message, client is not connected");
		}
		
	}
			

}
