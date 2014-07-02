package uk.ac.aber.sssplit;

import java.io.StringReader;
import java.io.StringWriter;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.Vector;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.regex.PatternSyntaxException;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import org.w3c.dom.Document;
import org.xml.sax.InputSource;
import org.w3c.dom.Attr;
import org.w3c.dom.DocumentFragment;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import uk.ac.aber.sssplit.NodeInt;
import uk.ac.aber.sssplit.StringInt;

import java.io.*;
import javax.xml.transform.*;
import javax.xml.transform.dom.*;
import javax.xml.transform.stream.*;

/** Splits a SciXML file into sentences, respecting the XML tags.
 * 
 * @author Maria Liakata (mal)
 * @author Claire Q (cim)
 * @author Shyamasree Saha
 *
 */
class StringInt{
	public String sTags;
	public int id;
    //public Vector<Element> vec;
	public StringInt()
	{
		sTags = "";
		id = 2;
		//vec = new Vector<Element>();
	}
    public StringInt(String str,int i)//,Vector<Element> v)
	{
		sTags = new String(str);
		id = i;
		//vec = (Vector<Element>)v.clone();
	}
}

class NodeInt{
	public Node node;
	public int id;
	public NodeInt()
	{
		node = null;
		id = 2;
	}
	public NodeInt(Node n,int i)
	{
	    node = n.cloneNode(true);//copy();
		id = i;
	}
	public void setNode(Node n)
	{
	    node = n.cloneNode(true);//n.cloneNode(true);
	}
    public void setId(int n)
	{
	    id = n;//.cloneNode(true);//n.cloneNode(true);
	}
	
}

public class SSSplit {
	private static final int sapientVersion = 597;
	public static String fileName;
	private static StringBuffer finalbuffer;
	//private static int flagAbs;
    //private static int flagBody;
	public static String removeInvalidTags(String string)
	{
		//System.out.print("in Invalid Tag\n");
		//string = string.replaceAll("<FIGURE/>", "");
        //clearString = clearString.replaceAll("<fig.*?/>","");
        //string = string.replaceAll("<graphic.*?/>", "");//shs
        //String newClearString = clearString;
        //shs
        /*
        String abstractTag = "abstract>";
        String pTag = "p>";
        String bodyTag = "body>";
        String titleTag = "title>";
        String divTag = "div>";
        */
        //Pattern removeTags = Pattern.compile("<"+"/?"+abstractTag+"|"+pTag+"|"+bodyTag+"|"+titleTag+"|"+divTag);
        //Matcher remover = removeTags.matcher(newClearString);
        // removing all invalid tags...

        
        //Pattern openingTags = Pattern.compile("<([^/]+?)>");
        //Matcher openingTagsMatcher = openingTags.matcher(string);
        
        int i=0;
        Vector<String> tags = new Vector<String>();
        
        Pattern closingTags = Pattern.compile("</?(.+?)>");
        Matcher closingTagsMatcher = closingTags.matcher(string);
        //int flag=0;
        /*
        while(openingTagsMatcher.find())
        {
        	i++;
        	//System.out.println("opening Tags found :tag"+i+": "+openingTagsMatcher.group(1));
        	tags.add(openingTagsMatcher.group(1));
        }
        
        */
        
        
        while(closingTagsMatcher.find())
        {
        	//tags[i] = new String();
        	//tags[i] = allTagsMatcher.group(0);
        	//tags.add(openingTagsMatcher.group(0));
        	//System.out.println("tag :"+closingTagsMatcher.group()+"\t group one : "+closingTagsMatcher.group(1));
        	//flag=0;
        	//System.out.println("tag : "+ closingTagsMatcher.group());
        	if(!(closingTagsMatcher.group().endsWith("/>")))
        	{
        	if(closingTagsMatcher.group().charAt(1)=='/')
        	{
        		//System.out.println("closing tag ");
        		if(tags.lastElement().startsWith(closingTagsMatcher.group(1)))
        		{
        			tags.removeElementAt(tags.size()-1);
        		}
        		else
        		{
        			String pattern = "<"+tags.elementAt(tags.size()-1)+">(.+?)(?="+closingTagsMatcher.group()+")";
        			//System.out.println("\n\n tag ele :   "+tags.elementAt(tags.size()-1)+"closing invalid tag :   "+closingTagsMatcher.group()+"pattern "+ pattern);
        			
        			
        			Pattern p = Pattern.compile(pattern);//.matcher(string).replaceAll("<"+tags.elementAt(tags.size()-1)+">(.+?)");
        			Matcher m = p.matcher(string);
        			if(m.find())
        			{
        			//System.out.println("\n p captured :" + m.group());
        			//string.replace(m.group(), m.group());
        			string = string.replaceAll(pattern, m.group());
        			//m.replaceAll(m.group());
        			}
        			else
        				System.out.println("ajob...");
        				
        		}
        	}
        	else
        	{
        		tags.add(closingTagsMatcher.group(1));
        		//System.out.println("Tag added");
        	}
        	}
        	/*
        	Enumeration<String> enu = tags.elements();
        	while(enu.hasMoreElements())
            {
            	String tag = enu.nextElement().toString(); 
            	if(tag.startsWith(closingTagsMatcher.group(1)))
            	{
            		//System.out.println("Match found :tag: "+tag);
            		flag=1;
            		break;
            		
            	}
            	
            }
        	if(!enu.hasMoreElements()&&flag==0)
            {
            	string = string.replace(closingTagsMatcher.group(0), "");
            		System.out.println("Matching tag not found");
            }
            */
        	// look ahead and remove invalid tags
        	//Pattern invalidPattern = Pattern.compile(allTagsMatcher.group(0));
        	//System.out.println("closing Tags found :tag"+j+": "+closingTagsMatcher.group(1));
        	//System.out.println("Tags found :tag"+i+": "+closingTagsMatcher.group(0));
        	//Pattern correspond = Pattern.compile(allTagsMatcher.group(0)+"(?=(.+?))"+"");
        	
        	//if()
        	
        }//end of outer while
  
        return string;
	}
	
	
	public static StringInt sentenceSplit(String clearString,int sid)
	{
		String badWhiteSpace = "(\t|\r|\n|\\s)";
        String replacement = "<\\?jarpath /\\?>|<\\?host null:8181\\?>|<\\?viewer picture\\?>";
        
        ////System.out.println("\n before replacing replacement \n\n\n File String : \n\n\n"+fileString);
        
            
            
        clearString = clearString.replaceAll(replacement, "");
        
        
        clearString = clearString.replaceAll(badWhiteSpace, "sapientPOO");
        clearString = clearString.replaceAll("(sapientPOO)+", " ");
        
        clearString = clearString.replaceAll(">\\s<", "><");
        clearString = clearString.replaceAll("<FIGURE/>", "");
        //Pattern figurePattern = Pattern.compile("<fig.*?>(.+?)</fig>");
       
        //fileString = fileString.replaceAll("<fig.*?>(.+?)</fig>","");
        clearString = clearString.replaceAll("<graphic.*?/>", "");
       
		StringBuffer finalbuffer = new StringBuffer();
		//System.out.println("\n\n\n Clear String in sentenceSplit :\n\n"+clearString);
		//to be appended later
        
		ArrayList<StringBuffer> nsentences = new ArrayList<StringBuffer>();
        String allowedAttrChars = "[\\w-_\2013\\.\\(\\)\\[\\]]";
		
        // .*?/>
        //String refSCIgeneral = "(?:(?i)(?:(?:\\d+[,\u2013])*\\d+)?(?:</IT>)?<REF(?:\\sTYPE=\"\\w+?\")?(?:\\stext=\"(?:refs?\\.(?:\\s)?)?(?:(?:\\d+[,\u2013])*\\d+)?\\w*?\")?(?:\\sID=\"(?:\\w-)?\\w+?(?:\\s\\w+?)*\")(?:\\sREFID=\"\\w+?\")?(?:/>|>(?:(?:refs?\\.(?:\\s)?)?(?:(?:\\d+[,-\u2013])*\\d+)?\\w*?</REF>))(?-i))";
        //works but not fully: String refSCIgeneral = "(?:(?i)(?:(?:\\d+[,\u2013])*\\d+)?(?:</IT>)?<REF(?:\\sTYPE=\"\\w+?\")?(?:\\stext=\"(?:refs?\\.(?:\\s)?)?(?:(?:\\d+[,\u2013])*\\d+)?\\w*?\")?(?:\\sID=\"(?:\\w-)?\\w+?(?:\\s\\w+?)*\")(?:\\sREFID=\"\\w+?\")?(?:/>|>(?:(?:refs?\\.(?:\\s)?)?(?:(?:\\d+(?:(?:<IT>)?\\w?(?:</IT>)?)[,-\u2013])*\\d+)?(?:(?:<IT>)?\\w?(?:</IT>)?)*?</REF>))(?-i))";
        //hangs: String refSCIgeneral = "(?:(?i)(?:(?:\\d+[,\u2013])*\\d+)?(?:</IT>)?<REF(?:\\sTYPE=\"\\w+?\")?(?:\\stext=\"(?:refs?\\.(?:\\s)?)?(?:(?:\\d+[,\u2013\u002D])*\\d+)?\\w*?\")?(?:\\sID=\"(?:\\w-)?\\w+?(?:\\s\\w+?)*\")(?:\\sREFID=\"\\w+?\")?(?:/>|>(?:(?:refs?\\.(?:\\s)?)?(?:\\d+(?:\\d*(?:<IT>)?\\w?(?:</IT>)?[,-\u2013])*(\\d+|(?:\\d*(?:<IT>)?\\w(?:</IT>)?))?</REF>))(?-i))";
        //String refSCIgeneral = "(?:(?i)(?:(?:\\d+[,\u2013])*\\d+)?(?:</IT>)?<REF(?:\\sTYPE=\"\\w+?\")?(?:\\stext=\"(?:refs?\\.(?:\\s)?)?(?:(?:\\d+[,\u2013\u002D])*\\d+)?\\w*?\")?(?:\\sID=\"(?:\\w-)?\\w+?(?:\\s\\w+?)*\")(?:\\sREFID=\"\\w+?\")?(?:/>|>(?:(?:refs?\\.(?:\\s)?)?(?:(?:(?:\\d+(?:<IT>)?\\w?(?:</IT>)?)|(?:(?:<IT>)?\\w(?:</IT>)?[,-\u2013]))*(?:(?:\\d+(?:<IT>)?\\w?(?:</IT>)?)|(?:(?:<IT>)?\\w?(?:</IT>)?)))?</REF>))(?-i))";
        //String refSCIgeneral = "(?:(?i)(?:(?:\\d+[,\u2013])*\\d+)?(?:</IT>)?<REF(?:\\sID=\"(?:\\w-)?\\w+?(?:\\s\\w+?)*\")(?:\\sREFID=\"\\w+?\")?(?:\\stext=\"(?:refs?\\.(?:\\s)?)?(?:(?:\\d+[,�\u2013\u002D])*\\d+)?\\w*?\")?(?:\\sTYPE=\"\\w+?\")?(?:\\s?/>|>(?:(?:refs?\\.(?:\\s)?)?(?:(?:(?:\\d+(?:<IT>)?\\w?(?:</IT>)?)|(?:(?:<IT>)?\\w(?:</IT>)?[-,\u2013])|(?:(?:<IT>)?\\w(?:</IT>)?[-,\u2013]))*(?:(?:\\d+(?:<IT>)?\\w?(?:</IT>)?)|(?:(?:<IT>)?\\w?(?:</IT>)?)))?</REF>))(?-i))"; // might have to add |(?:(?i)(<xref(\\s((id=\\d)|(ref-type=\"[a-z]+\")|(rid=[-\\w]))*)>[-,\\d]+</xref>|<xref.*/>))
        String refSCIgeneral = "(?:(?i)(?:(?:\\d+[,\u2013])*\\d+)?(?:</IT>)?<REF(?:(?:\\sID=\"(?:\\w-)?\\w+?(?:\\s\\w+?)*\")|(?:\\sREFID=\"\\w+?\")|(?:\\stext=\"(?:refs?\\.(?:\\s)?)?(?:(?:\\d+[,�\u2013\u002D])*\\d+)?\\w*?\")|(?:\\sTYPE=\"\\w+?\"))*(?:\\s?/>|>(?:(?:refs?\\.(?:\\s)?)?(?:(?:(?:\\d+(?:<IT>)?\\w?(?:</IT>)?)|(?:(?:<IT>)?\\w(?:</IT>)?[-,\u2013])|(?:(?:<IT>)?\\w(?:</IT>)?[-,\u2013]))*(?:(?:\\d+(?:<IT>)?\\w?(?:</IT>)?)|(?:(?:<IT>)?\\w?(?:</IT>)?)))?</REF>))|(?:(?i)<xref(?:\\sid=\"(?:\\w-)?\\w+?(?:\\s\\w+?)*\")?(?:\\sref-type=\"(?:aff|app|author-notes|bibr|boxed-text|chem|contrib|corresp|disp-formula|fig|fn|kwd|list|plate|scheme|sec|statement|supplementary-material|table|table-fn|other)\")?(?:\\srid=\"(?:[-\\u2013\\w])*\")?>[-\\u2013,\\d]+</xref>)(?-i))"; // (?:[-\\u2013,\\d]+)? is removed so whether problem of (31,39). becoming (.31,39) can be solved by this // (?:(?i)<xref(?:\\sid=\"(?:\\w-)?\\w+?(?:\\s\\w+?)*\")?(?: ref-type=\"aff|app|author-notes|bibr|boxed-text|chem|contrib|corresp|disp-formula|fig|fn|kwd|list|plate|scheme|sec|statement|supplementary-material|table|table-fn|other\")?(?: rid=\"(?:[-\u2013\\w])*\")?>[-\u2013,\\d]+</xref>) might have to add |(?:(?i)(<xref(\\s((id=\\d)|(ref-type=\"[a-z]+\")|(rid=[-\\w]))*)>[-,\\d]+</xref>|<xref.*/>))
        //String refSCIgeneral = "(?:(?i)(?:(?:\\d+[,\u2013])*\\d+)?(?:</IT>)?<REF(?:\\sID=\"(?:\\w-)?\\w+?(?:\\s\\w+?)*\")(?:\\stext=\"(?:refs?\\.(?:\\s)?)?(?:(?:\\d+[,\u2013\u002D])*\\d+)?\\w*?\")?(?:\\sTYPE=\"\\w+?\")?(?:\\sREFID=\"\\w+?\")?(?:\\s?/>|>(?:(?:refs?\\.(?:\\s)?)?(?:(?:(?:\\d+(?:<IT>)?(?:\\w?|(?:\\P{M}\\p{M}*)?)(?:</IT>)?)|(?:(?:<IT>)?\\w(?:</IT>)?[,-\u2013]))*(?:(?:\\d+(?:<IT>)?\\w?(?:</IT>)?)|(?:(?:<IT>)?\\w?(?:</IT>)?)))?</REF>))(?-i))";
        //String refSCIgeneral = "(?:(?i)(?:(?:\\d+[,\u2013])*\\d+)?(?:</IT>)?<REF(?:.*)?(?:\\s/>)|>(?:.*)?(?:</REF>)?)(?-i))";
        //String refSCIgeneral = "(?:(?i)(?:(?:\\d+[,\u2013])*\\d+)?(?:</IT>)?<REF(?:.+?)/>|<REF.+?>(?:(?:refs?\\.(?:\\s)?)?(?:(?:(?:\\d+(?:<IT>)?\\w?(?:</IT>)?)|(?:(?:<IT>)?\\w(?:</IT>)?[,-\u2013]))*(?:(?:\\d+(?:<IT>)?\\w?(?:</IT>)?)|(?:(?:<IT>)?\\w?(?:</IT>)?)))?</REF>)(?-i))";
        //short but hangs : (?:\\d(?:\\d*(?:<IT>)?\\w?(?:</IT>)?[,-\u2013]?)*)?
        ////System.out.println("refSCIgeneral is:" + refSCIgeneral);
        String refFootnote= "<SUP TYPE=\"FOOTNOTE_MARKER\"\\sID=\"" + allowedAttrChars + "+?\"/>";
        //String atLeastOneRefSCI = "(" + refSCIgeneral + "+)";
        String atLeastOneRefSCI = "((?:" + refSCIgeneral + "+" + "\\)?)|" + refFootnote + "|\\))"; //there may be a bracket after the reference
        // <REF TYPE="P" (text="ref. 24a")? ID="cit24a">ref. 24<IT>a</IT></REF> <-- example SCIXML
        //String referenceSCI = "(<REF (?i)TYPE=\"\\w+?\"((\\stext=\"(?:(ref\\.(\\s)?)?(?:\\d+[,\u2013])*\\d+)?\")? ID=\"\\w+(\\s\\w+)*\"(?-i))?>(?:(ref\\.(\\s)?)?(?:\\d+[,\u2013])*\\d+)?</REF>)";q
        
        String capturePunctuation = "(\\.|\\?|(?<!\\(\\w{1,15})\\!)";
        //String capturePunctuation = "((?<!\\d+)\\.(?!\\d+)|\\?|(?<!\\(\\w{1,15})\\!)";
        String abbreviations = "((?i)(\\(|\\[|\\s|>|^)(al|Am|Angew|approx|Biochim|Biophys|ca|cf|Chem|Co|conc|Dr|Drs|Corp|Ed|no|No|e\\.g|p\\.p\\.m|Engl|eq|eqns?|exp|Rs|Figs?|Labs?|Dr|etc|Calc|i\\.e|Inc|Int|Lett|Ltd|p|p\\.a|Phys|Prof|prot|refs?|Rev|sect|st|vs|(?-i)(?<!(?:</SB>|(?:\\d\\s?(<IT>?))|<IT>))(?:(?:(?:[A-Z]|[a-z])?\\.)\\s?[a-z])|(?-i)(?<!(?:</SB>|(?:\\d\\s?(<IT>?))|<IT>))(?:(?:(?:[A-Z]|[a-z])\\.)?\\s?(?:(?:[A-Z]|[a-z])\\.)?\\s?[A-Z])|(?-i)(?<!(?:</SB>|(?:\\d\\s?(<IT>?))|<IT>))(?:(?:(?:[A-Z]|[a-z])\\.)?\\s?(?:(?:[A-Z]|[a-z])\\.)\\s?[a-z])|(?-i)(?<=(?:(?<!(?:</SB>|(?:\\d)))(?:(?:\\s|\\(|^)<IT>)))(?:\\s?\\w{1,10})|\\s?\\.\\s?\\.\\s?|\\())";//(?-i)(?<=(?:(?<!(?:</SB>|(?:\\d)))(?:(?:\\s|\\(|^)<IT>)))(?:\\s?\\w{1,10}) is added on 23-11-10 by shs to solve the problem of over splitting " from <IT>A. vinelandii</IT>" it was splitted after A.//[U.S.|U.s.|u.s. all are accepted but not 5 p.m. or ]// do not make second [a-z] or [A-Z] optional it still work for <bold>.</bold>//"((?i)(\\(|\\[|\\s|>)(al|Am|Angew|approx|Biochim|Biophys|ca|cf|Chem|Co|conc|Dr|Ed|e\\.g|Engl|eq|eqns?|exp|etc|Figs?|i\\.e|Inc|Int|Lett|Ltd|p|p\\.a|Phys|Prof|prot|refs?|Rev|sect|st|vs|(?-i)(?<!(?:</SB>|(?:\\d\\s?(?:<IT>?|<bold>?|<named-content>?|<italic>?|<B>?))|(?:<IT>|<bold>|<named-content>|<italic>|<B>))(?:[A-Z]?(?:\\.?\\s?[a-z]?)))))"; // made [A-Z] optional. so that <bold>.</bold> is excepted.
        
        //String abbreviations = "((?i)(\\(|\\[|\\s|>)(al|Am|Angew|approx|Biochim|Biophys|ca|cf|Chem|Co|conc|Dr|Ed|e\\.g|Engl|eq|eqns?|exp|Figs?|i\\.e|Inc|Int|Lett|Ltd|p|p\\.a|Phys|Prof|prot|refs?|Rev|sect|st|vs|(?-i)(?<!(?:</SB>|(?:\\d\\s?(<IT>?|<bold>?|<named-content>?|<italic>?|<B>?))|<IT>|<bold>|<named-content>|<italic>|<B>))(?:[A-Z])))";//\\.?\\s?[a-z]?)))";//"((?i)(\\(|\\[|\\s|>)(al|Am|Angew|approx|Biochim|Biophys|ca|cf|Chem|Co|conc|Dr|Ed|e\\.g|Engl|eq|eqns?|exp|etc|Figs?|i\\.e|Inc|Int|Lett|Ltd|p|p\\.a|Phys|Prof|prot|refs?|Rev|sect|st|vs|(?-i)(?<!(?:</SB>|(?:\\d\\s?(?:<IT>?|<bold>?|<named-content>?|<italic>?|<B>?))|(?:<IT>|<bold>|<named-content>|<italic>|<B>))(?:[A-Z]?(?:\\.?\\s?[a-z]?)))))"; // made [A-Z] optional. so that <bold>.</bold> is excepted.
        
        // moving all references inside the punctuation so that the sentence splitting is easier
        //changed on 22-12-10 by shyama
        Pattern refSentence = Pattern.compile("(.*?)" +  capturePunctuation + atLeastOneRefSCI,Pattern.CASE_INSENSITIVE);//shs
        //wrong  Pattern refSentence = Pattern.compile("(.*?)" +capturePunctuation + "(?!\\d+)"+ atLeastOneRefSCI,Pattern.CASE_INSENSITIVE);
     // $ should be optional coz abbreviation may or may not be at the end of sentence. also made </IT>? -> (?:</IT>)? on 28/03/11 it solved the problem of any abbreviation before ) i.e. Inc.) was becoming Inc). // keep this otherwise if a snetence end with abbreviation, it does not split the sentence.
        //02-06-2011
        //$ should be not be optional , coz here we want to check whether a is ending with an abbreviation, also made </IT>? -> (?:</IT>)? on 28/03/11 it solved the problem of any abbreviation before ) i.e. Inc.) was becoming Inc). // keep this otherwise if a snetence end with abbreviation, it does not split the sentence.
        
        Pattern abbrevs = Pattern.compile(".*?(" + abbreviations + "(?:</IT>)?)" + "$",Pattern.CASE_INSENSITIVE); 
        //Pattern abbrevs = Pattern.compile(".*?(" + abbreviations + "(</IT>)?)" + "$",Pattern.CASE_INSENSITIVE);//shs bracket added with </IT> otherwise only > is being optional // 
        //Pattern abbrevs = Pattern.compile(".*?(" + abbreviations + "(?:</IT>)?)" + "$",Pattern.CASE_INSENSITIVE);//shs
        //System.out.println("resSentence is" + refSentence);
        Matcher refm = refSentence.matcher(clearString);
        StringBuffer swappedString = new StringBuffer();
        //System.out.println("going for refm while loop");
        while (refm.find()) {
        		//System.out.println("in refm");
                String a = refm.group(1); //sentence
                String b = refm.group(2); //punctuation
                String c = refm.group(3); //reference
                //System.out.printf("a: %s\n b: %s\n c: %s\n",a,b,c);//shs
                Matcher abbrevm=abbrevs.matcher(a);
                //System.out.println("group a :"+a);
                //System.out.println("abbrevm :"+abbrevs);
                //if (Pattern.matches("al</IT>?$",a)){
                if (abbrevm.find()){
                    String ab = abbrevm.group(1);
                	//System.out.println("String" + " ends in an abbreviation: " + ab);//shs
                	swappedString.append(a); // don't change order
                	swappedString.append(b);
                	swappedString.append(c);
                }else{
                	//System.out.println("in refm else");
                	//System.out.println("last char of a"+a.toCharArray()[a.length()-1]+"\t start of c"+c.toCharArray()[0]);
                	//added on 22-12-10 	
                	if((a.endsWith("0")||a.endsWith("1")||a.endsWith("2")||a.endsWith("3")||a.endsWith("4")||a.endsWith("5")||a.endsWith("6")||a.endsWith("7")||a.endsWith("8")||a.endsWith("9"))&&(c.startsWith("1")||c.startsWith("2")||c.startsWith("3")||c.startsWith("4")||c.startsWith("5")||c.startsWith("6")||c.startsWith("7")||c.startsWith("8")||c.startsWith("9"))&&b.equals(".")) 
                	{
                		//System.out.println("a ends with number and c starts with number, in character by charact comparison");
                    	swappedString.append(a); // don't change order
                       	swappedString.append(b);
                       	swappedString.append(c);
                	}
                	else
                    {
                    	swappedString.append(a); //sentence
                    	swappedString.append(c); //reference or bracket
                    	swappedString.append(b); //punctuation
                    }

                	
               }
                
        }
        ////System.out.println("got out of the while loop");
        // anything after the last swapped reference
        String endbit = clearString.substring(swappedString.length(),
                        clearString.length());
        swappedString.append(endbit);
        clearString = swappedString.toString();
        clearString = clearString.replaceAll(">\\.<", ">\\. <"); // 29/3/09 added 
        ////System.out.println("ClearString: " + clearString);

        
        String capitals = "[A-Z0-9]"; //caps and numbers may begin a sentence
        String punctuation = "(?:\\.|\\?|(?<!\\(\\w{1,15})\\!)"; // .?!     "(?:\\.|\\?|(?<!\\(\\w{1,15}))\\!|\\:(?=<list.+>))" 
      
        String optPunctuation = punctuation + "??";
        String endEquation = "</EQN>";
        //String endPara1 = "(</P>|</ABSTRACT>)";
        String endPara = "(</P>|</ABSTRACT>|</list>)";//shs
        String beginPara = "<P>";
        //String notFollowFigTab = "(?!(<fig)|(<table-wrap))";
        String optStartQuote = "['\"\u201C]?";// '"
        String optCloseQuote = "['\"\u201D]?"; // '"
        String optReferenceSCI = refSCIgeneral + "*";
        //String beginFirstSentence = "(^<ABSTRACT>(<P>)?)";
        //String beginFirstSentence; 
        //if(sid==2&&flagAbs==1)
        	//beginFirstSentence = "((^(<ABSTRACT>)(<P>)?(<SEC.+?>)?)|(^(<ABSTRACT>)(<P>))|(^(<ABSTRACT>)(<P.+?>)?)|(^(<abstract.+?>)(<p.+?>)?(<sec.+?>)?))";
        //else
        	//beginFirstSentence = "(^(<BODY>)(<SEC.+?>)?(<P>)?)";
        String beginFirstSentence = "^";
        String endLastSentence = "$";
        String openHeader = "(<HEADER(\\sHEADER_MARKER=\""+ allowedAttrChars + "+?\")?>|<HEADER/>|<TITLE>|<TITLE/>)"; //shs
        String wholeHeader = "((<BODY>)?(<DIV(\\sDEPTH=\"\\d+\")?>)?(<HEADER(\\sHEADER_MARKER=\"" + allowedAttrChars + "+?\")?>.*?</HEADER>|<HEADER/>)|<TITLE>)";               
        String optOpenHeader = openHeader + "?";
        
        /*
        Pattern testP = Pattern.compile(endPara,Pattern.CASE_INSENSITIVE);
        Matcher testM = testP.matcher(clearString);
        if(testM.find())
        	System.err.println("\n\n\n fig or table found : \n"+testM.group()+"\n\n");
        else
        	System.err.println("\n\n\n fig or table not found : \n\n\n");*/
        
        //String notFollowedBy = "(?!(</caption>))"; //shs
        //String notPrecededBy = "(?<!(<label>(.+?)</label><caption>))<P>"; //shs
        
        String eqn = "<EQN(\\sID=\"" + allowedAttrChars + "+?\")?(\\sTYPE=\"" + allowedAttrChars + "+?\")?>";
        String xref = "<XREF(\\sID=\"" + allowedAttrChars + "+?\")?(\\sTYPE=\"" + allowedAttrChars + "+?\")?>";
        String listTag = "<list.+?>"; //13/10/09
        //String manyStartTags = "(" + eqn + "|" + xref + "|<BODY>|<DIV(\\sDEPTH=\"\\d+\")?>|<P>|<B>|<IT>)*";
        String manyStartTags = "(" + eqn + "|" + xref +"|"+listTag + "|<BODY>|<DIV(\\sDEPTH=\"\\d+\")?>|<P>|<p.+?>|<SEC.+?>|<disp-quote>|<supplementary-material.+?>|<boxed-text.+?>|<list list-type=\"\\w{2,20}\">|<list-item>|<ABSTRACT>|<abstract.+>|<statement>|<def>)*";//shs listTag on 13/10/09, <ABSTRACT>|<abstract.+> on 09/11/09
        //String atLeastOneStartTag = "(<IT>|" + eqn + "|" + xref + "|<BODY>|<DIV(\\sDEPTH=\"\\d+\")?>|<P>)+";
        //String optEndTags = "(</XREF>|</BODY>|</DIV>|</P>|</ABSTRACT>|</HEADER>|<HEADER/>|</SEC>|</TITLE>|</boxed-text>|</list>|</list-item>|</statement>)?"; //shs
        String optEndTags = "(</XREF>|</HEADER>|<HEADER/>|</TITLE>|</boxed-text>|</list>|</list-item>|</statement>)?"; //shs
        // <list.+?> added to optEndTags1
        String optEndTags1 = "(</XREF>|</HEADER>|<HEADER/>|</TITLE>|</boxed-text>|<list.+?>|</list>|</list-item>|</statement>|</inline-supplementary-material>|<inline-supplementary-material/>|</related-article>|</related-object>|</address>|</alternatives>|</array>|</boxed-text>|</chem-struct-wrap>|</fig>|</fig-group>|<graphic.+?/>|</media>|</preformat>|</supplementary-material>|</table-wrap>|</table-wrap-group>|</disp-formula>|</disp-formula-group>|</element-citation>|</mixed-citation>|</nlm-citation>|</bold>|</italic>|</monospace>|</overline>|</overline-start>|</overline-end>|</roman>|</sans-serif>|</sc>|</strike>|</underline>|</underline-start>|</underline-end>|</award-id>|</funding-source>|</open-access>|</chem-struct>|<inline-formula/>|<inline-graphic/> |</private-char>|</def-list>|</list>|</tex-math>|</mml:math>|</abbrev>|</milestone-end>|</milestone-start>|</named-content>|</styled-content>|</ack> |</disp-quote>|</speech>|</statement>|</verse-group>|</fn>|</target>|</xref>|</ref>|</sub>|</sup>|</def>)*"; //shs
        		// </P> added on 23-11-10 by shs
        String endTags = "(</P>|</IT>|</italic>|</EQN>|</XREF></bold>|</NAMED-CONTENT>|<disp-formula>|</HEADER>|<HEADER/>|</TITLE>|</disp-quote>|</supplementary-material>|</boxed-text>|</list>|</list-item>|</statement>)"; //shs
        String manyEndTags = endTags + "*";
        //String sentenceTerminator = "(?>" +endPara+ "|"+ endEquation +"|" + "(?<!(\\s|>)refs?)"+punctuation+")";
        String endParaOrEq = "(" + endPara+"|" + endEquation + ")\\s?"; //shs notFollowedBy added
        //String puncNoRef = "(?<!(\\s|>)refs?)"+punctuation + "\\s";
        //String abbreviations = "((?i)(\\(|\\s|>)(refs?|Figs?|vs|Prof|Dr|conc|e\\.g|i\\.e|prot|st|cf|exp|eqns?|Inc|Ltd|Co)(?-i))";
        String formatting="(<B>|<IT>|<SP>|<italic>|<BOLD>|<disp-formula>|<named-content.+?>)"; //shs 
        
        String puncNoAbbrv = "(?<!" + abbreviations + "(</IT>)?)"+ punctuation + "\\s"; // (\\b\\w+\\b)? added on 23-11-10 to solve over splitting , see above//"(\\s|\\s?(?=" + formatting +"))"; //29/3/09 made the \s optional if followed by formatting //String puncNoAbbrv = "(?<!" + abbreviations + "(</IT>)?)"+ punctuation + "\\s"; //"(\\s|\\s?(?=" + formatting +"))"; //29/3/09 made the \s optional if followed by formatting
        //?> gives priority to para and equations so that they are treated first before resorting to simple punctuation
        //String sentenceTerminator = "(?>" + endParaOrEq + "|" + puncNoAbbrv + ")";
        String greekLetters = "[\u0370-\u03FF\u1F00-\u1FFF]";
        String pAttr = "<p.+?>";
        String sentenceCommencer = "(?>" +beginPara + "|" + pAttr +"|"+ "Fig(s)?\\." + "|" + capitals + "|" + formatting + "|" + "\\[|\\(|"+greekLetters+"|\u007C)";
        String equationCommencer = "(" + eqn + ".)";
        String commencer = "(" + sentenceCommencer + "|" + equationCommencer + ")";
        // For matching the beginning of the next sentence
        // ((space|(space?(starttag+|<HEADER>)))starttag*<HEADER>?\"?caps|para|fig)
        //String beginSentenceLookahead = "((\\s|(\\s?(" + atLeastOneStartTag
         //               + "|" + openHeader + ")))" + manyStartTags + optOpenHeader
         //               + optStartQuote + sentenceCommencer + ")";
        
        String noSpaceReqLookahead =  manyStartTags + optOpenHeader + optStartQuote + commencer;
        
        String nocapsParaLookAhead  = "(\\s?<P>)";
        
        String startSentence = manyStartTags + optStartQuote + commencer;
        
        // For matching the end of the previous sentence
        String sentenceFigLookbehind = "(?<=(?<!"+ abbreviations + punctuation + ")((" + endParaOrEq + ")|("+ puncNoAbbrv + ")|("
        + optPunctuation + optEndTags + endTags + "\\s?)))";
        
        //for matching the start of a sentence following a header
        String headerLookahead = "(?=(?:" + manyStartTags + optOpenHeader
                        + optStartQuote + commencer + "))";
        //(Headerstuff | ((normal sentence | firstsentence) sentenceContent, (punctuation|endEquation), optionalEndings, lookahead))
        //String figLookAhead = "";
        String Figure="<fig.+?</fig>";
        String tableWrap = "<table-wrap.+?</table-wrap>";
        String title = "((?:<title/>)|(?:<title.+?</title>))";//"<title.+?</title>";
        //String absBodyLookBehind = "((?:<abstract>)|(?:<abstract.+?>)|(?:<body>))";
        String secLookBehind = "((?:<SEC>)|(?:<SEC.+?>))?"; // <sec> can be followed by<body>.
        String supplimentbehind = "<supplementary-material.+?</supplementary-material>";
        String refList = "<ref-list.+?</ref-list>";
        String boxed = "(?:<boxed-text.+?>)(?:<caption>)?";
        
        //String list = "<list.+?</list>";
        //String beginPAttr = "<p.+?>";
        Pattern sentence = Pattern.compile(
        		//"(" + sentenceFigLookbehind + absBodyLookBehind + title + secLookBehind + title +")|"+
        		//"(" + sentenceFigLookbehind + absBodyLookBehind + secLookBehind + title + ")|"+
        		//"(" + absBodyLookBehind + secLookBehind + title + ")|"+
        		"(" + sentenceFigLookbehind + "(" +secLookBehind + title +")+"+")|"+ // made (secLookBehind + titile)+ on 09/11/09.
        		"("+ sentenceFigLookbehind +"("+ boxed + secLookBehind + title +"?)"+optEndTags1+")|"+
        		"(" + sentenceFigLookbehind + wholeHeader + headerLookahead + 
        			//lookbehind and start of a normal sentence, or a match for the first sentence (at the beginning of the abstract)
        			")|" +
        			 "(" + sentenceFigLookbehind + "((("+ tableWrap+")+("+Figure +")+)|(("+ Figure +")+("+ tableWrap +")+)|("+tableWrap +")+|("+ Figure+")+)" + optEndTags+")|"
        			 +"("+ sentenceFigLookbehind + "((("+supplimentbehind +")+"+ optEndTags+")|(("+supplimentbehind +")+"+secLookBehind+title+")))|" //manystarttags added on 06/11/09 by shs
        			+ "("+ sentenceFigLookbehind + "("+ refList +")+"+optEndTags1+")|"
        			 +"(((" + sentenceFigLookbehind +""+ startSentence + 
        				")|" + beginFirstSentence + "|" + beginPara + ")" +
                    // The sentence content
        			"(.*?)(Fig(s)?\\..+?)*?" +
                    // punctuation that ends a sentence. Give prioriy to endEquation then puncNoRef
        			"(((?<!(" + endEquation + "\\s?|" + puncNoAbbrv + "\\s?|" + endPara + "\\s?))" 
        			    + "(?=(?:"  + nocapsParaLookAhead + ")))|" +
			   
			        "((?>" + endEquation + "\\s?|" + puncNoAbbrv + "\\s?|" + endPara + "\\s?)"
					+ optCloseQuote	+ optReferenceSCI + manyEndTags + "\\s?"//optReferenceSCI to optReferenceSCI* 
					+ "(?=(?:" + noSpaceReqLookahead + "|" + nocapsParaLookAhead + "|\\n|\\s*$)))|"+endLastSentence+"))"
        			
        		
        							
                    // lookahead to beginning of next sentence
        			// end of line or end of whole string
        ,Pattern.CASE_INSENSITIVE);//shs
        
        ////System.out.println("Sentence Pattern: " + sentence + "\n\n");
        Matcher m = sentence.matcher(clearString);
        ArrayList<StringBuffer> sentences = new ArrayList<StringBuffer>();
        
        int somethingFound = 0;
        // This bit splits the sentences
        while (m.find()) {
        		somethingFound = 1;
                sentences.add(new StringBuffer(m.group()));
                ////System.out.println(m.group());
        }
        if(somethingFound == 0) {
        	//System.out.println("No sentences matched");
        	
        }
        Pattern refSentenceRev = Pattern.compile("(.*?)" + atLeastOneRefSCI
                        + capturePunctuation + "(\\s?(?:</P>)?)\\Z",Pattern.CASE_INSENSITIVE);//shs
        //System.out.println("reversal pattern: "+ refSentenceRev.toString());
        int count = 0;
        
        ArrayList<StringBuffer> newSentences = new ArrayList<StringBuffer>();
        // this adds the paper title to the ArrayList of sentences
       
        //System.out.println("size of sentences:"+sentences.size());
        for (StringBuffer s : sentences) {
                //System.out.println(count + ": "+  s + "\n");
                Matcher refmRev = refSentenceRev.matcher(s);
                //System.out.println("refSentenceRev:"+refSentenceRev);
                // if sentence finishes with reference + punctuation, swap the two over
                if (refmRev.find()) {
                		//System.out.println("ref found");
                        String a = refmRev.group(1); //sentence
                        String b = refmRev.group(2); //reference or bracket or both
                        
                        String c = refmRev.group(3); //punctuation
                        String d = refmRev.group(4); //space and/or </P>
                        //System.out.printf("sentence "+count+": %s\n A: %s\n B: %s\n C: %s\n", s, a,b,c);
                        StringBuffer ns = new StringBuffer();
                        //if (b.equals(")")) {
                        if (b.endsWith(")")) { // made it endsWith instead of equals on 28/03/11 coz if reference is within bracket we do not want to swap punctuation, it worked, 31,39). is no longer becoming 31,.39) , why square bracket is not considered in bracket?????
                        	//System.out.println("b ends with )");
                        ns.append(a); //sentence
                        ns.append(b); //bracket
                        ns.append(c); //punctuation
                        ns.append(d); //space
                        } else{
                        	//System.out.println("b does not end with )");
                        	if(!b.startsWith("<"))
                            {
                            	int index=b.indexOf("<");
                            	//System.out.println("index:"+index);
                            	String b1=b.substring(0, index); // end index exclusive
                            	//System.out.println("B1:"+b1);
                            	//System.out.println("b at 0th position"+b.toCharArray()[0]);
                            	String b2=b.substring(index);
                            	a=a.concat(b1);
                            	b=b2;
                            }
                        	ns.append(a); //sentence
                            ns.append(c); //punctuation
                            ns.append(b); //reference
                            ns.append(d); //space
                        	
                        }
                        //System.out.printf("sentence "+count+": %s\n A: %s\n B: %s\n C: %s\n", s, a,b,c);
                        newSentences.add(ns);
                        
                        ////System.out.println("Sentence found: " + count);
                        
                } else {
                	//System.out.println("sentence added s:"+s);
                	newSentences.add(s);
                }
                //System.out.println("not if nor else : count="+count);
                count++;
        }
        //System.out.println("outside for");
        sentences = newSentences;
        // Post-processing sentence array to move XML tags outside the sentences
        // String ppSentenceTag = "(<s sid=\"\\d+\">)";
        String ppStartTags = "((?:<ABSTRACT>|<BODY>|<SEC(?:.+?)>|<DIV(\\sDEPTH=\"\\d+\")?>|<P>|<P.+>|<disp-quote>|<list.+?>|<list-item>|<abstract.+?>|<statement>)*)"; // added overall brackets and ?: 15/6/09 mal //shs <sec> <abstract.+?>
        String ppSentence = "(.+?)";
        String ppEndTags = "((?:</ABSTRACT>|</BODY>|</SEC>|</DIV>|</P>|</disp-quote>|</list>|</list-item>|</boxed-text>|</statement>|<list.+?>|<list-item>)*\\s?)\\Z";
       
        Pattern pp = Pattern.compile(ppStartTags + ppSentence + ppEndTags,Pattern.CASE_INSENSITIVE);//shs
        Pattern ppHeader = Pattern.compile(".*?<HEADER.+?",Pattern.CASE_INSENSITIVE);//shs
        Pattern ppTitle = Pattern.compile(".*?<TITLE.+?>",Pattern.CASE_INSENSITIVE); //shs
        Pattern ppFig = Pattern.compile("<fig.+?>|<table-wrap.+?>",Pattern.CASE_INSENSITIVE); //shs
        Pattern ppCap = Pattern.compile("</caption.+?>|</fn.+?>",Pattern.CASE_INSENSITIVE); //shs comment : seems it can't find the tag without .+?
        Pattern paraAttr = Pattern.compile("<abstract><p.+></p>",Pattern.CASE_INSENSITIVE);
        Pattern suppli = Pattern.compile("<supplementary-material.+?>",Pattern.CASE_INSENSITIVE);
        Pattern named = Pattern.compile("<named-content.+?>", Pattern.CASE_INSENSITIVE);
        
        int id = sid;
	// Vector<Element> allSentences = new Vector<Element>();
        //System.out.println("before sentences loop.");
        for (StringBuffer s : sentences) {
                Matcher ppm = pp.matcher(s);
                if (ppm.matches()) {
                        ////System.out.println("Sentence " + id+ " matches the post- processing tags");
                        String one = "";
                        if (ppm.group(1) != null)
                                one = ppm.group(1);
                        String two = ppm.group(3);
                     
                        String three = "";
                        if (ppm.group(4) != null)
                                three = ppm.group(4);
                        
                        //System.out.println("Group count:"+ppm.groupCount()+"\nSent id is: " + id+ " Group 1 is: " + ppm.group(1) + " Group 2 is: " + ppm.group(2) + "Group 3 is: " +ppm.group(3) + "Group 4 is: " + ppm.group(4));
                        
                        Matcher mHead = ppHeader.matcher(s);
                        Matcher mTitle = ppTitle.matcher(s);
                        Matcher mfig = ppFig.matcher(s);
                        Matcher mCap = ppCap.matcher(s);
                        Matcher mParaAttr = paraAttr.matcher(s);
                        Matcher mSuppli = suppli.matcher(s);
                        Matcher mNamed = named.matcher(s);
                        
            			//s.insertChild(titleNodes.get(titleNodes.size()-1).getValue(), 0);
            			
                        if (!(mHead.matches()||mTitle.matches()||mfig.matches()||mCap.matches()||mParaAttr.matches()|mSuppli.matches())) //{			//shs
                        {/*
                        	Element sElement = new Element("s");
                        	String sId = String.valueOf(id);
                			sElement.addAttribute(new Attribute("sid",sId));
                			Pattern p = Pattern.compile("<(.+?)\\s?(.+?)?>(.+?)</\\1>");
                			Matcher mp = p.matcher(two);
                			while(mp.find())
                			{
                				
                			}
                			
                			sElement.insertChild(two,0);
                			allSentences.add(sElement);*/
                        	nsentences.add(new StringBuffer(one + "<s sid=\"" + id
                                                + "\">" + two + "</s>" + three));
                                ////System.out.println("Sentence " + id + ": " + s);
                        	//System.out.println("after s tag:"+one + "<s sid=\"" + id+ "\">" + two + "</s>" + three);
                                id++;
                        } else {
                                // this is a header, mHead matches
                        	//System.out.println("\n\n\nHeader : "+s+"\n\n ");
                                nsentences.add(s);
                        }
                } else {
                        System.out.println("Sentence " + id + "-- " + s + " -- didn't match!");
                }
        }
       
        
        int countme = 0;
        for (StringBuffer s : nsentences) {
        		countme++;
                ////System.out.println("Appending sentence " + countme + ":\n" + s);
                finalbuffer.append(s);
        }

        String string = finalbuffer.toString();
        ////System.out.println("before return clearString :"+string+"\n\n final buffer"+finalbuffer);
        StringInt stringInt = new StringInt(string,id);//,allSentences);
        // fileString.replaceAll("<ABSTRACT>.+?</BODY>",
        // finalbuffer.toString());
        
        
        //bit of a hack here to get open Ps back in
       // fileString = fileString.replaceAll("</P><s", "</P><P><s");
        
        return stringInt;
	}
	public static String getString(Node node)
    {
	try {
            Source source = new DOMSource(node);
            StringWriter stringWriter = new StringWriter();
            Result result = new StreamResult(stringWriter);
            TransformerFactory tfactory = TransformerFactory.newInstance();
            Transformer transformer = tfactory.newTransformer();
            transformer.setOutputProperty(javax.xml.transform.OutputKeys.ENCODING, "UTF-8");
            //transformer.setOutputProperty(javax.xml.transform.OutputKeys.METHOD, "text");
	    //transformer.setParameter("{http://www.w3.org/1999/xlink}xlink",);
            transformer.transform(source, result);
	    //System.out.println("File"+stringWriter.getBuffer().toString());
	    	return stringWriter.getBuffer().toString();
        } catch (TransformerConfigurationException e) {
            e.printStackTrace();
        } catch (TransformerException e) {
            e.printStackTrace();
	    }
        return null;
    }
	public static NodeInt callSentenceSplitter(Document paperDoc, Node subroot,NodeList childNodesold, int id) throws Exception
	{
	    //System.out.println("in call Sentence id is "+id);
	    NodeInt paperId = new NodeInt(subroot,id);
	    NodeList childNodes = subroot.getChildNodes();
		if(childNodes!=null&&childNodes.getLength()!=0)
		{
			for(int i=0; i<childNodes.getLength(); i++)
			{
			    //System.out.println("in for loop child is "+childNodes.item(i).getNodeName());

				if(childNodes.item(i).getNodeName().equalsIgnoreCase("sec")||childNodes.item(i).getNodeName().equalsIgnoreCase("statement")||childNodes.item(i).getNodeName().equalsIgnoreCase("DIV")||childNodes.item(i).getNodeName().equalsIgnoreCase("boxed-text")||childNodes.item(i).getNodeName().equalsIgnoreCase("list")||childNodes.item(i).getNodeName().equalsIgnoreCase("list-item")||childNodes.item(i).getNodeName().equalsIgnoreCase("disp-quote")||childNodes.item(i).getNodeName().equalsIgnoreCase("speech")||childNodes.item(i).getNodeName().equalsIgnoreCase("fn-group")||childNodes.item(i).getNodeName().equalsIgnoreCase("fn")||childNodes.item(i).getNodeName().equalsIgnoreCase("def-list")||childNodes.item(i).getNodeName().equalsIgnoreCase("def-item")||childNodes.item(i).getNodeName().equalsIgnoreCase("def"))
				{
					NodeList grandNodes = childNodes.item(i).getChildNodes();
					//System.out.println("in sec, going to call callsentenceSplitter again. id is "+id);
					paperId = callSentenceSplitter(paperDoc,childNodes.item(i),grandNodes,id);
					id = paperId.id;
					subroot.replaceChild(paperId.node,childNodes.item(i));
					paperId.setNode(subroot);
					//paperDoc = paperId.node;
					
				}
				else
				if(childNodes.item(i).getNodeName().equalsIgnoreCase("p"))//||childNodes.item(i).getNodeName().equals("#text"))
				{
				    //System.out.println("in p");
				    //NodeList extLink = ((Element)childNodes.item(i)).getElementsByTagName("ext-link");
				    NodeList graphic = ((Element)childNodes.item(i)).getElementsByTagName("graphic");
				    NodeList xlink = ((Element)childNodes.item(i)).getElementsByTagNameNS("*", "*");//((Element)childNodes.item(i)).getElementsByTagName("inline-graphic");
				    NodeList childrenOfP = ((Element)childNodes.item(i)).getChildNodes();
				   /* if(extLink!=null&&extLink.getLength()!=0)
					{
					    for(int s = 0; s<extLink.getLength(); s++)
						{
						    if(((Element)extLink.item(s)).hasAttribute("xlink:href"))
						    	//System.out.println("xlink is there"+((Element)extLink.item(s)).lookupNamespaceURI("xlink"));
						    ((Element)extLink.item(s)).setAttributeNS("http://www.w3.org/1999/xlink","xlink:href",((Element)extLink.item(s)).getAttributeNode("xlink:href").getNodeValue());
						}
					}*/
				    if(graphic!=null&&graphic.getLength()!=0)
					{
					    for(int s = 0; s<graphic.getLength(); s++)
						{
						    //((Element)graphic.item(s)).setAttributeNS("http://www.w3.org/1999/xlink","xlink:href","http://www.ncbi.nlm.nih.gov/");
						    if(((Element)graphic.item(s)).hasAttribute("xlink:href"))
						    	//System.out.println("graphic xlink:");
						    graphic.item(s).getParentNode().removeChild(graphic.item(s));
						}
					}
				    if(xlink!=null&&xlink.getLength()!=0)
					{
					    for(int s = 0; s<xlink.getLength(); s++)
						{
						    //((Element)graphic.item(s)).setAttributeNS("http://www.w3.org/1999/xlink","xlink:href","http://www.ncbi.nlm.nih.gov/");
						    if(((Element)xlink.item(s)).hasAttribute("xlink:href"))
						    {	
						    	//System.out.println("xlink node:"+xlink.item(s).getNodeName()+"attr value :"+((Attr)((Element)xlink.item(s)).getAttributeNode("xlink:href")).getNodeValue());
						    	((Element)xlink.item(s)).setAttributeNS("http://www.w3.org/1999/xlink","xlink:href",((Element)xlink.item(s)).getAttributeNode("xlink:href").getNodeValue());
						    //xlink.item(s).getParentNode().removeChild(xlink.item(s));
						    }
						    if(((Element)xlink.item(s)).hasAttribute("xlink:type"))
						    {	
						    	//System.out.println("xlink node:"+xlink.item(s).getNodeName()+"attr value :"+((Attr)((Element)xlink.item(s)).getAttributeNode("xlink:type")).getNodeValue());
						    	((Element)xlink.item(s)).setAttributeNS("http://www.w3.org/1999/xlink","xlink:type",((Element)xlink.item(s)).getAttributeNode("xlink:type").getNodeValue());
						    //xlink.item(s).getParentNode().removeChild(xlink.item(s));
						    }
						    if(((Element)xlink.item(s)).hasAttribute("xlink:role"))
						    {	
						    	//System.out.println("xlink node:"+xlink.item(s).getNodeName()+"attr value :"+((Attr)((Element)xlink.item(s)).getAttributeNode("xlink:role")).getNodeValue());
						    	((Element)xlink.item(s)).setAttributeNS("http://www.w3.org/1999/xlink","xlink:role",((Element)xlink.item(s)).getAttributeNode("xlink:role").getNodeValue());
						    //xlink.item(s).getParentNode().removeChild(xlink.item(s));
						    }
						    if(((Element)xlink.item(s)).hasAttribute("xlink:title"))
						    {	
						    	//System.out.println("xlink node:"+xlink.item(s).getNodeName()+"attr value :"+((Attr)((Element)xlink.item(s)).getAttributeNode("xlink:title")).getNodeValue());
						    	((Element)xlink.item(s)).setAttributeNS("http://www.w3.org/1999/xlink","xlink:title",((Element)xlink.item(s)).getAttributeNode("xlink:title").getNodeValue());
						    //xlink.item(s).getParentNode().removeChild(xlink.item(s));
						    }
						    if(((Element)xlink.item(s)).hasAttribute("xlink:show"))
						    {	
						    	//System.out.println("xlink node:"+xlink.item(s).getNodeName()+"attr value :"+((Attr)((Element)xlink.item(s)).getAttributeNode("xlink:show")).getNodeValue());
						    	((Element)xlink.item(s)).setAttributeNS("http://www.w3.org/1999/xlink","xlink:show",((Element)xlink.item(s)).getAttributeNode("xlink:show").getNodeValue());
						    //xlink.item(s).getParentNode().removeChild(xlink.item(s));
						    }
						    if(((Element)xlink.item(s)).hasAttribute("xlink:actuate"))
						    {	
						    	//System.out.println("xlink node:"+xlink.item(s).getNodeName()+"attr value :"+((Attr)((Element)xlink.item(s)).getAttributeNode("xlink:actuate")).getNodeValue());
						    	((Element)xlink.item(s)).setAttributeNS("http://www.w3.org/1999/xlink","xlink:actuate",((Element)xlink.item(s)).getAttributeNode("xlink:actuate").getNodeValue());
						    //xlink.item(s).getParentNode().removeChild(xlink.item(s));
						    }
						    if(((Element)xlink.item(s)).hasAttribute("mml:math"))
						    {	
						    	//System.out.println("mml node:"+xlink.item(s).getNodeName()+"attr value :"+((Attr)((Element)xlink.item(s)).getAttributeNode("mml:math")).getNodeValue());
						    	((Element)xlink.item(s)).setAttributeNS("http://www.w3.org/1998/Math/MathML","mml:math",((Element)xlink.item(s)).getAttributeNode("mml:math").getNodeValue());
						    //xlink.item(s).getParentNode().removeChild(xlink.item(s));
						    }
						}
					}
				    if(childrenOfP.getLength()==1&&!(childrenOfP.item(0).getNodeName().equals("#text"))&&(((Element)childrenOfP.item(0)).getNodeName().equalsIgnoreCase("ext-link")||((Element)childrenOfP.item(0)).getNodeName().equalsIgnoreCase("e-mail")||((Element)childrenOfP.item(0)).getNodeName().equalsIgnoreCase("uri")||((Element)childrenOfP.item(0)).getNodeName().equalsIgnoreCase("inline-supplementary-material")||((Element)childrenOfP.item(0)).getNodeName().equalsIgnoreCase("related-article")||((Element)childrenOfP.item(0)).getNodeName().equalsIgnoreCase("related-object")||((Element)childrenOfP.item(0)).getNodeName().equalsIgnoreCase("address")||((Element)childrenOfP.item(0)).getNodeName().equalsIgnoreCase("alternatives")||((Element)childrenOfP.item(0)).getNodeName().equalsIgnoreCase("array")||((Element)childrenOfP.item(0)).getNodeName().equalsIgnoreCase("funding-source")||((Element)childrenOfP.item(0)).getNodeName().equalsIgnoreCase("inline-graphic"))) 
				    {}	
				    else
				    {
				    	String tobeSplitorg = getString(childNodes.item(i));
				    	////System.out.println("Before calling sentencesplit:tobeSplitorg:"+tobeSplitorg);
				    	tobeSplitorg = tobeSplitorg.replaceFirst("<\\?xml.+?>","");
				    	//tobeSplit = tobeSplit.replaceFirst("<p.+?>", replacement)
				    	Pattern para = Pattern.compile("<p>|<p.+?>", Pattern.CASE_INSENSITIVE);
				    	Matcher mpara = para.matcher(tobeSplitorg);
						if(mpara.find())
						{
							//System.out.println("p found");
							Pattern cpara = Pattern.compile("</p>", Pattern.CASE_INSENSITIVE);
					    	Matcher cmpara = cpara.matcher(tobeSplitorg);
					    	
							String tobeSplit = mpara.replaceFirst("");
							if(cmpara.find())
					    	{
								tobeSplit = tobeSplit.substring(0, tobeSplit.length()-4);
					    	}
							//System.out.println("Before calling sentencesplit:tobeSplit:"+tobeSplit);
							StringInt strInt = sentenceSplit(tobeSplit,id);
							
							String split = strInt.sTags;
							split = split.concat(tobeSplitorg.substring(tobeSplitorg.length()-4,tobeSplitorg.length()));
							split = mpara.group().concat(split);
							//System.out.println("mapara group : "+mpara.group()+"\t id = "+id+"\nbefore making doc, split is:\n\n"+split);
							//DocumentFragment dfp = paperDoc.getDocumentFragment();
							try
							{
							DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
							factory.setIgnoringComments(true);
							factory.setCoalescing(true); // Convert CDATA to Text nodes
							factory.setNamespaceAware(false); // No namespaces: this is default
							factory.setValidating(false); // Don't validate DTD: also default
							factory.setXIncludeAware(false);
							StringReader stReader = new StringReader(split);
							InputSource isource = new InputSource(stReader);
							DocumentBuilder parser = factory.newDocumentBuilder();				   
							Document document = parser.parse(isource);
							Node pTag = paperDoc.importNode((document.getDocumentElement()).cloneNode(true),true);
							//System.out.println("\n pTag Node Name: "+pTag.getNodeName()+"\t parent of child :"+childNodes.item(i));
							subroot.replaceChild(pTag,childNodes.item(i));
							id = strInt.id;
							paperId.setId(id);
							//subroot.insertBefore(pTag,childNodes.item(i));
							//Node removed = subroot.removeChild(childNodes.item(i+1));
							paperId.setNode(subroot);
							}
							catch(Exception e)
							{
								System.out.println("\n\n ERROR Occured while creating sub tree: return value :\n "+split);
								e.printStackTrace();
								//System.exit(0); //added on 23/11/10 by shs 
							}
						
						}	
				    }
				}
				else
				{
					if(childNodes.item(i).getNodeName().equals("#text")||childNodes.item(i).getNodeName().equals("B")||childNodes.item(i).getNodeName().equals("SUP")||childNodes.item(i).getNodeName().equals("XREF")||childNodes.item(i).getNodeName().equals("IT")||childNodes.item(i).getNodeName().equals("REF")||childNodes.item(i).getNodeName().equals("SB")||childNodes.item(i).getNodeName().equals("SP")||childNodes.item(i).getNodeName().equals("ext-link"))
						//B | SUP | XREF
					{
					    if(childNodes.item(i).getNodeName().equals("ext-link"))
						//	((Element)childNodes.item(i)).setAttribute
						childNodes.item(i).setPrefix("xlink");
						String tobeSplit = getString(childNodes.item(i));
						tobeSplit = tobeSplit.replaceFirst("<\\?xml.+?>","");
						//System.out.println("TEXT PART"+childNodes.item(i).getNodeName()+" : value :"+childNodes.item(i).getNodeValue());
						//tobeSplit = tobeSplit.substring(0, tobeSplit.length()-4);	
						int j=i+1;
						int inew=-1;
						int oldj = j;
						int newj =-1;

						for(j=i+1;j<childNodes.getLength();j++)
						{
							if(childNodes.item(i).getNodeName().equals("#text")||childNodes.item(i).getNodeName().equals("B")||childNodes.item(i).getNodeName().equals("SUP")||childNodes.item(i).getNodeName().equals("XREF")||childNodes.item(i).getNodeName().equals("IT")||childNodes.item(i).getNodeName().equals("REF")||childNodes.item(i).getNodeName().equals("SB")||childNodes.item(i).getNodeName().equals("SP")||childNodes.item(i).getNodeName().equals("ext-link"))
							{
							    
								String sibling = getString(childNodes.item(j));
								sibling = sibling.replaceFirst("<\\?xml.+?>","");
								inew = j;
								tobeSplit = tobeSplit.concat(sibling);
								//Node deleted = subroot.removeChild(childNodes.item(i));
								////System.out.println("deleted Node :"+deleted.getNodeName());
							}
							else
							{
							    	newj = j;
								break;
							}
						}
						
						StringInt strInt = sentenceSplit(tobeSplit,id);
						id = strInt.id;
						
						paperId.setId(id);
						String split = strInt.sTags;
						String dummy = "<dummy>";
						split = split.concat("</dummy>");//tobeSplit.substring(tobeSplit.length()-4,tobeSplit.length()));
						split = dummy.concat(split);
						//System.out.println("before making doc, split is:\n\n"+split);
						DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
						factory.setIgnoringComments(true);
						factory.setCoalescing(true); // Convert CDATA to Text nodes
						factory.setNamespaceAware(false); // No namespaces: this is default
						factory.setValidating(false); // Don't validate DTD: also default
						factory.setXIncludeAware(false);
						StringReader stReader = new StringReader(split);
						InputSource isource = new InputSource(stReader);
						DocumentBuilder parser = factory.newDocumentBuilder();				   
						Document document = parser.parse(isource);
						Node pTag = (document.getDocumentElement()).cloneNode(true);
						DocumentFragment df = paperDoc.createDocumentFragment();
						NodeList pTagNodes = pTag.getChildNodes();
						if(pTagNodes!=null&&pTagNodes.getLength()!=0)
						    {
							for(int a=0; a<pTagNodes.getLength(); a++)
							    {
								Node imported = paperDoc.importNode(pTagNodes.item(a),true);//df.importNode(pTagNodes.item(i),true);
								df.appendChild(imported);
							    }
						    }
						//	Node copyOfsubroot = subroot.cloneNode(true);
						/*
						if(i<childNodes.getLength())
						    copyOfsubroot.insertBefore(df,childNodes.item(i));
						else
						copyOfsubroot.appendChild(df);*/
						//subroot.insertBefore(df,childNodes.item(i));
						for(int g = i; g<j; g++)
						    {
							Node deleted = subroot.removeChild(childNodes.item(i));
						        //System.out.println("deleted Node :"+deleted.getNodeName());
						    }
						if(j>=childNodes.getLength())
						{
							//System.out.println("in if j is:"+j);
							subroot.appendChild(df);
							//break;
						}
						else
						{
							//System.out.println("in else j is:"+j);
							subroot.insertBefore(df, childNodes.item(i+1));
							
						}
						i = i+ pTagNodes.getLength()-1;
							//subroot.insertBefore(df, subroot)
					     	paperId.setNode(subroot);
						//paperDoc.replaceChild(subroot,copyOfsubroot);
						//System.out.println("\n pTag Node Name: "+pTag.getNodeName());
						
					}
				}
				////System.out.println("in for loop end id is "+id);
			}
		}
		return paperId;
	}
	
	public static Document findChildren(Document paperDoc,int id)throws Exception
	{
	    NodeInt paperId = new NodeInt(paperDoc,id);
		Element root = paperDoc.getDocumentElement();
		NodeList nodes = root.getElementsByTagName("ABSTRACT");
		if(nodes==null||nodes.getLength()==0)
		{
			nodes = paperDoc.getElementsByTagName("article");
			if(nodes!=null && nodes.getLength()!=0)
			{
				nodes = ((Element)nodes.item(0)).getElementsByTagName("front");
				if(nodes!=null && nodes.getLength()!=0)
				{
					nodes = ((Element)nodes.item(0)).getElementsByTagName("abstract");
					if(nodes!=null&&nodes.getLength()!=0)
					{
						for(int i=0; i<nodes.getLength(); i++)
						{
							NodeList childNodes = nodes.item(i).getChildNodes();
							//System.out.println("in abs loop id is :"+id+"node :"+nodes.item(i));
							paperId = callSentenceSplitter(paperDoc, nodes.item(i),childNodes, id); //delete this node.item(i), send the ref node, before what it will be added later. node that has been recreated returning that will be good. then after coming back from the function we replace it
							//	paperDoc = paperId.node;
							//System.out.println("in abs loop id is :"+id+"node :"+nodes.item(i));
							Node pTag = paperDoc.importNode(paperId.node.cloneNode(true),true);
							nodes.item(i).getParentNode().replaceChild(pTag,nodes.item(i));
							//System.out.println("in abs loop id returned from callSentence is :"+paperId.id);
							id = paperId.id;
						}
					}
				}
				//return paperDoc;
			}
			else
			{
				//System.out.println("No Abstract");
			}
		}
		else
		{
			//System.out.println("ABSTRACT found");
			for(int i=0; i<nodes.getLength(); i++)
			{
				NodeList childNodes = nodes.item(i).getChildNodes();
				paperId = callSentenceSplitter(paperDoc, nodes.item(i),childNodes, id);
				//paperDoc = paperId.node;
				Node pTag = paperDoc.importNode(paperId.node.cloneNode(true),true);
				root.replaceChild(pTag,nodes.item(i));
				id = paperId.id;
			}
		}

		nodes = root.getElementsByTagName("BODY");
		if(nodes==null||nodes.getLength()==0)
		{
			nodes = paperDoc.getElementsByTagName("article");
			if(nodes!=null && nodes.getLength()!=0)
			{
		       		nodes = ((Element)nodes.item(0)).getElementsByTagName("body");
	       			if(nodes!=null&&nodes.getLength()!=0)
       				{
       					for(int i=0; i<nodes.getLength(); i++)
       					{
	       					NodeList childNodes = nodes.item(i).getChildNodes();
	       					//System.out.println("in body loop id is :"+id);
	       					paperId = callSentenceSplitter(paperDoc, nodes.item(i), childNodes, id); 
       						//paperDoc = paperId.node;
						Node pTag = paperDoc.importNode(paperId.node.cloneNode(true),true);
					        nodes.item(i).getParentNode().replaceChild(pTag,nodes.item(i));
       						//System.out.println("in body loop id returned from callSentence is :"+paperId.id);
       						id = paperId.id;
       					}
       				}
				
				//return paperDoc;
			}
			else
			{
				//System.out.println("No Body");
			}
		}
		else
		{
			//System.out.println("BODY found");
			for(int i=0; i<nodes.getLength(); i++)
			{
				//System.out.println("Body read by XML::GDOME:"+nodes.item(i).toString());
				NodeList childNodes = nodes.item(i).getChildNodes();
				paperId = callSentenceSplitter(paperDoc, nodes.item(i), childNodes, id);
				//paperDoc = paperId.node;
				Node pTag = paperDoc.importNode(paperId.node.cloneNode(true),true);
				root.replaceChild(pTag, nodes.item(i));
				id = paperId.id;
			}
		}

		/*
		for(int i = 0; i < nodes.getLength(); i++)
		{
			org.w3c.dom.NodeList children = nodes.item(i).getChildNodes();
			if(children!=null && children.getLength()!=0)
			{
				paperDoc = callSentenceSplitter(paperDoc,id);
			}
		}
		*/
		return paperDoc;
	}
	public static Document getTitle(Document paperDoc, NodeList child, String str)
	{
		//Node title = null;
		if(child!=null&&child.getLength()!=0)
	    {
	    	int i=0;
	    	String subStrings[] = null;
	    	if(str.contains("/"))
    		{
    			subStrings = str.split("/");
    		}
	    	for(i = 0; i<child.getLength(); i++)
	    	{
	    		//System.out.println("Child :"+i+" :"+child.item(i).getNodeName());
	    		if(str.contains("/"))
	    		{
	    			// = str.split("/");
	    			if(child.item(i).getNodeName().equals(subStrings[0]))//||child.item(i).getNodeName().equals("CURRENT-TITLE")||child.item(i).getNodeName().equals("TITLE")||child.item(i).getNodeName().equals("article")||child.item(i).getNodeName().equals("front")||child.item(i).getNodeName().equals("article-meta")||child.item(i).getNodeName().equals("title-group"))
		    		{
	    				String subString = subStrings[1];
	    				for(int k=2;k<subStrings.length;k++)
	    				{
	    					subString = subString.concat("/"+subStrings[k]);
	    					/*
	    					if(k!=subStrings.length-1)
	    						subString = subString.concat("/");*/
	    				}
	    				NodeList grand1 = child.item(i).getChildNodes();
		    			paperDoc = getTitle(paperDoc, grand1,subString);
		    			return paperDoc;
		    		}	
	    		}
	    		else
	    		if(child.item(i).getNodeName().equals(str))//||child.item(i).getNodeName().equals("CURRENT-TITLE")||child.item(i).getNodeName().equals("TITLE")||child.item(i).getNodeName().equals("article")||child.item(i).getNodeName().equals("front")||child.item(i).getNodeName().equals("article-meta")||child.item(i).getNodeName().equals("title-group"))
	    		{
	    			//flag = 1;
	    			break;
	    		}
	    	}//for loop
	    	if(i<child.getLength())
	    	{
	    			NodeList grand = child.item(i).getChildNodes();
	    			if(grand!=null&&grand.getLength()!=0)
	    			{
	    				Element st = paperDoc.createElement("s");
	    				st.setAttribute("sid", "1");
	    				for(int j = 0; j<grand.getLength(); j++)
	    				{
	    					Node addGr = grand.item(j).cloneNode(true);
	    					st.appendChild(addGr);
	    				}
	    				child.item(i).insertBefore(st,child.item(i).getFirstChild());
						NodeList grandnew = child.item(i).getChildNodes();
						int limit = grandnew.getLength();
						//System.out.println("count :"+grandnew.getLength()+" ; limit"+limit);

						for(int j = 1; j<limit ; j++)
						    {
								Node rem = child.item(i).removeChild(grandnew.item(1));
							////System.out.println("rem :"+rem.getNodeName());
						    }
						//	NodeList grandnew = child.item(i).getChildNodes();
		    			for(int j = 0; j<grandnew.getLength(); j++)
		    			{
		    				//System.out.println("new :"+grandnew.item(j).getNodeName());
		    			}
		    			return paperDoc;
	    			// Done ..title found. so add s tag in it. cloneNode(true) can be used to get copy of the node. or may be s tag can be inserted before all node under title.when creating subtree create a node and mention its document_fragment , or create document_fragment from document
	    		
	    			}
	   		}
	    }
		return null;
	}
	public static String sentenceExtraction(Document paperDoc, String name) throws Exception {
		//System.out.println("in sentence Extraction\n\n\n\n");
		try{
		    Element root = paperDoc.getDocumentElement();
		    NodeList child = root.getChildNodes();
		    //NodeList child = root.getElementsByTagName("TITLE");//all element name title in this doc is returned
		    int flag = 0;
		    Document testpaperDoc = getTitle(paperDoc,child,"CURRENT_TITLE");
		    if(testpaperDoc==null)
		    {
		    	testpaperDoc = getTitle(paperDoc,child,"TITLE");
		    	if(testpaperDoc==null)
		    	{
		    		testpaperDoc = getTitle(paperDoc,child,"article/front/article-meta/title-group/article-title");
		    		if(testpaperDoc!=null)
			    	{
		    			//System.out.println("article-title");
		    			flag=1;
			    	}
		    		else
		    		{
		    			flag =-1;
		    			//System.out.println("no title");
		    		}
		    	}
		    	else
		    	{
		    		//System.out.println("ART paper, title");
		    	}
		    }
		    else
		    {
		    	//System.out.println("current title");
		    }
		    int id =1;
		    if(flag!=-1)
			{
			    id = 2;
			}
		    long startTime = System.currentTimeMillis();

		    paperDoc = findChildren(paperDoc,id);
		    long endTime = System.currentTimeMillis();
		    //System.out.println("time elapsed : "+ (endTime-startTime));
			//flagAbs = 0;
			//flagBody = 0;
			
			//if(absTags.size()>0)
			//flagAbs = 1;*/
			/*
			//System.out.println("Paper document base uri:  "+paperDoc.getBaseURI());
			String queryAbs = "PAPER/article/front/article-meta/abstract|PAPER/ABSTRACT";
			int id=2;
			String queryAbs2 = "PAPER/article/front/article-meta";
			Nodes abRoot = paperDoc.query("PAPER/article/front/article-meta|PAPER");
			NodeInt nid = findChildren(paperDoc,queryAbs,2,queryAbs2);
			id = nid.id;
			//System.out.println("\n\n root of nid : "+id+":"+nid.node.toString());
			
			if(abRoot.size()==1)
			{
				paperDoc.replaceChild(abRoot.get(0), nid.node);
			}
			String queryBody = "PAPER/article/body|PAPER/BODY";
			String queryBody2 = "PAPER/article";
			nid = findChildren(paperDoc,queryBody,id,queryBody2);
			paperDoc.replaceChild(paperDoc.getRootElement(), nid.node);
			//System.out.println("\n\nback");
			fileString = paperDoc.toXML();
			//System.out.println("\n\n FILE STRING :\n\n"+fileString);*/
		}
		catch(Exception xp)
		{
			xp.printStackTrace();
		}
	String fileString = getString(paperDoc);
	
	Pattern xmlDeclaration = Pattern.compile("(<\\?xml.+?><PAPER>)(.*)\\Z",Pattern.DOTALL);//shs
    Matcher xmatch = xmlDeclaration.matcher(fileString);
    if (xmatch.find()) {
            String a = xmatch.group(1);
            String b = xmatch.group(2);
            a = a + "<mode2 name='" + name + "' hasDoc='yes'" + " version= '" + sapientVersion + "'/>";
            fileString = a + b;
    }

        return fileString;
	} 

}

