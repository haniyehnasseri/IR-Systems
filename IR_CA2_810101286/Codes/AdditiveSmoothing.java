package org.lemurproject.galago.core.retrieval.iterator.scoring;

import org.lemurproject.galago.core.retrieval.RequiredParameters;
import org.lemurproject.galago.core.retrieval.RequiredStatistics;
import org.lemurproject.galago.core.retrieval.iterator.CountIterator;
import org.lemurproject.galago.core.retrieval.iterator.DeltaScoringIterator;
import org.lemurproject.galago.core.retrieval.iterator.LengthsIterator;
import org.lemurproject.galago.core.retrieval.iterator.ScoringFunctionIterator;
import org.lemurproject.galago.core.retrieval.processing.ScoringContext;
import org.lemurproject.galago.core.retrieval.query.NodeParameters;

import java.io.IOException;

/**
 * A ScoringIterator that makes use of the AdditiveSmoothing score function for
 * converting a count into a score.
 *
 * @author sjh
 */
@RequiredStatistics(statistics = {"collectionLength", "nodeFrequency", "maximumCount", "vocabCount"})
@RequiredParameters(parameters = {"delta"})
public class AdditiveSmoothing extends ScoringFunctionIterator
        implements DeltaScoringIterator {

    // delta
    private final double weight;
    private final double min; // min score
    private final double max; // max tf
    private final double weightedMin;
    private final double weightedMax;
    private final double weightedMaxDiff;
    // stats
    private final double delta;
    private final double vocabCount;

    public AdditiveSmoothing(NodeParameters p, LengthsIterator ls, CountIterator it)
            throws IOException {
        super(p, ls, it);

        // stats
        delta = p.get("delta", 100D);

        // delta
        weight = p.get("w", 1.0);

        // the max score can be bounded where the maxtf is also the length of that document (a long document of just tf)
        max = additiveSmoothingScore(p.getLong("maximumCount"), p.getLong("maximumCount"));

        // the min score is an over estimate for when the iterator does NOT contain the term (document freq of zero)
        //   MAX-SCORE requires this to be over estimated, otherwise you will lose documents
        //   empirically average document length is a good number (even if its NOT an overestimate of min possible score)
        min = additiveSmoothingScore(0, 1);

        weightedMin = weight * min;
        weightedMax = weight * max;
        weightedMaxDiff = weightedMax - weightedMin;

        vocabCount = p.getLong("vocabCount");
    }

    @Override
    public double minimumScore() {
        return min;
    }

    @Override
    public double maximumScore() {
        return max;
    }

    @Override
    public double getWeight() {
        return weight;
    }

    @Override
    public double deltaScore(ScoringContext c) {
        return weight * (max - score(c));
    }

    @Override
    public double maximumWeightedScore() {
        return weightedMax;
    }

    @Override
    public double minimumWeightedScore() {
        return weightedMin;
    }

    @Override
    public double maximumDifference() {
        return weightedMaxDiff;
    }

    @Override
    public double score(ScoringContext c) {
        int count = ((CountIterator) iterator).count(c);
        int length = this.lengthsIterator.length(c);
        return additiveSmoothingScore(count, length);
    }

    private double additiveSmoothingScore(double count, double length) {
        double numerator = count + delta;
        double denominator = length + delta * vocabCount;
        return numerator / denominator;
    }
}
