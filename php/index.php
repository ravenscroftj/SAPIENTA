<?php
/**
* PHP web frontend for SAPIENTA (if you don't have WSGI on your web server)
*
*/


require("config.php");
require("sapienta.php");


/**
* View used to display the status page for a running job
*
*/
function jobstatus_view(){

	include("templates/header.php");

	$id = (int)$_GET['jobid'];

	//talk to SAPIENTA server about the job
	$sc = new SAPIENTAClient();
	$job =$sc->get_job_status($id);

	
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
	}elseif( $job['status'] == "FAILED" ){
	?>
	<p>Unfortunately Job <?php echo $job['jobid']; ?> encountered an error and could not be completed.</p>

	<textarea style="width: 640; height:480;"><?php echo $job['error']; ?></textarea>

	<p>This may be a problem with the paper file or it may be a server error. Please try again later or try
	annotating a different paper</p>

	<?
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
	$sc = new SAPIENTAClient();
	$job =$sc->get_job_status($id);
	$content = $sc->get_job_content($id);

	header('Content-Type: application/octet-stream');
	header("Content-Transfer-Encoding: Binary");
	header("Content-disposition: attachment; filename=\"".basename($job['filename'])."\"");

	print $content;
	exit();
}

/**
* Return the current status of the server
*
*/
function status_view(){

	include("templates/header.php");

	$sc = new SAPIENTAClient();
	$stats = $sc->get_service_status();

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
				
				
				$sc = new SAPIENTAClient();
				$job_id = $sc->submit_job($filename);

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

	case 'apiinfo':
	include("templates/header.php");
	include("templates/api.php");
	include("templates/footer.php");
	break;

	case 'index': default:
	include("templates/header.php");
	include("templates/index.php");
	include("templates/footer.php");
	break;
}

?>
