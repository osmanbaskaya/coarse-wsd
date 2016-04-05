import it.uniroma1.lcl.babelnet.*;
import it.uniroma1.lcl.babelnet.data.BabelSenseSource;
import it.uniroma1.lcl.babelnet.resources.WordNetSynsetID;

import java.io.*;
import java.util.Scanner;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;


public class WikipediaDataProvider {


    private static final Log LOGGER = LogFactory.getLog(WikipediaDataProvider.class.getName());



    public static void wordNetSense2WikipediaPageID(String filename) throws FileNotFoundException, UnsupportedEncodingException {

        Scanner in = new Scanner(new FileReader(filename)).useDelimiter("\n");
        String outFilename = "../coarse-wsd/wikipages.txt";
        PrintWriter writer = new PrintWriter(outFilename, "UTF-8");

        BabelNet bn = BabelNet.getInstance();
        int count = 0;
        while (in.hasNext()) {
            count++;
            if (count % 100 == 0) {
                LOGGER.info(count + " line processed...");
            }
            String [] tokens = in.next().split("\t");
            String word = tokens[0];
            String synsetOffset = tokens[3];
            BabelSynset by = bn.getSynset(new WordNetSynsetID(synsetOffset));
            if (by != null) {
                for (BabelSense sense : by.getSenses(BabelSenseSource.WIKI)) {
                    writer.println(word + "\t" + sense.getLemma() + "\t" + synsetOffset + "\t" + sense.getLanguage() +
                            "\t" + "\t" + sense.getSynset());
                }
            }
            else {
                LOGGER.info("Synset: " + synsetOffset +  " cannot be found");
            }
        }
        writer.close();
        LOGGER.info("Output file: " + outFilename);
    }

    public static void main(String[] args) throws IOException, InvalidBabelSynsetIDException {
        WikipediaDataProvider.wordNetSense2WikipediaPageID("synset-info.txt");
    }
}