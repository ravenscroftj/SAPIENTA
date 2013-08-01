<?php

/**
* A collection of functions for dealing with API and web frontend actions
*
*/

require("xmlrpc-2.2.2/lib/xmlrpc.inc");

class SAPIENTAClient{

	function __construct(){
		$this->xmlrpc = new xmlrpc_client("http://".RPC_HOST.":".RPC_PORT."/");
	}

	/**
	 * Return an array of job status information for given job ID
	 *
	 * @param int $job_id the numerical ID from the job, allocated at submission
	 * @return string[] job status structure
	 */
	function get_job_status($job_id){
		//initiate XML-RPC communication
		$r = $this->xmlrpc->send(new xmlrpcmsg('get_status', array(new xmlrpcval($job_id,'int'))));
		$job = php_xmlrpc_decode($r->value());
		return $job;
	}

	/**
	 * Return the service status of the annotation server
	 *
	 * @return string[] array containing details of service status
	 */
	function get_service_status(){
		$r = $this->xmlrpc->send(new xmlrpcmsg("get_stats", array()));
		$stats = php_xmlrpc_decode($r->value());
		return $stats;
	}

	/**
	 * Return the annotated XML from the job
	 *
	 * @param int $job_id the numerical ID from the job, allocated at submission
	 * @return string XML string containing all content from the annotated file
	 */
	function get_job_content($job_id){

		$r = $this->xmlrpc->send(new xmlrpcmsg('get_result', array(new xmlrpcval($job_id,'int'))));
		$content = php_xmlrpc_decode($r->value());

		return gzuncompress($content);
	}

	/**
	 * Submit a PDF or XML file for annotation
	 *
	 * @param $filename the name of the file to send for annotation
	 * @return int The job ID used for tracking and retrieving the result from the job
	 */
	function submit_job($filename){
		//read and encode uploaded form data
		$fp = fopen($filename, 'rb');
		$data = fread($fp, filesize($filename));
		fclose($fp);
		
		$filexml = new xmlrpcval($filename, 'string');
		$content = new xmlrpcval(gzcompress($data), 'base64');

		$r = $this->xmlrpc->send(new xmlrpcmsg("queue_job", array($filexml, $content)));

		//post XML-RPC data and get job ID
		return php_xmlrpc_decode($r->value());
	}
}

?>
