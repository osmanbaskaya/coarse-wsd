import it.uniroma1.lcl.babelnet.BabelNet;
import it.uniroma1.lcl.babelnet.BabelSense;
import it.uniroma1.lcl.babelnet.BabelSynset;
import it.uniroma1.lcl.babelnet.InvalidBabelSynsetIDException;
import it.uniroma1.lcl.babelnet.data.BabelPOS;
import it.uniroma1.lcl.babelnet.data.BabelSenseSource;
import it.uniroma1.lcl.babelnet.resources.WordNetSynsetID;
import it.uniroma1.lcl.jlt.util.Language;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import java.io.*;
import java.util.*;


public class WikipediaDataProvider {


    private static final Log LOGGER = LogFactory.getLog(WikipediaDataProvider.class.getName());

    private static Map<String, List<String[]>> createWordMap(String filename) throws FileNotFoundException {
        Map<String, List<String []>> wordMap = new HashMap<>();
        Scanner in = new Scanner(new FileReader(filename)).useDelimiter("\n");
        List<String []> lineList;
        while (in.hasNext()) {
            String[] tokens = in.next().split("\t");
            String word = tokens[0];
            if (wordMap.containsKey(word)) {
                lineList = wordMap.get(word);
            } else {
                lineList = new ArrayList<>();
                wordMap.put(word, lineList);
            }
            lineList.add(tokens);
        }
        return wordMap;
    }

    private static void run(Map<String, List<String []>> wordMap, PrintWriter writer) {
        // WordNet Sense processing.
        BabelNet bn = BabelNet.getInstance();
        LOGGER.info("Total number of words that will be processed: " + wordMap.size());
        int count = 0;
        for (Map.Entry<String, List<String[]>> entry : wordMap.entrySet()) {
            String word = entry.getKey();
            LOGGER.info(++count + ". " + word);
            Set<String> processedSynsets = new HashSet<>();
            for (String[] tokens : entry.getValue()) {
                String synsetOffset = tokens[3];
                BabelSynset by = bn.getSynset(new WordNetSynsetID(synsetOffset));
                if (by != null) {
                    for (BabelSense sense : by.getSenses(BabelSenseSource.WIKI)) {
                        writer.println(word + "\t" + sense.getLemma() + "\t" + synsetOffset + "\t" + sense.getLanguage() +
                                "\t" + sense.getSynsetID().getID() + "\t" + sense.getWordNetOffset());
                        processedSynsets.add(sense.getSynsetID().getID());
                    }
                } else {
                    LOGGER.info("Synset: " + synsetOffset + " cannot be found");
                }
            }

            // BabelNet Sense Processing
            List<BabelSynset> byl = bn.getSynsets(word, Language.EN, BabelPOS.NOUN, BabelSenseSource.WIKI);
            for (BabelSynset by: byl) {
                String synsetID = by.getId().getID();
                if (!processedSynsets.contains(synsetID)) {
                    for (BabelSense sense : by.getSenses(BabelSenseSource.WIKI)) {
                        writer.println(word + "\t" + sense.getLemma() + "\t" + sense.getSynsetID().getID() + "\t" +
                                sense.getLanguage() + "\t" + sense.getSynsetID().getID() + "\t" + sense.getWordNetOffset());
                    }

                }
            }
        }
    }

    private static void wordNetSense2WikipediaPageID(String filename) throws FileNotFoundException, UnsupportedEncodingException {

        Map<String, List<String[]>> wordMap = createWordMap(filename);

        String outFilename = "../coarse-wsd/semcor-pages.txt";
        PrintWriter writer = new PrintWriter(outFilename, "UTF-8");
        try {
            run(wordMap, writer);
        }
        catch (RuntimeException e) {
            // Most likely it reaches daily requests limit for BabelNet.
            writer.close();
        }


        writer.close();
        LOGGER.info("Output file: " + outFilename);
    }

    public static void main(String[] args) throws IOException, InvalidBabelSynsetIDException {
        WikipediaDataProvider.wordNetSense2WikipediaPageID("semcor-synset-info.txt");
    }
}