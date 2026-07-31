import numpy as np
from scipy.stats import entropy as scipy_entropy
from typing import List, Dict, Any, Tuple

class EntropyEngine:
    """
    Mathematical engine to calculate Shannon Entropy, Volatility, and Reason Divergence
    from analyzed comment distributions.
    """

    @staticmethod
    def calculate_shannon_entropy(stances: List[str]) -> float:
        """
        Calculates Shannon Entropy H(P) = - sum(p_i * log2(p_i)) over stance distribution.
        Stances can be 'support', 'oppose', 'neutral'.
        Max entropy for 3 categories is log2(3) ~ 1.5849 bits.
        """
        if not stances:
            return 0.0

        counts = {
            "support": stances.count("support"),
            "oppose": stances.count("oppose"),
            "neutral": stances.count("neutral")
        }
        total = len(stances)
        if total == 0:
            return 0.0

        probabilities = [count / total for count in counts.values() if count > 0]
        if not probabilities:
            return 0.0

        # Calculate Shannon entropy using base 2
        h = float(scipy_entropy(probabilities, base=2))
        return round(h, 4)

    @staticmethod
    def calculate_volatility(scores: List[float]) -> float:
        """
        Calculates sentiment volatility as the standard deviation of comment stance scores.
        Scores typically range from -1.0 (strongly oppose) to +1.0 (strongly support).
        """
        if not scores or len(scores) < 2:
            return 0.0

        arr = np.array(scores, dtype=np.float64)
        vol = float(np.std(arr, ddof=1))
        return round(vol, 4)

    @staticmethod
    def calculate_reason_divergence(reasons: List[str]) -> float:
        """
        Calculates reason divergence (entropy over facts, values, process).
        High divergence indicates people agree or disagree for fundamentally different types of reasons.
        """
        if not reasons:
            return 0.0

        counts = {
            "facts": reasons.count("facts"),
            "values": reasons.count("values"),
            "process": reasons.count("process")
        }
        total = len(reasons)
        if total == 0:
            return 0.0

        probs = [c / total for c in counts.values() if c > 0]
        div = float(scipy_entropy(probs, base=2))
        return round(div, 4)

    @staticmethod
    def compute_full_metrics(analyzed_comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Computes all metrics for a given batch of analyzed comments.
        """
        if not analyzed_comments:
            return {
                "total_comments": 0,
                "support_pct": 0.0,
                "oppose_pct": 0.0,
                "neutral_pct": 0.0,
                "avg_confidence": 0.0,
                "entropy": 0.0,
                "volatility": 0.0,
                "reasons_breakdown": {"facts": 0, "values": 0, "process": 0},
                "reason_divergence": 0.0
            }

        total = len(analyzed_comments)
        stances = [c.get("stance", "neutral") for c in analyzed_comments]
        scores = [c.get("score", 0.0) for c in analyzed_comments]
        reasons = [c.get("reason", "facts") for c in analyzed_comments]
        confidences = [c.get("confidence", 0.8) for c in analyzed_comments]

        sup_count = stances.count("support")
        opp_count = stances.count("oppose")
        neu_count = stances.count("neutral")

        shannon_h = EntropyEngine.calculate_shannon_entropy(stances)
        volatility = EntropyEngine.calculate_volatility(scores)
        reason_div = EntropyEngine.calculate_reason_divergence(reasons)

        facts_cnt = reasons.count("facts")
        values_cnt = reasons.count("values")
        process_cnt = reasons.count("process")

        return {
            "total_comments": total,
            "support_pct": round((sup_count / total) * 100, 1),
            "oppose_pct": round((opp_count / total) * 100, 1),
            "neutral_pct": round((neu_count / total) * 100, 1),
            "avg_confidence": round(float(np.mean(confidences)), 2) if confidences else 0.0,
            "entropy": shannon_h,
            "volatility": volatility,
            "reasons_breakdown": {
                "facts": facts_cnt,
                "values": values_cnt,
                "process": process_cnt
            },
            "reason_divergence": reason_div
        }
