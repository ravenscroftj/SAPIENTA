package uk.ac.aber.sssplit;

import java.io.File;
import java.io.FileReader;
import java.io.IOException;

import org.custommonkey.xmlunit.Diff;
import org.junit.Assert;
import org.junit.Test;
import org.xml.sax.SAXException;

public class AverageTimeTest {
    @Test
    public void testSplit() throws Exception{

    	double accum = 0;
    	
        for(int i=0; i < 100; i++) {
        	System.out.println(String.format("Running splitter - Iteration #%d", i));
        	long timeTaken= timeOperation();
            System.out.println(String.format("Took %dms",timeTaken ));
            accum += timeTaken;
            System.out.println(String.format("Running average: %f", accum / (i+1)) );
        }
        

        System.out.println(String.format("Average time of splitter: %f", accum / 100) );

    }
    
    private long timeOperation() throws SAXException, IOException{
    	
    	
    	
        File noSentFile = new File("b103844n_nosents.xml");
        File outFile    = new File("b103844n_nosents_mode2.xml");
        File refFile    = new File("b103844n_mode2_reference.xml");


        System.out.print("-------------Running sentence splitter--------------");
    	
        long start = System.currentTimeMillis();
        XMLSentSplit.processFile(noSentFile.getName(), noSentFile.getParent());
        long end = System.currentTimeMillis();
        
        FileReader fr1 = null;
        FileReader fr2 = null;
        
        fr1 = new FileReader(outFile);
        fr2 = new FileReader(refFile);

        System.out.println("------------Running XML Diff--------------");
        System.out.println("Reference file: " + refFile.getName());
        System.out.println("File under test: " + outFile.getName());

        Diff diff = new Diff(fr1, fr2);
        System.out.println("Similar? " + diff.similar());
        Assert.assertTrue("The XML is not identical", diff.identical());
        System.out.println("Identical? " + diff.identical());
        
        return end - start;
    }
}
