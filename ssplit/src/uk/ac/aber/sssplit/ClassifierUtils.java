package uk.ac.aber.sssplit;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLEncoder;
import java.util.Hashtable;
import java.util.Random;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

import org.xml.sax.InputSource;
import org.xml.sax.SAXException;


enum CoreSc
{
	Bac,Con,Exp,Goa,Met,Mot,Obs,Res,Mod,Obj,Hyp
}

class NamedObject<T> {
	  public final int id;
	  public final T object;

	  public NamedObject(int id, T object) {
	    this.id = id;
	    this.object = object;
	  }
	}

/*
 * this class need some updating/modification to make this appropriate for SSSplit2.
 */
public class ClassifierUtils {
	private static Random random = new Random();

	protected static String randomString() {
		return Long.toString(random.nextLong(), 36);
	}
	
	public NamedObject<org.w3c.dom.Element> setAttributes(CoreSc res, org.w3c.dom.Element newEle, Hashtable<String, Integer> conceptId)
	{
		int concept_count=0;
		  switch(res)
		  {
		    case Bac:
			      conceptId.put("Bac", ((Integer)conceptId.get("Bac")).intValue()+1);
			      concept_count=((Integer)conceptId.get("Bac")).intValue();
			      newEle.setAttribute("novelty","None");
			      newEle.setAttribute("advantage","None");
			      break;
		    case Con:
			      conceptId.put("Con", ((Integer)conceptId.get("Con")).intValue()+1);
			      concept_count=((Integer)conceptId.get("Con")).intValue();
			      newEle.setAttribute("novelty","None");
			      newEle.setAttribute("advantage","None");				     
			      break;
		    case Exp:
			      conceptId.put("Exp", ((Integer)conceptId.get("Exp")).intValue()+1);
			      concept_count=((Integer)conceptId.get("Exp")).intValue();
			      newEle.setAttribute("novelty","None");
			      newEle.setAttribute("advantage","None");
			      break;
		    case Goa:
			      conceptId.put("Goa", ((Integer)conceptId.get("Goa")).intValue()+1);
			      concept_count=((Integer)conceptId.get("Goa")).intValue();
			      newEle.setAttribute("novelty","None");
			      newEle.setAttribute("advantage","None");
			      break;
		    case Met:
			      conceptId.put("Met", ((Integer)conceptId.get("Met")).intValue()+1);
			      concept_count=((Integer)conceptId.get("Met")).intValue();
			      newEle.setAttribute("novelty","None");
			      newEle.setAttribute("advantage","None");
			      break;
		    case Mot:
			      conceptId.put("Mot", ((Integer)conceptId.get("Mot")).intValue()+1);
			      concept_count=((Integer)conceptId.get("Mot")).intValue();
			      newEle.setAttribute("novelty","None");
			      newEle.setAttribute("advantage","None");
			      break;
		    case Obs:
			      conceptId.put("Obs", ((Integer)conceptId.get("Obs")).intValue()+1);
			      concept_count=((Integer)conceptId.get("Obs")).intValue();
			      newEle.setAttribute("novelty","None");
			      newEle.setAttribute("advantage","None");
			      break;
		    case Res:
			      conceptId.put("Res", ((Integer)conceptId.get("Res")).intValue()+1);
			      concept_count=((Integer)conceptId.get("Res")).intValue();
			      newEle.setAttribute("novelty","None");
			      newEle.setAttribute("advantage","None");
			      break;
		    case Mod:
			      conceptId.put("Mod", ((Integer)conceptId.get("Mod")).intValue()+1);
			      concept_count=((Integer)conceptId.get("Mod")).intValue();
			      newEle.setAttribute("novelty","None");
			      newEle.setAttribute("advantage","None");
			      break;
		    case Obj:
			      conceptId.put("Obj", ((Integer)conceptId.get("Obj")).intValue()+1);
			      concept_count=((Integer)conceptId.get("Obj")).intValue();
			      newEle.setAttribute("novelty","None");
			      newEle.setAttribute("advantage","None");
			      break;
		    case Hyp:
			      conceptId.put("Hyp", ((Integer)conceptId.get("Hyp")).intValue()+1);
			      concept_count=((Integer)conceptId.get("Hyp")).intValue();
			      newEle.setAttribute("novelty","None");
			      newEle.setAttribute("advantage","None");
			      break;
		  }
		  return new NamedObject<org.w3c.dom.Element>(concept_count,newEle);
	}
	public void recombine(File mode2File, String resultFile,String outDir) throws ParserConfigurationException, IOException, SAXException, TransformerException
	{
		
		DocumentBuilderFactory fact = DocumentBuilderFactory.newInstance();
    	System.err.println(" After factory");
    	fact.setExpandEntityReferences(false);
    	fact.setIgnoringComments(true);
    	fact.setCoalescing(true); // Convert CDATA to Text nodes
	    fact.setNamespaceAware(false); // No namespaces: this is default
	    fact.setValidating(false); // Don't validate DTD: also default
	    fact.setXIncludeAware(false);
    	DocumentBuilder build = fact.newDocumentBuilder();
    	
		BufferedReader resultReader = new BufferedReader(new FileReader(resultFile));
		
		StringBuffer sb = new StringBuffer(1024);
		String line="";
		while ((line=resultReader.readLine())!=null) {
			sb.append(line);
		}
		resultReader.close();

		InputSource isource = new InputSource(new InputStreamReader(new FileInputStream(mode2File), "UTF-8"));
		org.w3c.dom.Document d = build.parse(isource);
	    

	    String []resultsData = sb.toString().split(">");

	    if (d!=null) 
	    {
	    
	        int count=2;
	        //get all the s tags
	        org.w3c.dom.NodeList elements=d.getElementsByTagName("s");
	        String concepts[] = {"Bac","Con","Exp","Goa","Met","Mot","Obs","Res","Mod","Obj","Hyp"};
	        Hashtable<String, Integer> conceptId = new Hashtable<String, Integer>(11);
			for(int con=0;con<concepts.length;con++)
			{
			  conceptId.put(concepts[con], 0);
			}
			
	        for(int ele=0; ele<elements.getLength(); ele++)
	        {
	            //skip the first sentence as its the title
	        	org.w3c.dom.Element element = (org.w3c.dom.Element)elements.item(ele);
	            if(element.getAttribute("sid").equals("1"))
	            {
	                continue;
	            }
	            //get the CoreSc1 child  
		        int flag=0;
		        if(element.hasChildNodes())
		        {
		        	org.w3c.dom.NodeList core1 = element.getElementsByTagName("CoreSc1");
		        	
		        		if(core1.getLength()>0)
		        		{
		        			flag=1;
		        			org.w3c.dom.NodeList core2 = element.getElementsByTagName("CoreSc2");
		        			if(core2.getLength()>0)
		        			{
		        				flag=2;
		        				org.w3c.dom.NodeList core3 = element.getElementsByTagName("CoreSc3");
		        				if(core3.getLength()>0)
		        				{
		        					//((org.w3c.dom.Element)child).setAttribute("type",resultsData[count-2]);      
		        					flag=3;
		        				}
		        			}
		        		}
		        	// if CoreSc1 tag is already not there we add it and set the type and concept ids.
		        		//System.out.println("\n\n\nValue of Flag:"+flag);
		        	if(flag<3) 
		        	{
		        		org.w3c.dom.Element newEle = null;
		        		if(flag==0)
		        		{
		        			newEle = d.createElement("CoreSc1");
		        		}
		        		if(flag==1)
		        		{
		        			newEle = d.createElement("CoreSc2");
		        		}
		        		if(flag==2)
		        		{
		        			newEle = d.createElement("CoreSc3");
		        		}
		        		
		        		if(newEle==null)
		        		{
		        			System.out.println("WHY NEWELE IS NULLLLLLLL");
		        			throw new NullPointerException();
		        			//System.exit(0);
		        		}
		        		newEle = (org.w3c.dom.Element) element.appendChild(newEle);
		        		newEle.setAttribute("type",resultsData[count-2]);
		        		newEle.setAttribute("atype","GSC");
		        		int concept_count=0;
		        		CoreSc res= CoreSc.valueOf(resultsData[count-2]);
		        		NamedObject<org.w3c.dom.Element> updatedElement=setAttributes(res, newEle, conceptId);
		        		newEle=(org.w3c.dom.Element)updatedElement.object;
		        		concept_count=updatedElement.id;
		        		newEle.setAttribute("conceptID",resultsData[count-2].concat(Integer.toString(concept_count)));
		        		//children=element.getChildNodes();
		        		//foreach($children as $child)
		        		//System.out.println("Node name:"+element.getFirstChild().getNodeName());
		        		element.insertBefore(newEle, element.getFirstChild());

		        		//			  while(element.hasChildNodes()&&!(element.getFirstChild().getNodeName().equals("CoreSc1"))) //!(element.getFirstChild().getLocalName().equals("CoreSc1"))
		        		//			  {
		        		//			    org.w3c.dom.Node child = element.getFirstChild();
		        		//			    System.out.println("child name:"+child.getNodeName());
		        		//			    if(!(child.getNodeName().equals("CoreSc1")))
		        		//	            {
		        		//			    	org.w3c.dom.Node annChild=element.removeChild(child);
		        		//	                System.out.println("\n child name"+annChild.getLocalName()+", has child :"+annChild.hasChildNodes());
		        		//	                newEle.appendChild(annChild);
		        		//	            }
		        		//			  }
		        	}
		        	else
		        	{
		        		//we do not put the predicted annotation, but counter should increment, so that next prediction is assigned to currect sentence. 
		        	}
		        }          
		   flag=0;
	       count++;
	     }
	        //BufferedWriter out = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(mode2File), "UTF-8"));
	        //String doc=SSSplit.getString(d);
	        TransformerFactory tFactory =
	            TransformerFactory.newInstance();
	          Transformer transformer = tFactory.newTransformer();

	          DOMSource source = new DOMSource(d);
	          StreamResult result = new StreamResult(new OutputStreamWriter(new FileOutputStream(outDir.concat(mode2File.getName())), "UTF-8"));
	          transformer.transform(source, result);
	        //out.write(doc);
	    }
	}
	/**
	 * Sends the paper over a post request to the webservice for classifying
	 * 
	 * @param emailAddress - email address of the user sending the paper
	 * @param filename - the name of the file to send
	 * @param paperName - the paper name
	 * @param callBackUrl - the call back URL to update the modified paper, should be http://sapientserver/ARTServlet?action=classify_submit&....
	 * @throws UnsupportedEncodingException 
	 */
	public static void sendPaper(String emailAddress,String filename,String name,String callBackUrl) throws UnsupportedEncodingException
	{
		URL url;

		String boundary= randomString();

		//build the call back URL

		callBackUrl=callBackUrl+"?action=classify_replace&mode2file="+URLEncoder.encode(filename,"US-ASCII");
		//System.out.println("call back url " + callBackUrl);


		//example  /home/cos/workspace/Sapient2_svn/sapient_workspace/scrapbook/Maria_b506219e/mode2.xml
		//we want to extract Maria_b506219e and add .xml
		System.out.println("File separator:"+System.getProperty("file.separator")+"\n File name parent:"+new File(filename).getParent());
		String regex="/";
		if(System.getProperty("file.separator").equals("\\"))
		{
			regex="\\\\";
		}
		System.out.println("regex"+regex);
		String splitStr[]=new File(filename).getParent().split(regex); //fixed by shyama //bound to break on windows because regex won't like / but works fine on unix;

		String serverName=splitStr[splitStr.length-1]+".xml";

		try 
		{
			//url = new URL("http://pcafc.dcs.aber.ac.uk/~cos/webservice/upload_test.php");
			url = new URL("http://www.ebi.ac.uk/Rebholz-srv/sapienta/webservice/upload_test.php");
			HttpURLConnection con = (HttpURLConnection) url.openConnection();
			con.setRequestMethod("POST");
			con.setDoOutput(true);

			con.setRequestProperty("Content-type","multipart/form-data; boundary=\""+boundary+"\"");
			con.connect();

			OutputStreamWriter out = new OutputStreamWriter(con.getOutputStream(),"UTF-8");
			BufferedReader in = new BufferedReader(new InputStreamReader(new FileInputStream(filename), "UTF-8")); 
			//			StringBuffer sb=new StringBuffer();

			//send the file	
			//con.setRequestProperty("Content-Length", Integer.toString(sb.toString().getBytes().length));

			out.write("--"+boundary+"\r\n");				
			out.write("Content-Disposition: form-data; name=\"file\"; filename=\""+serverName+"\"\r\n");
			out.write("Content-Type: text/xml\r\n\r\n");

			String str;
			while ((str = in.readLine()) != null) 
			{ 
				out.write(str);		
			} 	

			out.write("\r\n--"+boundary+"\r\n");
			out.write("Content-Disposition: form-data; name=\"email\"\r\n\r\n"+emailAddress+"\r\n");
			out.write("--"+boundary+"\r\n");
			out.write("Content-Disposition: form-data; name=\"callbackurl\"\r\n\r\n"+URLEncoder.encode(callBackUrl,"US-ASCII")+"\r\n");
			out.write("--"+boundary+"\r\n");
			out.write("Content-Disposition: form-data; name=\"name\"\r\n\r\n"+name+"\r\n");
			out.write("--"+boundary+"\r\n");
			out.write("Content-Disposition: form-data; name=\"submit\"\r\n\r\nSubmit\r\n");
			out.write("--"+boundary+"--"+"\r\n");    
			out.close();

			in = new BufferedReader(new InputStreamReader(con.getInputStream()));	

			while ((str = in.readLine()) != null) {
				//System.out.println(str);
			}
			in.close();
			con.disconnect();

		} 
		catch (MalformedURLException e) 
		{
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		catch (IOException e)
		{
			e.printStackTrace();
		}

	}
//	public void getPaper()
//	{
//		
//		String url = URLDecoder.decode(request.getParameter("url"),
//		"US-ASCII");
//
//		/*WARNING: we are taking the full path to the file and replacing it with a user supplied URL
//this is to save us having to figure out the file path again. 
//BUT THIS IS A HUGE SECURITY VULNERABILITY
//as it allows a remote user to rewrite any file that sapient has permission to
//to stop this being abused any url not begining http://www.ebi.ac.uk/Rebholz-srv/sapienta/ will
//throw a security exception. As only a single server runs the web service
//we can check to make sure that only the web service system can be the source
//of a new file. 
//
//Ideally we should just use the paper name and rebuild the directory.
//The paper name should also be banned from containing slashes or percent signs.
//However I don't quite understand the sapient enough to get this working. 				
//		 */
//
//		//System.out.println("\nCall back URL:"+url);
//		if(!url.startsWith("http://www.ebi.ac.uk/Rebholz-srv/sapienta/"))
//		{
//			throw new SecurityException("disallowed URL");
//		}
//
//		String mode2file = URLDecoder.decode(
//				request.getParameter("mode2file"), "US-ASCII");
//
//		//System.out.println("Replacing " + mode2file + " with " + url);
//
//
//		URL replacement = new URL(url);
//		HttpURLConnection connection = (HttpURLConnection) replacement
//		.openConnection();
//
//		connection.setRequestMethod("GET");
//
//		connection.connect();
//
//		BufferedReader reader = new BufferedReader(
//				new InputStreamReader(connection.getInputStream()));
//		// following line should change, instead of writing to mode2file, we will right a new file with results. Shyama need to add a function that recombine.
//		String parent=new File(mode2file).getParent();
//		System.out.println("mode2 parent path"+parent);
//		String resultFile=parent.concat(System.getProperty("file.separator")).concat("results.txt");
//		//BufferedWriter writer = new BufferedWriter(new FileWriter(mode2file));			
//		BufferedWriter writer = new BufferedWriter(new FileWriter(resultFile));
//		String line = null;
//		while ((line = reader.readLine()) != null) {
//			writer.write(line);
//		}
//		writer.close();
//		reader.close();
//		connection.disconnect();
//		recombine(mode2file,resultFile);
//		//System.out.println("done");
//		//added by shyama to see whether it helps to view next few lines in a html page, it does
//		response.setContentType("text/html");
//		PrintWriter out=response.getWriter();
//		out.println("<html>\n");
//		out.println("<head>\n");
//		out.println("<title>SAPIENTA Paper Classifier Link</title>\n");
//		out.println("</head>\n");
//		out.println("<body>\n");
//		out.println("Your paper " + name + " has been upated.");
//		out.println("<a href=\"ART?action=showmode2&sid=s1&name="+name+"\">Click here to view the updated paper</a>");
//		out.println("</body>\n");
//		out.println("</html>\n");
//	}
//	//in case of error. At the moment, not very specific.
//} catch (Exception e) {
//	e.printStackTrace();
//	response.setContentType("text/plain");
//	response.getWriter().println("Problem occured, Please Contact the developer");
//}
////System.out.println(":::at end of do get:::"+name);
//}
}
