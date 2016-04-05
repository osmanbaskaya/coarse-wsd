import it.uniroma1.lcl.babelnet.*;
import it.uniroma1.lcl.babelnet.data.BabelSenseSource;
import it.uniroma1.lcl.babelnet.resources.ResourceID;
import it.uniroma1.lcl.babelnet.resources.WikidataID;
import it.uniroma1.lcl.babelnet.resources.WordNetSynsetID;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.Scanner;
import java.util.logging.Logger;


public class WikipediaDataProvider {

    private static final Logger LOGGER = Logger.getLogger(WikipediaDataProvider.class.getName());

    public static void wordNetSense2WikipediaPageID(String filename) throws FileNotFoundException {
        Scanner in = new Scanner(new FileReader(filename)).useDelimiter("\n");
        String synsetOffset;

        BabelNet bn = BabelNet.getInstance();
        while (in.hasNext()) {
            synsetOffset = in.next().split("\t")[3];
            BabelSynset by = bn.getSynset(new WordNetSynsetID(synsetOffset));
            if (by != null) {
                for (BabelSense sense : by.getSenses(BabelSenseSource.WIKI)) {
                    System.out.println(sense.getLemma() + "\t" + sense.getLanguage() + "\t" + "\t" + sense.getSynset());
                }
            }
            else {
                LOGGER.info("Synset: " + synsetOffset +  " cannot be found");
            }
        }
    }

    public static void main(String[] args) throws IOException, InvalidBabelSynsetIDException {
        WikipediaDataProvider.wordNetSense2WikipediaPageID("synset-info.txt");
    }
}