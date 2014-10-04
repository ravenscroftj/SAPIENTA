package uk.ac.aber.sssplit;

import java.io.ByteArrayInputStream;
import java.io.InputStreamReader;
import java.io.StringReader;
import java.util.HashMap;

import org.apache.log4j.Logger;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.json.simple.JSONObject;
import org.json.simple.JSONValue;

public class SplitTask implements Runnable{
	
	private SplitServer requester;
	private MqttMessage message;
	private Logger logger = Logger.getLogger(SplitTask.class);
	
	public SplitTask(SplitServer requester, MqttMessage message) {
		this.requester = requester;
		this.message = message;
	}

	@Override
	public void run() {
		
		ByteArrayInputStream bin = new ByteArrayInputStream(message.getPayload());
		
		JSONObject value = (JSONObject)JSONValue.parse(new InputStreamReader(bin));
		
		if(value.containsKey("filedata")) {
			
			//we're dealing with encoded data
			try {
				String result = XMLSentSplit.processXML(new StringReader((String)value.get("filedata")), 
						(String)value.get("docname"));
				
				HashMap<String, String> responseMap = new HashMap<>();
				responseMap.put("filedata", result);
				responseMap.put("docname", (String)value.get("docname"));
				
				JSONObject obj = new JSONObject(responseMap);
				
				MqttMessage responseMessage = new MqttMessage(obj.toJSONString().getBytes());
				requester.sendResult(responseMessage);
				
			} catch (Exception e) {
				logger.error("SSSPlit task error", e);
			}
			
		}
		
	}

}
