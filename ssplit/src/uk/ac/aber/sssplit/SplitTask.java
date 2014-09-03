package uk.ac.aber.sssplit;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.StringBufferInputStream;

import org.apache.log4j.Logger;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.json.simple.JSONObject;
import org.json.simple.JSONValue;

import sun.misc.BASE64Decoder;

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
		
		File processFile = null;
		
		if(value.containsKey("filename")) {
			//we're dealing with a local file
			processFile = new File((String)value.get("filename"));
		}else if(value.containsKey("filedata")) {
			//we're dealing with encoded data
			try {
				processFile = stashFile((String)value.get("filedata"));
			} catch (IOException e) {
				logger.error("SSSPlit task error", e);
			}
			
		}
		

		XMLSentSplit.processFile(processFile.getName(), processFile.getParent());
		
		
	}
	
	
	private File stashFile(String data) throws IOException {
		
		BASE64Decoder b64 = new BASE64Decoder();
		File processFile = File.createTempFile("sssplit", ".tmp");
		FileOutputStream fout = new FileOutputStream(processFile);
		ByteArrayInputStream bin = new ByteArrayInputStream(data.getBytes());
		b64.decodeBuffer(bin, fout);
		fout.close();
		
		return processFile;
	}
	


}
