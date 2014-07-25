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
	public StringInt()
	{
		sTags = "";
		id = 2;
	}
    public StringInt(String str,int i)
	{
		sTags = new String(str);
		id = i;
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
	    node = n.cloneNode(true);
	    id = i;
	}
	public void setNode(Node n)
	{
	    node = n.cloneNode(true);
	}
    public void setId(int n)
	{
	    id = n;
	}
	
}

public class SSSplit {
	private static final int sapientVersion = 597;
	public static String fileName;
	private static StringBuffer finalbuffer;

	public static String removeInvalidTags(String string)
	{
        
	    int i=0;
	    Vector<String> tags = new Vector<String>();
	    
	    Pattern closingTags = Pattern.compile("</?(.+?)>");
	    Matcher closingTagsMatcher = closingTags.matcher(string);
	    
	    
	    while(closingTagsMatcher.find())
		{
		    if(!(closingTagsMatcher.group().endsWith("/>")))
			{
			    if(closingTagsMatcher.group().charAt(1)=='/')
				{
				    if(tags.lastElement().startsWith(closingTagsMatcher.group(1)))
					{
					    tags.removeElementAt(tags.size()-1);
					}
				    else
					{
					    String pattern = "<"+tags.elementAt(tags.size()-1)+">(.+?)(?="+closingTagsMatcher.group()+")";
        			
					    
					    Pattern p = Pattern.compile(pattern);
					    Matcher m = p.matcher(string);
					    if(m.find())
						{
						    string = string.replaceAll(pattern, m.group());
						}
					    else
						System.out.println("ajob...");
					    
					}
				}
			    else
				{
				    tags.add(closingTagsMatcher.group(1));
				}
			}
		}//end of outer while
  
	    return string;
	}
	
	
	public static StringInt sentenceSplit(String clearString,int sid)
	{
	    String badWhiteSpace = "(\t|\r|\n|\\s)";
	    String replacement = "<\\?jarpath /\\?>|<\\?host null:8181\\?>|<\\?viewer picture\\?>";
        
	    clearString = clearString.replaceAll(replacement, "");
        
	    clearString = clearString.replaceAll(badWhiteSpace, "sapientPOO");
	    clearString = clearString.replaceAll("(sapientPOO)+", " ");
        
	    clearString = clearString.replaceAll(">\\s<", "><");
	    clearString = clearString.replaceAll("<FIGURE/>", "");

	    clearString = clearString.replaceAll("<graphic.*?/>", "");
       
	    StringBuffer finalbuffer = new StringBuffer();
	    ArrayList<StringBuffer> nsentences = new ArrayList<StringBuffer>();
	    String allowedAttrChars = "[\\w-_\2013\\.\\(\\)\\[\\]]";
		
	    String refSCIgeneral = "(?:(?i)(?:(?:\\d+[,\u2013])*\\d+)?(?:</IT>)?<REF(?:(?:\\sID=\"(?:\\w-)?\\w+?(?:\\s\\w+?)*\")|(?:\\sREFID=\"\\w+?\")|(?:\\stext=\"(?:refs?\\.(?:\\s)?)?(?:(?:\\d+[,�\u2013\u002D])*\\d+)?\\w*?\")|(?:\\sTYPE=\"\\w+?\"))*(?:\\s?/>|>(?:(?:refs?\\.(?:\\s)?)?(?:(?:(?:\\d+(?:<IT>)?\\w?(?:</IT>)?)|(?:(?:<IT>)?\\w(?:</IT>)?[-,\u2013])|(?:(?:<IT>)?\\w(?:</IT>)?[-,\u2013]))*(?:(?:\\d+(?:<IT>)?\\w?(?:</IT>)?)|(?:(?:<IT>)?\\w?(?:</IT>)?)))?</REF>))|(?:(?i)<xref(?:\\sid=\"(?:\\w-)?\\w+?(?:\\s\\w+?)*\")?(?:\\sref-type=\"(?:aff|app|author-notes|bibr|boxed-text|chem|contrib|corresp|disp-formula|fig|fn|kwd|list|plate|scheme|sec|statement|supplementary-material|table|table-fn|other)\")?(?:\\srid=\"(?:[-\\u2013\\w])*\")?>[-\\u2013,\\d]+</xref>)(?-i))"; 

	    String refFootnote= "<SUP TYPE=\"FOOTNOTE_MARKER\"\\sID=\"" + allowedAttrChars + "+?\"/>";

	    String atLeastOneRefSCI = "((?:" + refSCIgeneral + "+" + "\\)?)|" + refFootnote + "|\\))"; //there may be a bracket after the reference
        
	    String capturePunctuation = "(\\.|\\?|(?<!\\(\\w{1,15})\\!)";

	    String abbreviations = "((?i)(\\(|\\[|\\s|>|^)(al|Am|Angew|approx|Biochim|Biophys|ca|cf|Chem|Co|conc|Dr|Drs|Corp|Ed|no|No|e\\.g|p\\.p\\.m|Engl|eq|eqns?|exp|Rs|Figs?|Labs?|Dr|etc|Calc|i\\.e|Inc|Int|Lett|Ltd|p|p\\.a|Phys|Prof|prot|refs?|Rev|sect|st|vs|(?-i)(?<!(?:</SB>|(?:\\d\\s?(<IT>?))|<IT>))(?:(?:(?:[A-Z]|[a-z])?\\.)\\s?[a-z])|(?-i)(?<!(?:</SB>|(?:\\d\\s?(<IT>?))|<IT>))(?:(?:(?:[A-Z]|[a-z])\\.)?\\s?(?:(?:[A-Z]|[a-z])\\.)?\\s?[A-Z])|(?-i)(?<!(?:</SB>|(?:\\d\\s?(<IT>?))|<IT>))(?:(?:(?:[A-Z]|[a-z])\\.)?\\s?(?:(?:[A-Z]|[a-z])\\.)\\s?[a-z])|(?-i)(?<=(?:(?<!(?:</SB>|(?:\\d)))(?:(?:\\s|\\(|^)<IT>)))(?:\\s?\\w{1,10})|\\s?\\.\\s?\\.\\s?|\\())";
        
        
	    // moving all references inside the punctuation so that the sentence splitting is easier
	    Pattern refSentence = Pattern.compile("(.*?)" +  capturePunctuation + atLeastOneRefSCI,Pattern.CASE_INSENSITIVE);

        Pattern abbrevs = Pattern.compile(".*?(" + abbreviations + "(?:</IT>)?)" + "$",Pattern.CASE_INSENSITIVE); 

        Matcher refm = refSentence.matcher(clearString);
        StringBuffer swappedString = new StringBuffer();

        while (refm.find()) {
                String a = refm.group(1); //sentence
                String b = refm.group(2); //punctuation
                String c = refm.group(3); //reference

                Matcher abbrevm=abbrevs.matcher(a);
                if (abbrevm.find()){
                    String ab = abbrevm.group(1);
                	swappedString.append(a); // don't change order
                	swappedString.append(b);
                	swappedString.append(c);
                }else {
		    if((a.endsWith("0")||a.endsWith("1")||a.endsWith("2")||a.endsWith("3")||a.endsWith("4")||a.endsWith("5")||a.endsWith("6")||a.endsWith("7")||a.endsWith("8")||a.endsWith("9"))&&(c.startsWith("1")||c.startsWith("2")||c.startsWith("3")||c.startsWith("4")||c.startsWith("5")||c.startsWith("6")||c.startsWith("7")||c.startsWith("8")||c.startsWith("9"))&&b.equals(".")) 
                	{
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

        // anything after the last swapped reference
        String endbit = clearString.substring(swappedString.length(),
                        clearString.length());
        swappedString.append(endbit);
        clearString = swappedString.toString();
        clearString = clearString.replaceAll(">\\.<", ">\\. <"); 

        
        String capitals = "[A-Z0-9]"; //caps and numbers may begin a sentence
        String punctuation = "(?:\\.|\\?|(?<!\\(\\w{1,15})\\!)"; 
      
        String optPunctuation = punctuation + "??";
        String endEquation = "</EQN>";
        String endPara = "(</P>|</ABSTRACT>|</list>)";
        String beginPara = "<P>";
        String optStartQuote = "['\"\u201C]?";
        String optCloseQuote = "['\"\u201D]?";
        String optReferenceSCI = refSCIgeneral + "*";

        String beginFirstSentence = "^";
        String endLastSentence = "$";
        String openHeader = "(<HEADER(\\sHEADER_MARKER=\""+ allowedAttrChars + "+?\")?>|<HEADER/>|<TITLE>|<TITLE/>)"; 
        String wholeHeader = "((<BODY>)?(<DIV(\\sDEPTH=\"\\d+\")?>)?(<HEADER(\\sHEADER_MARKER=\"" + allowedAttrChars + "+?\")?>.*?</HEADER>|<HEADER/>)|<TITLE>)";               
        String optOpenHeader = openHeader + "?";
        
        
        String eqn = "<EQN(\\sID=\"" + allowedAttrChars + "+?\")?(\\sTYPE=\"" + allowedAttrChars + "+?\")?>";
        String xref = "<XREF(\\sID=\"" + allowedAttrChars + "+?\")?(\\sTYPE=\"" + allowedAttrChars + "+?\")?>";
        String listTag = "<list.+?>"; //13/10/09

        String manyStartTags = "(" + eqn + "|" + xref +"|"+listTag + "|<BODY>|<DIV(\\sDEPTH=\"\\d+\")?>|<P>|<p.+?>|<SEC.+?>|<disp-quote>|<supplementary-material.+?>|<boxed-text.+?>|<list list-type=\"\\w{2,20}\">|<list-item>|<ABSTRACT>|<abstract.+>|<statement>|<def>)*";
        String optEndTags = "(</XREF>|</HEADER>|<HEADER/>|</TITLE>|</boxed-text>|</list>|</list-item>|</statement>)?"; //shs

        String optEndTags1 = "(</XREF>|</HEADER>|<HEADER/>|</TITLE>|</boxed-text>|<list.+?>|</list>|</list-item>|</statement>|</inline-supplementary-material>|<inline-supplementary-material/>|</related-article>|</related-object>|</address>|</alternatives>|</array>|</boxed-text>|</chem-struct-wrap>|</fig>|</fig-group>|<graphic.+?/>|</media>|</preformat>|</supplementary-material>|</table-wrap>|</table-wrap-group>|</disp-formula>|</disp-formula-group>|</element-citation>|</mixed-citation>|</nlm-citation>|</bold>|</italic>|</monospace>|</overline>|</overline-start>|</overline-end>|</roman>|</sans-serif>|</sc>|</strike>|</underline>|</underline-start>|</underline-end>|</award-id>|</funding-source>|</open-access>|</chem-struct>|<inline-formula/>|<inline-graphic/> |</private-char>|</def-list>|</list>|</tex-math>|</mml:math>|</abbrev>|</milestone-end>|</milestone-start>|</named-content>|</styled-content>|</ack> |</disp-quote>|</speech>|</statement>|</verse-group>|</fn>|</target>|</xref>|</ref>|</sub>|</sup>|</def>)*"; 

        String endTags = "(</P>|</IT>|</italic>|</EQN>|</XREF></bold>|</NAMED-CONTENT>|<disp-formula>|</HEADER>|<HEADER/>|</TITLE>|</disp-quote>|</supplementary-material>|</boxed-text>|</list>|</list-item>|</statement>)"; //shs
        String manyEndTags = endTags + "*";

        String endParaOrEq = "(" + endPara+"|" + endEquation + ")\\s?"; 
        String formatting="(<B>|<IT>|<SP>|<italic>|<BOLD>|<disp-formula>|<named-content.+?>)"; 
        
        String puncNoAbbrv = "(?<!" + abbreviations + "(</IT>)?)"+ punctuation + "\\s";
        String greekLetters = "[\u0370-\u03FF\u1F00-\u1FFF]";
        String pAttr = "<p.+?>";
        String sentenceCommencer = "(?>" +beginPara + "|" + pAttr +"|"+ "Fig(s)?\\." + "|" + capitals + "|" + formatting + "|" + "\\[|\\(|"+greekLetters+"|\u007C)";
        String equationCommencer = "(" + eqn + ".)";
        String commencer = "(" + sentenceCommencer + "|" + equationCommencer + ")";

        
        String noSpaceReqLookahead =  manyStartTags + optOpenHeader + optStartQuote + commencer;
        
        String nocapsParaLookAhead  = "(\\s?<P>)";
        
        String startSentence = manyStartTags + optStartQuote + commencer;
        
        // For matching the end of the previous sentence
        String sentenceFigLookbehind = "(?<=(?<!"+ abbreviations + punctuation + ")((" + endParaOrEq + ")|("+ puncNoAbbrv + ")|("
        + optPunctuation + optEndTags + endTags + "\\s?)))";
        
        //for matching the start of a sentence following a header
        String headerLookahead = "(?=(?:" + manyStartTags + optOpenHeader
                        + optStartQuote + commencer + "))";

        String Figure="<fig.+?</fig>";
        String tableWrap = "<table-wrap.+?</table-wrap>";
        String title = "((?:<title/>)|(?:<title.+?</title>))";
        String secLookBehind = "((?:<SEC>)|(?:<SEC.+?>))?"; // <sec> can be followed by<body>.
        String supplimentbehind = "<supplementary-material.+?</supplementary-material>";
        String refList = "<ref-list.+?</ref-list>";
        String boxed = "(?:<boxed-text.+?>)(?:<caption>)?";
        
        Pattern sentence = Pattern.compile(
        		"(" + sentenceFigLookbehind + "(" +secLookBehind + title +")+"+")|"+ 
        		"("+ sentenceFigLookbehind +"("+ boxed + secLookBehind + title +"?)"+optEndTags1+")|"+
        		"(" + sentenceFigLookbehind + wholeHeader + headerLookahead + 
			//lookbehind and start of a normal sentence, or a match for the first sentence (at the beginning of the abstract)
			")|" +
			"(" + sentenceFigLookbehind + "((("+ tableWrap+")+("+Figure +")+)|(("+ Figure +")+("+ tableWrap +")+)|("+tableWrap +")+|("+ Figure+")+)" + optEndTags+")|"
			+"("+ sentenceFigLookbehind + "((("+supplimentbehind +")+"+ optEndTags+")|(("+supplimentbehind +")+"+secLookBehind+title+")))|" 
			+ "("+ sentenceFigLookbehind + "("+ refList +")+"+optEndTags1+")|"
			+"(((" + sentenceFigLookbehind +""+ startSentence + 
			")|" + beginFirstSentence + "|" + beginPara + ")" +
			// The sentence content
			"(.*?)(Fig(s)?\\..+?)*?" +
			// punctuation that ends a sentence. Give prioriy to endEquation then puncNoRef
			"(((?<!(" + endEquation + "\\s?|" + puncNoAbbrv + "\\s?|" + endPara + "\\s?))" 
			+ "(?=(?:"  + nocapsParaLookAhead + ")))|" +
			
			"((?>" + endEquation + "\\s?|" + puncNoAbbrv + "\\s?|" + endPara + "\\s?)"
			+ optCloseQuote	+ optReferenceSCI + manyEndTags + "\\s?"
			+ "(?=(?:" + noSpaceReqLookahead + "|" + nocapsParaLookAhead + "|\\n|\\s*$)))|"+endLastSentence+"))"
        			
        		
        							
			// lookahead to beginning of next sentence
			// end of line or end of whole string
			,Pattern.CASE_INSENSITIVE);
        

        Matcher m = sentence.matcher(clearString);
        ArrayList<StringBuffer> sentences = new ArrayList<StringBuffer>();
        
        int somethingFound = 0;
        // This bit splits the sentences
        while (m.find()) {
	    somethingFound = 1;
	    sentences.add(new StringBuffer(m.group()));
        }
        if(somethingFound == 0) {
	    // ???
        }
        Pattern refSentenceRev = Pattern.compile("(.*?)" + atLeastOneRefSCI
				 + capturePunctuation + "(\\s?(?:</P>)?)\\Z",Pattern.CASE_INSENSITIVE);

        int count = 0;
        
        ArrayList<StringBuffer> newSentences = new ArrayList<StringBuffer>();

       

        for (StringBuffer s : sentences) {
                Matcher refmRev = refSentenceRev.matcher(s);

                // if sentence finishes with reference + punctuation, swap the two over
                if (refmRev.find()) {
                        String a = refmRev.group(1); //sentence
                        String b = refmRev.group(2); //reference or bracket or both
                        
                        String c = refmRev.group(3); //punctuation
                        String d = refmRev.group(4); //space and/or </P>

                        StringBuffer ns = new StringBuffer();

                        if (b.endsWith(")")) { 
			    ns.append(a); //sentence
			    ns.append(b); //bracket
			    ns.append(c); //punctuation
			    ns.append(d); //space
                        } else {
			    if(!b.startsWith("<"))
				{
				    int index=b.indexOf("<");
				    String b1=b.substring(0, index); // end index exclusive
				    String b2=b.substring(index);
				    a=a.concat(b1);
				    b=b2;
				}
			    ns.append(a); //sentence
                            ns.append(c); //punctuation
                            ns.append(b); //reference
                            ns.append(d); //space
                        	
                        }
                        newSentences.add(ns);
                        
                } else {
                	newSentences.add(s);
                }
                count++;
        }
        sentences = newSentences;
        // Post-processing sentence array to move XML tags outside the sentences
        String ppStartTags = "((?:<ABSTRACT>|<BODY>|<SEC(?:.+?)>|<DIV(\\sDEPTH=\"\\d+\")?>|<P>|<P.+>|<disp-quote>|<list.+?>|<list-item>|<abstract.+?>|<statement>)*)"; 
        String ppSentence = "(.+?)";
        String ppEndTags = "((?:</ABSTRACT>|</BODY>|</SEC>|</DIV>|</P>|</disp-quote>|</list>|</list-item>|</boxed-text>|</statement>|<list.+?>|<list-item>)*\\s?)\\Z";
       
        Pattern pp = Pattern.compile(ppStartTags + ppSentence + ppEndTags,Pattern.CASE_INSENSITIVE);
        Pattern ppHeader = Pattern.compile(".*?<HEADER.+?",Pattern.CASE_INSENSITIVE);
        Pattern ppTitle = Pattern.compile(".*?<TITLE.+?>",Pattern.CASE_INSENSITIVE); 
        Pattern ppFig = Pattern.compile("<fig.+?>|<table-wrap.+?>",Pattern.CASE_INSENSITIVE); 
        Pattern ppCap = Pattern.compile("</caption.+?>|</fn.+?>",Pattern.CASE_INSENSITIVE); 
        Pattern paraAttr = Pattern.compile("<abstract><p.+></p>",Pattern.CASE_INSENSITIVE);
        Pattern suppli = Pattern.compile("<supplementary-material.+?>",Pattern.CASE_INSENSITIVE);
        Pattern named = Pattern.compile("<named-content.+?>", Pattern.CASE_INSENSITIVE);
        
        int id = sid;

        for (StringBuffer s : sentences) {
                Matcher ppm = pp.matcher(s);
                if (ppm.matches()) {
                        String one = "";
                        if (ppm.group(1) != null)
                                one = ppm.group(1);
                        String two = ppm.group(3);
                     
                        String three = "";
                        if (ppm.group(4) != null)
                                three = ppm.group(4);
                        
                        Matcher mHead = ppHeader.matcher(s);
                        Matcher mTitle = ppTitle.matcher(s);
                        Matcher mfig = ppFig.matcher(s);
                        Matcher mCap = ppCap.matcher(s);
                        Matcher mParaAttr = paraAttr.matcher(s);
                        Matcher mSuppli = suppli.matcher(s);
                        Matcher mNamed = named.matcher(s);
                        
                        if (!(mHead.matches()||mTitle.matches()||mfig.matches()||mCap.matches()||mParaAttr.matches()|mSuppli.matches())) 
                        {
			    nsentences.add(new StringBuffer(one + "<s sid=\"" + id
						+ "\">" + two + "</s>" + three));
			    id++;
                        } else {
			    nsentences.add(s);
                        }
                } else {
                        System.out.println("Sentence " + id + "-- " + s + " -- didn't match!");
                }
        }
       
        
        int countme = 0;
        for (StringBuffer s : nsentences) {
	    countme++;
	    finalbuffer.append(s);
        }
	
        String string = finalbuffer.toString();
        StringInt stringInt = new StringInt(string,id);
        
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
            transformer.transform(source, result);
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
	    NodeInt paperId = new NodeInt(subroot,id);
	    NodeList childNodes = subroot.getChildNodes();
	    if(childNodes!=null&&childNodes.getLength()!=0)
		{
		    for(int i=0; i<childNodes.getLength(); i++)
			{
			    if(childNodes.item(i).getNodeName().equalsIgnoreCase("sec")||childNodes.item(i).getNodeName().equalsIgnoreCase("statement")||childNodes.item(i).getNodeName().equalsIgnoreCase("DIV")||childNodes.item(i).getNodeName().equalsIgnoreCase("boxed-text")||childNodes.item(i).getNodeName().equalsIgnoreCase("list")||childNodes.item(i).getNodeName().equalsIgnoreCase("list-item")||childNodes.item(i).getNodeName().equalsIgnoreCase("disp-quote")||childNodes.item(i).getNodeName().equalsIgnoreCase("speech")||childNodes.item(i).getNodeName().equalsIgnoreCase("fn-group")||childNodes.item(i).getNodeName().equalsIgnoreCase("fn")||childNodes.item(i).getNodeName().equalsIgnoreCase("def-list")||childNodes.item(i).getNodeName().equalsIgnoreCase("def-item")||childNodes.item(i).getNodeName().equalsIgnoreCase("def"))
				{
					NodeList grandNodes = childNodes.item(i).getChildNodes();

					paperId = callSentenceSplitter(paperDoc,childNodes.item(i),grandNodes,id);
					id = paperId.id;
					subroot.replaceChild(paperId.node,childNodes.item(i));
					paperId.setNode(subroot);
					
				}
				else
				if(childNodes.item(i).getNodeName().equalsIgnoreCase("p"))
				{
				    NodeList graphic = ((Element)childNodes.item(i)).getElementsByTagName("graphic");
				    NodeList xlink = ((Element)childNodes.item(i)).getElementsByTagNameNS("*", "*");
				    NodeList childrenOfP = ((Element)childNodes.item(i)).getChildNodes();
				    if(graphic!=null&&graphic.getLength()!=0)
					{
					    for(int s = 0; s<graphic.getLength(); s++)
						{
						    if(((Element)graphic.item(s)).hasAttribute("xlink:href"))
						    graphic.item(s).getParentNode().removeChild(graphic.item(s));
						}
					}
				    if(xlink!=null&&xlink.getLength()!=0)
					{
					    for(int s = 0; s<xlink.getLength(); s++)
						{
						    if(((Element)xlink.item(s)).hasAttribute("xlink:href"))
						    {	
						    	((Element)xlink.item(s)).setAttributeNS("http://www.w3.org/1999/xlink","xlink:href",((Element)xlink.item(s)).getAttributeNode("xlink:href").getNodeValue());
						    }
						    if(((Element)xlink.item(s)).hasAttribute("xlink:type"))
						    {	
						    	((Element)xlink.item(s)).setAttributeNS("http://www.w3.org/1999/xlink","xlink:type",((Element)xlink.item(s)).getAttributeNode("xlink:type").getNodeValue());
						    }
						    if(((Element)xlink.item(s)).hasAttribute("xlink:role"))
						    {	
						    	((Element)xlink.item(s)).setAttributeNS("http://www.w3.org/1999/xlink","xlink:role",((Element)xlink.item(s)).getAttributeNode("xlink:role").getNodeValue());
						    }
						    if(((Element)xlink.item(s)).hasAttribute("xlink:title"))
						    {	
						    	((Element)xlink.item(s)).setAttributeNS("http://www.w3.org/1999/xlink","xlink:title",((Element)xlink.item(s)).getAttributeNode("xlink:title").getNodeValue());
						    }
						    if(((Element)xlink.item(s)).hasAttribute("xlink:show"))
						    {	
						    	((Element)xlink.item(s)).setAttributeNS("http://www.w3.org/1999/xlink","xlink:show",((Element)xlink.item(s)).getAttributeNode("xlink:show").getNodeValue());
						    }
						    if(((Element)xlink.item(s)).hasAttribute("xlink:actuate"))
						    {	
						    	((Element)xlink.item(s)).setAttributeNS("http://www.w3.org/1999/xlink","xlink:actuate",((Element)xlink.item(s)).getAttributeNode("xlink:actuate").getNodeValue());
						    }
						    if(((Element)xlink.item(s)).hasAttribute("mml:math"))
						    {	
						    	((Element)xlink.item(s)).setAttributeNS("http://www.w3.org/1998/Math/MathML","mml:math",((Element)xlink.item(s)).getAttributeNode("mml:math").getNodeValue());
						    }
						}
					}
				    if(childrenOfP.getLength()==1&&!(childrenOfP.item(0).getNodeName().equals("#text"))&&(((Element)childrenOfP.item(0)).getNodeName().equalsIgnoreCase("ext-link")||((Element)childrenOfP.item(0)).getNodeName().equalsIgnoreCase("e-mail")||((Element)childrenOfP.item(0)).getNodeName().equalsIgnoreCase("uri")||((Element)childrenOfP.item(0)).getNodeName().equalsIgnoreCase("inline-supplementary-material")||((Element)childrenOfP.item(0)).getNodeName().equalsIgnoreCase("related-article")||((Element)childrenOfP.item(0)).getNodeName().equalsIgnoreCase("related-object")||((Element)childrenOfP.item(0)).getNodeName().equalsIgnoreCase("address")||((Element)childrenOfP.item(0)).getNodeName().equalsIgnoreCase("alternatives")||((Element)childrenOfP.item(0)).getNodeName().equalsIgnoreCase("array")||((Element)childrenOfP.item(0)).getNodeName().equalsIgnoreCase("funding-source")||((Element)childrenOfP.item(0)).getNodeName().equalsIgnoreCase("inline-graphic"))) 
				    {}	
				    else
				    {
				    	String tobeSplitorg = getString(childNodes.item(i));
				    	tobeSplitorg = tobeSplitorg.replaceFirst("<\\?xml.+?>","");
				    	Pattern para = Pattern.compile("<p>|<p.+?>", Pattern.CASE_INSENSITIVE);
				    	Matcher mpara = para.matcher(tobeSplitorg);
						if(mpara.find())
						{
						    Pattern cpara = Pattern.compile("</p>", Pattern.CASE_INSENSITIVE);
						    Matcher cmpara = cpara.matcher(tobeSplitorg);
					    	
						    String tobeSplit = mpara.replaceFirst("");
						    if(cmpara.find())
							{
							    tobeSplit = tobeSplit.substring(0, tobeSplit.length()-4);
							}
						    StringInt strInt = sentenceSplit(tobeSplit,id);
							
						    String split = strInt.sTags;
						    split = split.concat(tobeSplitorg.substring(tobeSplitorg.length()-4,tobeSplitorg.length()));
						    split = mpara.group().concat(split);
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
							subroot.replaceChild(pTag,childNodes.item(i));
							id = strInt.id;
							paperId.setId(id);
							paperId.setNode(subroot);
							}
							catch(Exception e)
							{
								System.out.println("\n\n ERROR Occured while creating sub tree: return value :\n "+split);
								e.printStackTrace();
							}
						
						}	
				    }
				}
				else
				{
					if(childNodes.item(i).getNodeName().equals("#text")||childNodes.item(i).getNodeName().equals("B")||childNodes.item(i).getNodeName().equals("SUP")||childNodes.item(i).getNodeName().equals("XREF")||childNodes.item(i).getNodeName().equals("IT")||childNodes.item(i).getNodeName().equals("REF")||childNodes.item(i).getNodeName().equals("SB")||childNodes.item(i).getNodeName().equals("SP")||childNodes.item(i).getNodeName().equals("ext-link"))
					{
					    if(childNodes.item(i).getNodeName().equals("ext-link"))
						childNodes.item(i).setPrefix("xlink");
						String tobeSplit = getString(childNodes.item(i));
						tobeSplit = tobeSplit.replaceFirst("<\\?xml.+?>","");
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
						split = split.concat("</dummy>");
						split = dummy.concat(split);
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
								Node imported = paperDoc.importNode(pTagNodes.item(a),true);
								df.appendChild(imported);
							    }
						    }
						for(int g = i; g<j; g++)
						    {
							Node deleted = subroot.removeChild(childNodes.item(i));
						    }
						if(j>=childNodes.getLength())
						{
							subroot.appendChild(df);
						}
						else
						{
							subroot.insertBefore(df, childNodes.item(i+1));
							
						}
						i = i+ pTagNodes.getLength()-1;
					     	paperId.setNode(subroot);
					}
				}
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
							paperId = callSentenceSplitter(paperDoc, nodes.item(i),childNodes, id); //delete this node.item(i), send the ref node, before what it will be added later. node that has been recreated returning that will be good. then after coming back from the function we replace it
							Node pTag = paperDoc.importNode(paperId.node.cloneNode(true),true);
							nodes.item(i).getParentNode().replaceChild(pTag,nodes.item(i));
							id = paperId.id;
						}
					}
				}
			}
			else
			{
			}
		}
		else
		{
			for(int i=0; i<nodes.getLength(); i++)
			{
				NodeList childNodes = nodes.item(i).getChildNodes();
				paperId = callSentenceSplitter(paperDoc, nodes.item(i),childNodes, id);

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

	       					paperId = callSentenceSplitter(paperDoc, nodes.item(i), childNodes, id); 

						Node pTag = paperDoc.importNode(paperId.node.cloneNode(true),true);
					        nodes.item(i).getParentNode().replaceChild(pTag,nodes.item(i));
       						id = paperId.id;
       					}
       				}
			}
			else
			{
			}
		}
		else
		{
			for(int i=0; i<nodes.getLength(); i++)
			{
				NodeList childNodes = nodes.item(i).getChildNodes();
				paperId = callSentenceSplitter(paperDoc, nodes.item(i), childNodes, id);
				Node pTag = paperDoc.importNode(paperId.node.cloneNode(true),true);
				root.replaceChild(pTag, nodes.item(i));
				id = paperId.id;
			}
		}

		return paperDoc;
	}
	public static Document getTitle(Document paperDoc, NodeList child, String str)
	{
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
	    		if(str.contains("/"))
	    		{
	    			if(child.item(i).getNodeName().equals(subStrings[0]))
		    		{
	    				String subString = subStrings[1];
	    				for(int k=2;k<subStrings.length;k++)
	    				{
	    					subString = subString.concat("/"+subStrings[k]);
	    				}
	    				NodeList grand1 = child.item(i).getChildNodes();
		    			paperDoc = getTitle(paperDoc, grand1,subString);
		    			return paperDoc;
		    		}	
	    		}
	    		else
	    		if(child.item(i).getNodeName().equals(str))
	    		{
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

						for(int j = 1; j<limit ; j++)
						    {
							Node rem = child.item(i).removeChild(grandnew.item(1));
						    }
		    			for(int j = 0; j<grandnew.getLength(); j++)
		    			{
		    			}
		    			return paperDoc;
	    			// Done ..title found. so add s tag in it. cloneNode(true) can be used to get copy of the node. or may be s tag can be inserted before all node under title.when creating subtree create a node and mention its document_fragment , or create document_fragment from document
	    		
	    			}
	   		}
	    }
		return null;
	}
	public static String sentenceExtraction(Document paperDoc, String name) throws Exception {
		try{
		    Element root = paperDoc.getDocumentElement();
		    NodeList child = root.getChildNodes();
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
		    			flag=1;
			    	}
		    		else
		    		{
		    			flag =-1;
		    		}
		    	}
		    	else
		    	{
		    	}
		    }
		    else
		    {
		    }
		    int id =1;
		    if(flag!=-1)
			{
			    id = 2;
			}
		    long startTime = System.currentTimeMillis();

		    paperDoc = findChildren(paperDoc,id);
		    long endTime = System.currentTimeMillis();


		}
		catch(Exception xp)
		{
			xp.printStackTrace();
		}
	String fileString = getString(paperDoc);
	
	Pattern xmlDeclaration = Pattern.compile("(<\\?xml.+?><PAPER>)(.*)\\Z",Pattern.DOTALL);
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

