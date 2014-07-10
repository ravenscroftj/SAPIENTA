package uk.ac.aber.sssplit;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileFilter;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.io.StringReader;
import java.io.UnsupportedEncodingException;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import nu.xom.Builder;
import nu.xom.Document;
import nu.xom.Element;
import nu.xom.Elements;
import nu.xom.Node;

import org.xml.sax.EntityResolver;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;
import org.xml.sax.XMLReader;
import org.xml.sax.helpers.XMLReaderFactory;


enum OPTION {fs,ds,sf,sd,fcr,cfr,dc,cd,fcl,cfl,dcl,cdl,fsc,dsc,fcs,cfs,csf,sfc,scf,dcs,cds,csd,sdc,scd,fscl,dscl,fcsl,cfsl,csfl,sfcl,scfl,dcsl,cdsl,csdl,sdcl,scdl,fscr,dscr,fcsr,cfsr,csfr,sfcr,scfr,dcsr,cdsr,csdr,sdcr,scdr};
class DummyEntityResolver implements EntityResolver {
    public InputSource resolveEntity(String publicID, String systemID)
        throws SAXException {

        return new InputSource(new StringReader(""));
    }
}

class XMLFileFilter implements FileFilter
{
	String end;
	public XMLFileFilter(String e)
	{
		end = e;
	}
	public boolean accept(File file)
	{
		//File f = new File(name);
		String name = file.getName();
		//System.out.println("in XMLFILEFILTER : file name end "+name.endsWith("xml")+ "file is file"+ file);
		if((file.isFile()&&name.endsWith(end)))
		{
			//System.out.println(" in xmlfilefilter this is file and ends with xml : "+file.isFile()+ "file name : "+name+"f path:"+file.getAbsolutePath());
			return true;
		}
		else
			return false;
		
	}
}


class DirFileFilter implements FileFilter
{
	String end;
	public DirFileFilter()
	{
	}
	public boolean accept(File file)
	{
		//String name = file.getName();
		//String name = file.getName();
		
		if(file.isDirectory())
		{
			//System.out.println("in dirFILEFILTER : file is folder"+ file);
			return true;
		}
		else
			return false;
		
	}
}


public class XMLSentSplit {
	
	public static StringBuffer queuePath=new StringBuffer("/nfs/research2/textmining/sapienta/queue/processing/output/All/Test/Feature/");
	public static String getFileName(String filepath)
	{
		char sep = File.separatorChar;
		String filename = "";
		if(sep == '/') {
			filename = filepath.replaceAll(".*/" ,"");
		} else {
			filename = filepath.replaceAll(".*\\\\" ,"");
		}
		String name = filename; 
		if(filename.matches(".*\\.xml$")) {
			name = name.substring(0, filename.length()-4);  // need to be changed..... so that it can capture file name without extension..
		}
		return name;
	}
	public static void processFile(String filepath, String fileDir){
		//System.out.println("filepath: " + filepath + " fileDir: " + fileDir);
		String name = getFileName(filepath);
		 // Read the whole file into a stringbuffer
        //StringBuffer sb = new StringBuffer(1024);
        //BufferedReader reader;
        //System.out.println("\n\n File Name : "+filepath);
        try {
			//reads from a string that is the contents of the file
			StringReader sr = new StringReader(filepath);
			XMLReader reader = XMLReaderFactory.createXMLReader();
        	reader.setEntityResolver(new DummyEntityResolver());
			File f = new File(filepath);
			String xml = "<?xml ...";
			xml = xml.trim().replaceFirst("^([\\W]+)<","<");
			//makes a xom.Document from the string
			Document paperDoc = new Builder(reader).build(f);
			//Element paper = paperDoc.createElement();
			// Adding paper tag
			Element root = paperDoc.getRootElement();
			//System.out.println("\n\nroot tag  = "+root.getLocalName());
			if(root.getLocalName()!="PAPER")
			{
				/*
				Elements children = root.getChildElements();
				int i=0;
				for(i=0;i< children.size();i++)
				{
					
				}*/
			Element paperElement = new Element("PAPER"); // shs
			//while(paperDoc.)
			Element node = paperDoc.getRootElement();
			Elements ele = node.getChildElements();
			//System.out.println("\n\n\n\n Node being added  :\n"+node.toString()+"\t Size of this Elements : "+ele.size());
			Node nodeAdd = new Element(node);
			paperElement.appendChild(nodeAdd);
			Document doc = new Document(paperElement);
			paperDoc = doc;
		    //String result = doc.toXML();
		    //System.out.println("\n\n\n\n new Document  :\n"+result);
			}// end of if
			else
				System.out.println("\n Checked that the Paper tag is present. \n"); //root = "+root.getValue());
        
            String fileString = paperDoc.toXML();//stringWriter.getBuffer().toString(); // shs -- paper tag is added; this way its already free from <!DOCTYPE ...
			String outString = "";
			fileString = fileString.replaceFirst("<!DOCTYPE.+?>","");
    		Pattern p = Pattern.compile("<PAPER>|<paper>");
    		Matcher m = p.matcher(fileString.substring(0,fileString.length()/4));
    		if(!m.find())
    		{
    			String paper = "<PAPER>";
    			System.out.println("The Root node is not Paper");
    			fileString = paper.concat(fileString+"</PAPER>");
    			//str = concat
    		}
    		String badWhiteSpace = "(\t|\r|\n|\\s)";
    		String replacement = "<\\?jarpath /\\?>|<\\?host null:8181\\?>|<\\?viewer picture\\?>";
            //System.out.println("\n before replacing replacement \n\n\n File String : \n\n\n"+fileString);           
    		fileString = fileString.replaceAll(replacement, "");
    		fileString = fileString.replaceAll(badWhiteSpace, "sapientPOO");
    		fileString = fileString.replaceAll("(sapientPOO)+", " ");
    		fileString = fileString.replaceAll(">\\s<", "><");
    		fileString = fileString.replaceAll("<FIGURE/>", "");
			    //System.out.println("FileReader : \n\n"+fileString);
    		StringReader stReader = new StringReader(fileString);
    		//System.out.println("after string reader1");
    		//System.out.println("after string reader2");
    		//System.out.println("after string reader3");
    		InputSource isource = new InputSource(stReader);
    		//System.out.println("after InputSource1");
    		//System.out.println("after InputSource2");
    		//System.out.println("after InputSource3");
			DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
			factory.setIgnoringComments(true);
			factory.setCoalescing(true); // Convert CDATA to Text nodes
			factory.setNamespaceAware(false); // No namespaces: this is default
			factory.setValidating(false); // Don't validate DTD: also default
			factory.setXIncludeAware(false);
			//StringReader stReader = new StringReader(fileString);
			//InputSource isource = new InputSource(stReader);
			DocumentBuilder parser = factory.newDocumentBuilder();			   
			org.w3c.dom.Document document = parser.parse(isource);
			SSSplit.fileName=filepath;
			outString = SSSplit.sentenceExtraction(document, name);
			
			
			
			if(outString!=null)
			{
				try{
				StringReader outReader = new StringReader(outString);
				Document outDoc = new Builder().build(outReader);
				
				File a = new File(fileDir, name + "_mode2.xml");
				System.out.println("the outputfile is: " + a.toString());
			
				BufferedWriter out = new BufferedWriter(new OutputStreamWriter(
                            new FileOutputStream(a),
                            "UTF8"));
				out.write(outString);
				out.close();
				} catch(nu.xom.ParsingException pe) {
		        	System.out.println("\n\n A parsing Error occured in the output file");
				}
			}
			else
			{
				System.out.println("\n\n The file does not have abstract and body, so no output file for " + filepath);
			}
        	//}//end of if
        
        
		} catch (UnsupportedEncodingException e1) {
			e1.printStackTrace();
		} catch (FileNotFoundException e1) {
			e1.printStackTrace();
		} catch (IOException e) {
		} catch (Exception e1) {
			e1.printStackTrace();
		}
	}
	
	public static String[] recursiveFiles(File dir, String outdirpath)
	{
		XMLFileFilter filter = new XMLFileFilter("xml");
		DirFileFilter dirFilter = new DirFileFilter();
		File files[] = dir.listFiles(filter);
		File folders[] = dir.listFiles(dirFilter);
		
		//list[0]= dir.getPath();
		//String dirpath = dir.getPath();//+ File.separator +  s ;
		
		int i=0;
		if(folders!=null)
		{
		while(i<folders.length)
		{
			//System.out.println("It is folder :"+folders[i].getName() +" and going to find files under it");
			
				String outList[] = recursiveFiles(folders[i],outdirpath);
				//System.out.println("Returned from file search and no of files :" + outList.length);
				if(outList!=null)
				{
					//System.out.println("Files returned from folder : no of files "+ outList.length);
					for (String s: outList) {
					//String path = dirpath + File.separator +  s ;
						processFile(s, outdirpath);
					}
				}
				/*for(int k=0; k<outList.size();k++)
				{
					list.add(outList.get(k)); 
				}*/
				i++;
				
		}
		}
		
		if(files!=null)
		{
			int j = 0;
			int k = files.length;
			//System.out.println("It is folder :"+ dir +" adding files to list. files length"+ k);
			
		String list[] = new String[files.length];
		while(j<k)
		{
			//System.out.print("in while\n");
			
			//if(files[i].isFile())
			list[j]= files[j].getAbsolutePath();
			j++;
		}
		//System.out.print("listing done");
		return list;
		}
		return null;
	}
	private static void singleFileSentencizing(String inputFilename, String outdirpath)
	{
		File temp = new File(inputFilename);
		String path = temp.getPath();
		processFile(path, outdirpath);
	}
	private static void batchSentencizing(String inputDir, String outdirpath)
	{
		File directory = new File(inputDir);
		String dirpath = directory.getPath();
		//XMLFileFilter fileFilter = new XMLFileFilter("xml");
		//System.out.println("directory: " + directory + " dirpath: " + dirpath);
		//File files[] = directory.listFiles(fileFilter);
		//int i=0;

		String children[] = recursiveFiles(directory,outdirpath);
		if(children!=null)
		{
			for (String s: children) {
				//String path = dirpath + File.separator +  s ;
				processFile(s, outdirpath);
			}
		}
	}
	public static void printSystemOut(Process p)
	{
		StreamGobbler s1 = new StreamGobbler ("stdin", p.getInputStream ());
		StreamGobbler s2 = new StreamGobbler ("stderr", p.getErrorStream ());
		s1.start ();
		s2.start ();

		try {
			p.waitFor();
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		//System.out.println("Status:"+p.exitValue());
	}
	private static void classifySingle(String filepath, String outputDir, char option, char serverFlag) throws IOException, InterruptedException
	{
		String name = getFileName(filepath);
		//add ends withh "/" checking
		String classifyFilename="";
		if(option=='c')
		{
			classifyFilename=filepath;
		}
		else
		{
			classifyFilename=outputDir.endsWith(File.separator)? outputDir.concat(name.concat("_mode2.xml")):outputDir.concat(File.separator).concat(name.concat("_mode2.xml"));
		}
		//System.out.println("classifyfile name:"+classifyFilename);
		if(serverFlag=='l')
		{
			Process classifyProcess=Runtime.getRuntime().exec("perl /nfs/research2/textmining/sapienta/Project/sidePrograms/Code_for_svn/perl_code/pipeline_for_sapient_crfsuite.perl "+classifyFilename);
			//classifyProcess.waitFor();
			printSystemOut(classifyProcess);
			
		}
		else if (serverFlag=='r')
		{
			//send request to the server
			//File mode2File = new File(filepath);
            //String mode2FileString=mode2File.toString();
            //String serverAddress="http://www.ebi.ac.uk/Rebholz-srv/sapienta/webservice/upload_test.php";
			String serverAddress="http://www.ebi.ac.uk/Rebholz-srv/sapienta/CoreSCWeb/";
            Process uploadfileForClassification=Runtime.getRuntime().exec("curl -F file=@" + classifyFilename + serverAddress);
            printSystemOut(uploadfileForClassification);
		}
		
	}
	private static String classifyBatch(String inputDir, char flag) throws IOException, InterruptedException
	{
		inputDir=inputDir.endsWith(File.separator)? inputDir:inputDir.concat(File.separator);
		File directory = new File(inputDir);
		String dirpath = directory.getPath();
		
		//System.out.println("directory: " + directory + " dirpath: " + dirpath);
		
		File children[] = directory.listFiles(new XMLFileFilter(".xml"));
		if(children!=null)
		{
			//for (File s: children) {
				if(flag=='l')
				{	
					Process classifyProcess=Runtime.getRuntime().exec("perl /nfs/research2/textmining/sapienta/Project/sidePrograms/Code_for_svn/perl_code/pipeline_for_sapient_crfsuite.perl "+dirpath+" batch");//.exec("ls -all");//
					printSystemOut(classifyProcess);
					
					
					
					String batch_foldernames[];
					char sep = File.separatorChar;
					
					if(sep == '/') {
						batch_foldernames = inputDir.split("/");
					} else {
						batch_foldernames = inputDir.split("\\\\");
					}
					//-2 because e.g. user passed out directory is "/net/isilon4/research/textmining/sapienta/Project/Development/SSSplit2/corpora/test_batch_out/" then inputDir variable here has "/net/isilon4/research/textmining/sapienta/Project/Development/SSSplit2/corpora/test_batch_out/Sentencized". but result files are in .../test_batch_out/ folder. 
					//System.out.println("Last element of batch_f:"+batch_foldernames[batch_foldernames.length-2]);
					queuePath.append("Batch/").append(batch_foldernames[batch_foldernames.length-2]).append("/");
					return queuePath.toString();
				}
				else
				{
					//send request to server for classification
				}
			//}
		}
		return null;
	}
	/*
	 * @param args options, the file to be split, the output directory
	 * @param interpretation of two parameters after options changes depending the option value. If we want both sentencizing and classification,
	 * input directory is where non-splitted xml files are / or single file  and output directory is where files will be
	 * saved after merging with classified result. sentencized results will be outputDirectory/Sentencized directory  
	 */
	public static void main(String[] args) {
		if(args.length != 3) {
			System.out.println("Wrong number of arguments -- please supply a filename/directory for the XML file you wish to split into sentences, and an output directory for the finished product."+ args.length);
			System.exit(0);
		}
		String option = args[0];
		String inputFilename = "";
		String inputDir = "";	
		String fileDir = args[2];
		File outdir = new File(fileDir);
		String outdirpath = outdir.getAbsolutePath();
		//System.out.println("Outdir is : "+ outdirpath +" \n File Dir : "+ fileDir);
		outdirpath=outdirpath.endsWith(File.separator)? outdirpath:outdirpath.concat(File.separator);
		if(option.startsWith("-"))
		{
			try
			{
				OPTION optn=OPTION.valueOf(option.replace("-", ""));

				switch(optn)
				{
				case fs:
				case sf:
					singleFileSentencizing(args[1], outdirpath);
					break;
				case ds:
				case sd:
					batchSentencizing(args[1], outdirpath);
					break;
				case fcr:
				case cfr:
					System.out.println("Classification Process has not been incorporated yet for external User");
					break;
				case dc:
				case cd:
					System.out.println("Classification Process has not been incorporated yet for external User");
					break;
				case fcl:
				case cfl:
				{
					classifySingle(args[1], "", 'c','l'); //outdirpath for merged file
					ClassifierUtils ut=new ClassifierUtils();
					//String name=getFileName(args[1]);
					File m=new File(args[1]);
					//recombine(String mode2File, String resultFile)
					ut.recombine(m, queuePath.toString().concat(m.getName().concat("/result.txt")), outdirpath);
				}
					break;
				case dcl:
				case cdl:
				{
					String resPath=classifyBatch(args[1], 'l');
					ClassifierUtils ut=new ClassifierUtils();
					File mode2File[]=new File(args[1]).listFiles(new XMLFileFilter(".xml"));
					for(int fi=0;fi<mode2File.length;fi++)
					{
						ut.recombine(mode2File[fi], resPath.concat(mode2File[fi].getName().concat("/result.txt")), outdirpath);
					}
				}
					break;
				case fscr:
				case fcsr:
				case cfsr:
				case csfr:
				case sfcr:
				case scfr:
				{
					String outputDir=outdirpath.endsWith(File.separator)? outdirpath.concat("Sentencized".concat(File.separator)):outdirpath.concat(File.separator).concat("Sentencized".concat(File.separator));
					File dirChecker = new File(outputDir);
					if(!dirChecker.exists())
					{
						dirChecker.mkdirs();
					}
					singleFileSentencizing(args[1], outputDir);
					String name=getFileName(args[1]);
					classifySingle(outputDir.concat(name.concat("_mode2.xml")), outdirpath, 'c','r');
					ClassifierUtils ut=new ClassifierUtils();
					File m=new File(outputDir.concat(name.concat("_mode2.xml")));
					ut.recombine(m, queuePath.toString().concat(m.getName().concat("/result.txt")), outdirpath);
					//System.out.println("Classification Process has not been incorporated yet for external User");
					//classifySingle(args[1], outdirpath, 'l');
				}
					break;
				case dsc:
				case dcs:
				case cds:
				case csd:
				case sdc:
				case scd:
				{
					String outputDir=outdirpath.endsWith(File.separator)? outdirpath.concat("Sentencized".concat(File.separator)):outdirpath.concat(File.separator).concat("Sentencized".concat(File.separator));
					File dirChecker = new File(outputDir);
					if(!dirChecker.exists())
					{
						dirChecker.mkdirs();
					}
					batchSentencizing(args[1], outputDir);
					System.out.println("Classification Process has not been incorporated yet for external User");
				}
					break;
				case fscl:
				case fcsl:
				case cfsl:
				case csfl:
				case sfcl:
				case scfl:
				{
					String outputDir=outdirpath.endsWith("/")? outdirpath.concat("Sentencized/"):outdirpath.concat(String.valueOf(File.separatorChar)).concat("Sentencized/");
					File dirChecker = new File(outputDir);
					if(!dirChecker.exists())
					{
						dirChecker.mkdirs();
					}
					singleFileSentencizing(args[1],outputDir); //outdirpath will be used for classified merged output
					String name=getFileName(args[1]);
					classifySingle(outputDir.concat(name.concat("_mode2.xml")), outdirpath, 'c','l');
					ClassifierUtils ut=new ClassifierUtils();
					File m=new File(outputDir.concat(name.concat("_mode2.xml")));
					ut.recombine(m, queuePath.toString().concat(m.getName().concat("/result.txt")), outdirpath);
				}
					break;
				case dscl:
				case dcsl:
				case cdsl:
				case csdl:
				case sdcl:
				case scdl:
				{
					String outputDir=outdirpath.endsWith("/")? outdirpath.concat("Sentencized/"):outdirpath.concat(String.valueOf(File.separatorChar)).concat("Sentencized/");
					File dirChecker = new File(outputDir);
					if(!dirChecker.exists())
					{
						dirChecker.mkdirs();
					}
					batchSentencizing(args[1], outputDir);
					String resPath=classifyBatch(outputDir, 'l');
					ClassifierUtils ut=new ClassifierUtils();
					File mode2File[]=new File(outputDir).listFiles(new XMLFileFilter(".xml"));
					for(int fi=0;fi<mode2File.length;fi++)
					{
						ut.recombine(mode2File[fi], resPath.concat(mode2File[fi].getName().concat("/result.txt")), outdirpath);
					}
				}
					break;
				}
			}catch(Exception e)
			{
				e.printStackTrace();
				//change following print statement and mention all the options
				System.out.println("Wrong option: please use either -d to split all the files in a specified directory, or -f to split a particular file.");
			}		
		}
		else
		{
			System.out.println("Options should be preceeded by \"-\"");
		}
	}
}
