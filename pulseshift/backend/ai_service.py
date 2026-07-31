import json
import logging
import random
import re
from typing import List, Dict, Any, Optional
from config import settings

logger = logging.getLogger(__name__)

class AIService:
    """
    Modular AI Service supporting Anthropic Claude, OpenAI, and Heuristic NLP Fallback.
    Analyzes YouTube comments to extract stance, score, reason type, emotion, and confidence.
    """

    def __init__(self):
        self.anthropic_client = None
        self.openai_client = None

        if settings.has_anthropic_key:
            try:
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                logger.info("Anthropic Claude client initialized.")
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic client: {e}")

        if settings.has_openai_key:
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI client initialized.")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")

    def analyze_comment(self, comment_text: str, topic_title: str) -> Dict[str, Any]:
        """
        Analyzes a single comment or batch of comments.
        Tries Anthropic Claude first, then OpenAI, then falls back to Heuristic NLP.
        """
        if self.anthropic_client:
            res = self._analyze_with_anthropic(comment_text, topic_title)
            if res:
                return res

        if self.openai_client:
            res = self._analyze_with_openai(comment_text, topic_title)
            if res:
                return res

        return self._heuristic_nlp_analysis(comment_text, topic_title)

    def analyze_batch(self, comments: List[Dict[str, Any]], topic_title: str) -> List[Dict[str, Any]]:
        """
        Analyzes a batch of comments concurrently or sequentially.
        """
        results = []
        for item in comments:
            analysis = self.analyze_comment(item["text"], topic_title)
            item.update(analysis)
            results.append(item)
        return results

    def _analyze_with_anthropic(self, comment_text: str, topic_title: str) -> Optional[Dict[str, Any]]:
        try:
            prompt = self._build_prompt(comment_text, topic_title)
            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=250,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            raw_content = response.content[0].text.strip()
            return self._parse_ai_json(raw_content)
        except Exception as e:
            logger.error(f"Anthropic AI analysis error: {e}")
            return None

    def _analyze_with_openai(self, comment_text: str, topic_title: str) -> Optional[Dict[str, Any]]:
        try:
            prompt = self._build_prompt(comment_text, topic_title)
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            raw_content = response.choices[0].message.content.strip()
            return self._parse_ai_json(raw_content)
        except Exception as e:
            logger.error(f"OpenAI analysis error: {e}")
            return None

    def _build_prompt(self, comment_text: str, topic_title: str) -> str:
        return f"""You are a public sentiment & consensus analyst.
Analyze the following public comment regarding the topic: "{topic_title}".

Comment: "{comment_text}"

Return ONLY a JSON object with no markdown formatting or extra text:
{{
  "stance": "support" | "oppose" | "neutral",
  "score": <float between -1.0 and 1.0, where -1.0 is strongly oppose and 1.0 is strongly support>,
  "reason": "facts" | "values" | "process",
  "emotion": "<dominant emotion word e.g. hope, anger, skepticism, optimism, frustration, curiosity>",
  "confidence": <float between 0.0 and 1.0>
}}
"""

    def _parse_ai_json(self, raw_text: str) -> Optional[Dict[str, Any]]:
        try:
            cleaned = raw_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned)
            # Validate fields
            stance = str(data.get("stance", "neutral")).lower()
            if stance not in ["support", "oppose", "neutral"]:
                stance = "neutral"

            reason = str(data.get("reason", "facts")).lower()
            if reason not in ["facts", "values", "process"]:
                reason = "facts"

            return {
                "stance": stance,
                "score": float(data.get("score", 0.0)),
                "reason": reason,
                "emotion": str(data.get("emotion", "neutral")).capitalize(),
                "confidence": max(0.0, min(1.0, float(data.get("confidence", 0.85))))
            }
        except Exception as e:
            logger.warning(f"Failed to parse AI JSON response: {e}")
            return None

    def _heuristic_nlp_analysis(self, comment_text: str, topic_title: str) -> Dict[str, Any]:
        """
        Rule-based NLP Fallback when AI APIs are unconfigured or unavailable.
        Uses sentiment keywords, syntactic structure, and heuristic indicators.
        """
        text_lower = comment_text.lower()

        # Keywords dictionary
        support_kw = ["love", "great", "awesome", "amazing", "support", "future", "good", "agree", "best", "promising", "yes", "incredible", "essential", "advantage", "benefit", "efficient"]
        oppose_kw = ["hate", "bad", "terrible", "worst", "fail", "stupid", "scam", "wrong", "expensive", "disaster", "never", "no", "problem", "useless", "flaw", "risk", "hazard", "threat"]

        facts_kw = ["data", "cost", "percent", "study", "research", "number", "stats", "battery", "price", "dollar", "kwh", "miles", "range", "proven", "test", "science"]
        values_kw = ["morals", "ethics", "rights", "freedom", "future", "children", "environment", "nature", "community", "culture", "belief", "fair", "justice"]
        process_kw = ["policy", "law", "government", "implementation", "infrastructure", "step", "rules", "regulation", "timeline", "grid", "build", "management"]

        sup_score = sum(1 for w in support_kw if w in text_lower)
        opp_score = sum(1 for w in oppose_kw if w in text_lower)

        if sup_score > opp_score:
            stance = "support"
            score = min(1.0, 0.3 + (sup_score * 0.25))
            emotion = random.choice(["Optimism", "Enthusiasm", "Hope", "Confidence"])
        elif opp_score > sup_score:
            stance = "oppose"
            score = max(-1.0, -0.3 - (opp_score * 0.25))
            emotion = random.choice(["Skepticism", "Frustration", "Concern", "Anger"])
        else:
            stance = "neutral"
            score = 0.0
            emotion = random.choice(["Curiosity", "Indifference", "Pragmatism", "Objectivity"])

        # Determine Reason type
        f_cnt = sum(1 for w in facts_kw if w in text_lower)
        v_cnt = sum(1 for w in values_kw if w in text_lower)
        p_cnt = sum(1 for w in process_kw if w in text_lower)

        if f_cnt >= v_cnt and f_cnt >= p_cnt:
            reason = "facts"
        elif v_cnt >= f_cnt and v_cnt >= p_cnt:
            reason = "values"
        else:
            reason = "process"

        confidence = min(0.98, max(0.65, 0.70 + (abs(score) * 0.2)))

        return {
            "stance": stance,
            "score": round(score, 2),
            "reason": reason,
            "emotion": emotion,
            "confidence": round(confidence, 2)
        }

ai_service = AIService()
