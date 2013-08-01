<?php

/**
* RESTFul API for paper processing with SAPIENTA
*
*/
require("config.php");
require("sapienta.php");


/**
* Return status of job
*
*/
function sapienta_api_jobstatus(){
	$id = (int)$_GET['id'];

	$sc = new SAPIENTAClient();
	$job =$sc->get_job_status($id);

	print json_encode($job);
}

function sapienta_api_serverstats(){
	$sc = new SAPIENTAClient();
	$stats = $sc->get_service_status();
	
	print json_encode($stats);
}

/**
* Download the actual XML 
*
*/
function sapienta_api_download(){
	$id = (int)$_GET['id'];

	//initiate XML-RPC communication
	$sc = new SAPIENTAClient();
	$job =$sc->get_job_status($id);
	$content = $sc->get_job_content($id);

	header('Content-Type: application/octet-stream');
	header("Content-Transfer-Encoding: Binary");
	header("Content-disposition: attachment; filename=\"".basename($job['filename'])."\"");

	print $content;
	exit();
}

function sapienta_api_submit(){

	if(isset($_FILES['the_file'])){
		$name = $_FILES['the_file']['name'];
		$ext = substr($name,-4,4);

		if( $ext == ".pdf" || $ext == ".xml"){
			
			$rand = uniqid();
			$filename = UPLOAD_DIR."/$rand.$ext";

			if(@move_uploaded_file($_FILES['the_file']['tmp_name'], $filename)){
				
				
				$sc = new SAPIENTAClient();
				$job_id = $sc->submit_job($filename);

				print json_encode(array("job_id" => $job_id));
				

			}else{ //couldn't move the file so there was a problem with the upload process
				$message="There was a problem with the file upload.";
				print json_encode(array("error" => $message));
			}

		}else{ //if the extension doesn't match pdf or xml
			$message = "The filetype that you have uploaded is unsupported. Only PDF and XML files may be uploaded";
			print json_encode(array("error" => $message));
		}
		
	}
}


if(!isset($_GET['action'])){
	$_GET['action'] = 'index';
}

switch($_GET['action']){
	
	case 'submit':
		sapienta_api_submit();
	break;

	case 'status':
		sapienta_api_serverstats();
	break;

	case 'get':
		sapienta_api_download();
	break;

	case 'job':
		sapienta_api_jobstatus();
	break;

	case 'index': default:
		print "Invalid operation.";
	break;
}

?>
