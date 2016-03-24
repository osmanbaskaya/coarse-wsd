import it.uniroma1.lcl.babelnet.*;
import it.uniroma1.lcl.babelnet.data.BabelSenseSource;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.Scanner;

public class WikipediaDataProvider {

    public static void wordNetSense2WikipediaPageID(String filename) throws FileNotFoundException {
        Scanner in = new Scanner(new FileReader(filename));
        String line;

        BabelNet bn = BabelNet.getInstance();
        while (in.hasNext()) {
            line = in.next().trim();
            BabelSynset by = bn.getSynset(new BabelSynsetID(line));
            for (BabelSense sense : by.getSenses(BabelSenseSource.WIKIDATA)) {
                String sensekey = sense.getSensekey();
                System.out.println(sense.getLemma() + "\t" + sense.getLanguage() + "\t" + sensekey);
            }
        }
    }

    public static void main(String[] args) throws IOException, InvalidBabelSynsetIDException {
        WikipediaDataProvider.wordNetSense2WikipediaPageID("sense-offsets.txt");
    }
}