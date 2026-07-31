from .config import settings

class ConsensusClassifier:
    """
    Classifies public discussion consensus state based on Shannon Entropy,
    Score Volatility, Stance Distributions, and Reason Divergence.
    """

    @staticmethod
    def classify(
        entropy: float,
        volatility: float,
        support_pct: float,
        oppose_pct: float,
        neutral_pct: float,
        reason_divergence: float = 0.0
    ) -> str:
        """
        Determines the state of consensus:
        - Genuine Consensus
        - Fragile Consensus
        - False Convergence
        - Polarized Disagreement
        - Emerging Alignment
        """
        dominant_stance_pct = max(support_pct, oppose_pct)

        # 1. False Convergence Check: Low Stance Entropy, but high reason divergence
        if entropy <= settings.GENUINE_CONSENSUS_ENTROPY_MAX and reason_divergence >= settings.FALSE_CONVERGENCE_REASON_DIVERGENCE_MIN:
            return "False Convergence"

        # 2. Genuine Consensus Check: Low Entropy, Low Volatility, strong majority
        if (
            entropy <= settings.GENUINE_CONSENSUS_ENTROPY_MAX
            and volatility <= settings.GENUINE_CONSENSUS_VOLATILITY_MAX
            and dominant_stance_pct >= 65.0
        ):
            return "Genuine Consensus"

        # 3. Fragile Consensus Check: Moderate/Low Entropy, but High Volatility or moderate dominant stance
        if (
            dominant_stance_pct >= 55.0
            and (volatility > settings.GENUINE_CONSENSUS_VOLATILITY_MAX or entropy > settings.GENUINE_CONSENSUS_ENTROPY_MAX)
        ):
            return "Fragile Consensus"

        # 4. Polarized Disagreement Check: High Entropy and High Volatility
        if entropy >= 1.1 or (support_pct >= 35.0 and oppose_pct >= 35.0):
            return "Polarized Disagreement"

        # 5. Default / Emerging Alignment
        if neutral_pct >= 45.0:
            return "Emerging Alignment"

        return "High Entropy Dispersal"

    @staticmethod
    def generate_ai_insight_summary(
        topic_title: str,
        total_comments: int,
        support_pct: float,
        oppose_pct: float,
        neutral_pct: float,
        entropy: float,
        volatility: float,
        classification: str,
        reasons_breakdown: dict
    ) -> str:
        """
        Generates a human-readable executive analysis summary based on quantitative metrics.
        """
        facts_cnt = reasons_breakdown.get("facts", 0)
        values_cnt = reasons_breakdown.get("values", 0)
        process_cnt = reasons_breakdown.get("process", 0)
        top_reason = max(reasons_breakdown, key=reasons_breakdown.get) if reasons_breakdown else "facts"

        summary = f"{support_pct}% of commenters express support regarding '{topic_title}', while {oppose_pct}% oppose and {neutral_pct}% remain neutral. "

        if classification == "Genuine Consensus":
            summary += f"Public discourse demonstrates strong **Genuine Consensus** with low Shannon Entropy ({entropy:.2f}) and minimal sentiment volatility ({volatility:.2f}). Most arguments are anchored in {top_reason}."
        elif classification == "Fragile Consensus":
            summary += f"While a majority appears supportive, consensus remains **Fragile** due to elevated sentiment volatility ({volatility:.2f}) and shifting commenter conviction."
        elif classification == "False Convergence":
            summary += f"Superficial agreement hides a state of **False Convergence**. Although stance scores appear aligned, commenters rely on diverging {top_reason} justifications."
        elif classification == "Polarized Disagreement":
            summary += f"The public discourse is marked by severe **Polarized Disagreement** with high Shannon Entropy ({entropy:.2f}) and significant volatility ({volatility:.2f}). Supporters and opponents present opposing core values."
        else:
            summary += f"The debate exhibits **{classification}** (Entropy: {entropy:.2f}, Volatility: {volatility:.2f}). Discussion is primarily driven by {top_reason}-based commentary."

        return summary
