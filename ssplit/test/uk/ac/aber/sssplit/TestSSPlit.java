package uk.ac.aber.sssplit;

import java.io.File;
import org.junit.Test;
import org.junit.Before;
import org.junit.Assert.*;

public class TestSSPlit {

    @Test
    public void testSplit(){

        File noSentFile = new File("b103844n_nosents.xml");

        XMLSentSplit.processFile(noSentFile.getName(), noSentFile.getParent());
    
    }

}
