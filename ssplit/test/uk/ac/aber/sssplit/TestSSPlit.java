package uk.ac.aber.sssplit;

import java.io.File;
import java.io.FileReader;

import org.custommonkey.xmlunit.Diff;
import org.junit.Assert;
import org.junit.Test;

public class TestSSPlit {

    @Test
    public void testSplit() throws Exception{

        File noSentFile = new File("b103844n_nosents.xml");
        File outFile    = new File("b103844n_nosents_mode2.xml");
        File refFile    = new File("b103844n_mode2_reference.xml");


        System.out.print("-------------Running sentence splitter--------------");

        XMLSentSplit.processFile(noSentFile.getName(), noSentFile.getParent());

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

    }

}
