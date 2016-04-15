import it.uniroma1.lcl.babelnet.*;
import it.uniroma1.lcl.babelnet.data.BabelPOS;
import it.uniroma1.lcl.babelnet.data.BabelSenseSource;
import it.uniroma1.lcl.babelnet.resources.WordNetSynsetID;

import java.io.*;
import java.util.HashSet;
import java.util.List;
import java.util.Scanner;
import java.util.Set;

import it.uniroma1.lcl.jlt.util.Language;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;


public class WikipediaDataProvider {


    private static final Log LOGGER = LogFactory.getLog(WikipediaDataProvider.class.getName());


    public static void wordNetSense2WikipediaPageID(String filename) throws FileNotFoundException, UnsupportedEncodingException {

        Scanner in = new Scanner(new FileReader(filename)).useDelimiter("\n");
        String outFilename = "../coarse-wsd/wikipages.txt";
        PrintWriter writer = new PrintWriter(outFilename, "UTF-8");

        Set<String> words = new HashSet<>();
        Set<String> processedSynsets = new HashSet<>();

        BabelNet bn = BabelNet.getInstance();
        int count = 0;
        // WordNet Sense processing.
        while (in.hasNext()) {
            count++;
            if (count % 100 == 0) {
                LOGGER.info(count + " line processed...");
            }
            String [] tokens = in.next().split("\t");
            String word = tokens[0];
            words.add(word);
            String synsetOffset = tokens[3];
            BabelSynset by = bn.getSynset(new WordNetSynsetID(synsetOffset));
            if (by != null) {
                for (BabelSense sense : by.getSenses(BabelSenseSource.WIKI)) {
                    writer.println(word + "\t" + sense.getLemma() + "\t" + synsetOffset + "\t" + sense.getLanguage() +
                            "\t" + sense.getSynsetID().getID() + "\t" + sense.getWordNetOffset());
                    processedSynsets.add(sense.getSynsetID().getID());
                }
            }
            else {
                LOGGER.info("Synset: " + synsetOffset +  " cannot be found");
            }
        }

        // Babelnet Sense Processing
        for(String word: words) {
            // Check it is none, check it is not processed before.
            List<BabelSynset> byl = bn.getSynsets(word, Language.EN, BabelPOS.NOUN, BabelSenseSource.WIKI);
            for (BabelSynset by: byl) {
                String synsetID = by.getId().getID();
                if (!processedSynsets.contains(synsetID)) {
                    for (BabelSense sense : by.getSenses(BabelSenseSource.WIKI)) {
                        writer.println(word + "\t" + sense.getLemma() + "\t" + sense.getSynsetID().getID() + "\t" + sense.getLanguage() +
                                "\t" + sense.getSynsetID().getID() + "\t" + sense.getWordNetOffset());
                    }

                }
            }
        }

        writer.close();
        LOGGER.info("Output file: " + outFilename);
    }

    public static void main(String[] args) throws IOException, InvalidBabelSynsetIDException {
        WikipediaDataProvider.wordNetSense2WikipediaPageID("synset-info.txt");
    }
}