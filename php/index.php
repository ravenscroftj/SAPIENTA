<?php

//require("XmlRPC.php");

require("xmlrpc-2.2.2/lib/xmlrpc.inc");

/**
* PHP web frontend for SAPIENTA (if you don't have WSGI on your web server)
*
*/
define('RPC_HOST',"127.0.0.1");
define('RPC_PORT',1234);
define('UPLOAD_DIR', "tmp");


/**
* View used to display the status page for a running job
*
*/
function jobstatus_view(){

	include("templates/header.php");

	$id = (int)$_GET['jobid'];

	//initiate XML-RPC communication
	$xmlrpc = new xmlrpc_client("http://".RPC_HOST.":".RPC_PORT."/");

	$r = $xmlrpc->send(new xmlrpcmsg('get_status', array(new xmlrpcval($id,'int'))));
	$job = php_xmlrpc_decode($r->value());
	
	if( $job['status'] == "WORKING" || $job['status'] == "PENDING") {
	?>
		<p>The job <?php echo $job['filename'];?> (JOBID <?php echo $job['jobid']; ?>) is currently being annotated. Please wait... </p>

		<img src="loader.gif" alt="Working..."/>


		<p>This page will refresh in 10 seconds...</p>
		<script type="text/JavaScript">
		<!--
			setTimeout("location.reload(true);", 10000);
		//   -->
		</script>
	<?php
	}else{
	?>
		<p>Job <?php echo $job['jobid']; ?> has been completed and is now ready to be downloaded</p>

		<a href="?action=get&amp;id=<?php echo $id; ?>" class="btn btn-primary btn-large">
			<i class="icon-arrow-down icon-white"></i> Download Paper
		</a>
	<?php
	}
	
	include("templates/footer.php");

}

/**
* View used to download the paper content itself
*
*/
function get_view(){

	$id = (int)$_GET['id'];

	//initiate XML-RPC communication
	$xmlrpc = new xmlrpc_client("http://".RPC_HOST.":".RPC_PORT."/");

	$r = $xmlrpc->send(new xmlrpcmsg('get_status', array(new xmlrpcval($id,'int'))));
	$job = php_xmlrpc_decode($r->value());

	$r = $xmlrpc->send(new xmlrpcmsg('get_result', array(new xmlrpcval($id,'int'))));
	$content = php_xmlrpc_decode($r->value());

	header('Content-Type: application/octet-stream');
	header("Content-Transfer-Encoding: Binary");
	header("Content-disposition: attachment; filename=\"".basename($job['filename'])."\"");

	print gzuncompress($content);
	exit();
}

/**
* Return the current status of the server
*
*/
function status_view(){

	include("templates/header.php");

	//$xmlrpc = new XmlRPC(RPC_HOST, RPC_PORT);

	$xmlrpc = new xmlrpc_client("http://".RPC_HOST.":".RPC_PORT."/");

	$r = $xmlrpc->send(new xmlrpcmsg("get_stats", array()));

	$stats = php_xmlrpc_decode($r->value());

	?>
	<h1>SAPIENTA Service Status</h1>

	<p>Sapienta is currently running with <?php echo $stats['workers']; ?> workers consisting of <?php echo $stats['slots']; ?> parallel processing threads in total.</p>

	<p>There are currently <?php echo $stats['pending']; ?> papers pending annotation and <?php echo $stats['working'];?> papers being processed</p>
	
	<?php


	include("templates/footer.php");

}

/**
* View used to display the upload form or actually submit the paper
*
*/
function upload_view(){

	include("templates/header.php");

	if(isset($_FILES['the_file'])){
		$name = $_FILES['the_file']['name'];
		$ext = substr($name,-4,4);

		if( $ext == ".pdf" || $ext == ".xml"){
			
			$rand = uniqid();
			$filename = UPLOAD_DIR."/$rand.$ext";

			if(@move_uploaded_file($_FILES['the_file']['tmp_name'], $filename)){
				
				
				//initiate XML-RPC communication
				$xmlrpc = new xmlrpc_client("http://".RPC_HOST.":".RPC_PORT."/");
				
				//read and encode uploaded form data
				$fp = fopen($filename, 'rb');
				$data = fread($fp, filesize($filename));
				fclose($fp);
				
				$filexml = new xmlrpcval($filename, 'string');
				$content = new xmlrpcval(gzcompress($data), 'base64');

				$r = $xmlrpc->send(new xmlrpcmsg("queue_job", array($filexml, $content)));

				//post XML-RPC data and get job ID
				$job_id = php_xmlrpc_decode($r->value());

				header("Location: ?action=viewjob&jobid=$job_id");
				exit();
				

			}else{ //couldn't move the file so there was a problem with the upload process
				$message="There was a problem with the file upload.";
				include("templates/error.php");
			}

		}else{ //if the extension doesn't match pdf or xml
			$message = "The filetype that you have uploaded is unsupported. Only PDF and XML files may be uploaded";
			include("templates/error.php");
		}
		
	}else{ //if no file was uploaded, display upload form
		include("templates/upload_form.php");
		include("templates/footer.php");
	}

}





if(!isset($_GET['action'])){
	$_GET['action'] = 'index';
}

switch($_GET['action']){
	
	case 'submit':
		upload_view();
	break;

	case 'status':
		status_view();
	break;

	case 'get':
		get_view();
	break;

	case 'viewjob':
		jobstatus_view();
	break;

	case 'index': default:
	include("templates/header.php");
	include("templates/index.php");
	include("templates/footer.php");
	break;
}

?>
