import java.io.*;
import java.net.*;
import java.util.*;
import java.util.regex.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.zip.*;

import edu.stanford.nlp.util.*;
import edu.stanford.nlp.semgraph.*;

import edu.stanford.nlp.ling.*;
import edu.stanford.nlp.ling.CoreAnnotations.*;
import edu.stanford.nlp.pipeline.*;
import edu.stanford.nlp.util.CoreMap;
import edu.stanford.nlp.trees.*;
import edu.stanford.nlp.trees.TreeCoreAnnotations.*;
import edu.stanford.nlp.semgraph.SemanticGraphCoreAnnotations.CollapsedCCProcessedDependenciesAnnotation;

import edu.ucla.sspace.matrix.*;
import edu.ucla.sspace.util.*;
import edu.ucla.sspace.vector.*;

public class Lemmatize {


    static final java.util.Properties props = new java.util.Properties();
    static {
        props.put("annotators", "tokenize, ssplit, pos, lemma");
    }

    static final ThreadLocal<StanfordCoreNLP> pipelines
        = new ThreadLocal<StanfordCoreNLP>();

    static final AtomicInteger numProcessed = new AtomicInteger();

    static final List<File> files = new ArrayList<File>();

    public static void main(String[] args) throws Exception {

        final File inputDir = new File(args[0]);

        for (File f : inputDir.listFiles()) {
            String n = f.getName();
            System.out.println(n);
            if (n.endsWith(".txt")&& !(n.contains(".tw") || n.contains(".lem")))
                files.add(f);
        }

        System.out.printf("Loaded %d files to process%n", files.size());



        files.parallelStream().forEach(f -> {
                String n = f.getName().replace(".txt", ".lem.txt");
                File outputFile = new File(f.getParentFile(), n);
                process(f, outputFile);
            });
    }

    static void process(File inputFile, File outputFile) {
        System.out.println("Processing " + inputFile);
        try {
            PrintWriter pw = new PrintWriter(outputFile);
            String target = inputFile.getName().split("\\.")[0];

            for (String line : new LineReader(inputFile)) {
                String[] cols = line.split("\t");
                String text = cols[0].replace("<target>", "");
                cols[0] = clean(text, target);
                pw.println(String.join("\t", cols));
            }
            pw.close();
                                             
            int i = numProcessed.incrementAndGet();
            if (i % 100 == 0)
                System.out.printf("Processed %d/%d dissertations%n", i, 
                                  files.size());
        } catch (Throwable t) {
            t.printStackTrace();
        }
    }

    static String clean(String s, String target) {
        Annotation document = new Annotation(s);
        getPipeline().annotate(document);

        StringBuilder sb = new StringBuilder();
        for (CoreMap sentence : document.get(SentencesAnnotation.class)) {
            for (CoreLabel token: sentence.get(TokensAnnotation.class)) { 
                String t = token.get(LemmaAnnotation.class);
                if (t.equals(target))
                    sb.append("<target>").append(t).append("<target>").append(' ');
                else
                    sb.append(t).append(' ');
                
            }
        }
        if (sb.length() > 0)
            sb.setLength(sb.length() - 1);
        return sb.toString();
    }


    static StanfordCoreNLP getPipeline() {
        StanfordCoreNLP p = pipelines.get();
        if (p == null) {
            p = new StanfordCoreNLP(props);        
            pipelines.set(p);
        }
        return p;
    }
}