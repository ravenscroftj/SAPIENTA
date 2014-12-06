package uk.ac.aber.sssplit;

import java.io.StringReader;
import java.util.Map;

import org.apache.log4j.Logger;

import com.rabbitmq.client.QueueingConsumer.Delivery;

public class SplitTask implements Runnable{
	
	private SplitServer requester;
	private Delivery message;
	private Logger logger = Logger.getLogger(SplitTask.class);
	
	public SplitTask(SplitServer requester, Delivery message) {
		this.requester = requester;
		this.message = message;
	}

	@Override
	public void run() {
		
		logger.info("Starting worker thread");
		
		Map<String,Object> headers = message.getProperties().getHeaders();
		String docname = (String)headers.get("docname").toString();
		
		
		//we're dealing with encoded data
		try {
			String result = XMLSentSplit.processXML(new StringReader(new String(message.getBody())), 
					docname);
			
			logger.info(String.format("Completed splitting %s, sending back.", docname));
			requester.sendResult(result.getBytes(), message.getProperties());
			
		} catch (Exception e) {
			logger.error("SSSPlit task error", e);
		}
		
		
	}

}
