<?php

/**
* RESTFul API for paper processing with SAPIENTA
*
*/
require("config.php");
require("sapienta.php");


/**
 * Converts an associative array of arbitrary depth and dimension into JSON representation.
 *
 * NOTE: If you pass in a mixed associative and vector array, it will prefix each numerical
 * key with "key_". For example array("foo", "bar" => "baz") will be translated into
 * {'key_0': 'foo', 'bar': 'baz'} but array("foo", "bar") would be translated into [ 'foo', 'bar' ].
 *
 * @param $array The array to convert.
 * @return mixed The resulting JSON string, or false if the argument was not an array.
 * @author Andy Rusterholz
 */
function array_to_json( $array ){

    if( !is_array( $array ) ){
        return false;
    }

    $associative = count( array_diff( array_keys($array), array_keys( array_keys( $array )) ));
    if( $associative ){

        $construct = array();
        foreach( $array as $key => $value ){

            // We first copy each key/value pair into a staging array,
            // formatting each key and value properly as we go.

            // Format the key:
            if( is_numeric($key) ){
                $key = "key_$key";
            }
            $key = "'".addslashes($key)."'";

            // Format the value:
            if( is_array( $value )){
                $value = array_to_json( $value );
            } else if( !is_numeric( $value ) || is_string( $value ) ){
                $value = "'".addslashes($value)."'";
            }

            // Add to staging array:
            $construct[] = "$key: $value";
        }

        // Then we collapse the staging array into the JSON form:
        $result = "{ " . implode( ", ", $construct ) . " }";

    } else { // If the array is a vector (not associative):

        $construct = array();
        foreach( $array as $value ){

            // Format the value:
            if( is_array( $value )){
                $value = array_to_json( $value );
            } else if( !is_numeric( $value ) || is_string( $value ) ){
                $value = "'".addslashes($value)."'";
            }

            // Add to staging array:
            $construct[] = $value;
        }

        // Then we collapse the staging array into the JSON form:
        $result = "[ " . implode( ", ", $construct ) . " ]";
    }

    return $result;
}



/**
* Return status of job
*
*/
function sapienta_api_jobstatus(){
	$id = (int)$_GET['id'];

	$sc = new SAPIENTAClient();
	$job =$sc->get_job_status($id);

	print array_to_json($job);
}

function sapienta_api_serverstats(){
	$sc = new SAPIENTAClient();
	$stats = $sc->get_service_status();
	
	print array_to_json($stats);
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

				print array_to_json(array("job_id" => $job_id));
				

			}else{ //couldn't move the file so there was a problem with the upload process
				$message="There was a problem with the file upload.";
				print array_to_json(array("error" => $message));
			}

		}else{ //if the extension doesn't match pdf or xml
			$message = "The filetype that you have uploaded is unsupported. Only PDF and XML files may be uploaded";
			print array_to_json(array("error" => $message));
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
