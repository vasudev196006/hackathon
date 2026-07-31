import logging
from typing import Dict, Any, Optional
import httpx
from .config import settings

logger = logging.getLogger("gemini_service")

class GeminiService:
    """
    Google Gemini AI Chatbot Service for PulseShift.
    Intellectual, news-driven AI assistant with non-truncating completions.
    """
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY.strip()
        self.model_candidates = ["gemini-flash-latest", "gemini-pro-latest", "gemini-2.0-flash-lite"]
        self.system_prompt = (
            "You are PulseShift Intelligence AI — a highly intellectual, analytical, and news-anchored Consensus Specialist.\n"
            "Your objective is to provide comprehensive, data-driven, and intellectually rigorous answers to user questions.\n"
            "Key Directives:\n"
            "1. NEWS & MEDIA FOCUS: Heavily reference, synthesize, and cite the provided news articles, media reports, and press coverage for the active topic. Compare media reporting against public stance distribution.\n"
            "2. INTELLECTUAL DEPTH: Explain complex dynamics (Shannon Information Entropy H(P), opinion divergence, volatility, policy risks) thoroughly and with complete mathematical and conceptual clarity.\n"
            "3. NO TRUNCATION: Provide complete, fully articulated explanations. Do NOT cut off mid-sentence.\n"
            "4. FORMATTING: Use clean, polished GitHub-style Markdown with clear section headers, bolding, bullet points, and code blocks."
        )

    def _build_prompt_payload(self, user_message: str, ctx: Dict[str, Any]) -> str:
        topic = ctx.get("topic_title") or "General Consensus"
        classification = ctx.get("classification") or ctx.get("state_classification") or "Genuine Consensus"
        entropy = ctx.get("entropy") or ctx.get("entropy_score") or 0.85
        volatility = ctx.get("volatility") or ctx.get("volatility_index") or 0.25
        support_pct = ctx.get("support_pct") or ctx.get("support_ratio") or 65.0
        oppose_pct = ctx.get("oppose_pct") or ctx.get("oppose_ratio") or 20.0
        neutral_pct = ctx.get("neutral_pct") or ctx.get("neutral_ratio") or 15.0
        total_comments = ctx.get("total_comments", 50)
        reasons = ctx.get("reasons_breakdown") or ctx.get("reason_breakdown") or {"facts": 45, "values": 30, "process": 25}

        support_comments = ctx.get("support_comments", [])
        oppose_comments = ctx.get("oppose_comments", [])
        news_articles = ctx.get("news_articles") or ctx.get("news", [])

        # Format News Articles
        news_lines = []
        if news_articles:
            for idx, n in enumerate(news_articles[:6], 1):
                if isinstance(n, dict):
                    t = n.get("title", "News Headline")
                    src = n.get("source", "Press Source")
                    desc = n.get("description", "")
                    url = n.get("url", "")
                    desc_str = f" - {desc[:150]}..." if desc else ""
                    news_lines.append(f"{idx}. [{t}] ({src}){desc_str} (Link: {url})")
        news_block = "\n".join(news_lines) if news_lines else "No specific news articles available for this topic."

        # Format Comments
        support_sample = "\n".join([f"- \"{c.get('text', c) if isinstance(c, dict) else c}\"" for c in support_comments[:3]]) or "No quotes available."
        oppose_sample = "\n".join([f"- \"{c.get('text', c) if isinstance(c, dict) else c}\"" for c in oppose_comments[:3]]) or "No quotes available."

        return f"""System Directives:
{self.system_prompt}

ACTIVE TOPIC: "{topic}"
- Consensus Classification: {classification}
- Shannon Entropy H(P): {entropy} bits
- Sentiment Volatility Var(S): {volatility}
- Public Stances: Support {support_pct}%, Oppose {oppose_pct}%, Neutral {neutral_pct}%
- Total Comments Sampled: {total_comments}
- Reason Drivers: Facts {reasons.get('facts', 0)}%, Values {reasons.get('values', 0)}%, Process {reasons.get('process', 0)}%

PRESS & NEWS COVERAGE (Primary Reference):
{news_block}

PUBLIC SUPPORT QUOTES:
{support_sample}

PUBLIC OPPOSITION QUOTES:
{oppose_sample}

USER QUERY: "{user_message}"

Generate a complete, intellectual, news-grounded Markdown response answering the user's query thoroughly without truncating."""

    async def generate_chat_response(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> str:
        ctx = context or {}
        prompt_text = self._build_prompt_payload(user_message, ctx)

        if self.api_key:
            async with httpx.AsyncClient(timeout=3.0) as client:
                for model_name in self.model_candidates[:2]:
                    try:
                        url = f"{self.BASE_URL}/{model_name}:generateContent?key={self.api_key}"
                        payload = {
                            "contents": [{"parts": [{"text": prompt_text}]}],
                            "generationConfig": {
                                "temperature": 0.35,
                                "maxOutputTokens": 800
                            }
                        }
                        resp = await client.post(url, json=payload)
                        if resp.status_code == 200:
                            data = resp.json()
                            candidates = data.get("candidates", [])
                            if candidates and "content" in candidates[0]:
                                parts = candidates[0]["content"].get("parts", [])
                                if parts and "text" in parts[0]:
                                    return parts[0]["text"]
                        else:
                            logger.warning(f"Gemini API model {model_name} returned status {resp.status_code}: {resp.text[:100]}")
                            if resp.status_code in (400, 401, 402, 429):
                                break
                    except Exception as err:
                        logger.warning(f"Error calling Gemini model {model_name}: {err}")

        # Dynamic Fallback Consensus Engine if API is unavailable
        return self._generate_fallback_response(user_message, ctx)

    def _generate_fallback_response(self, user_message: str, ctx: Dict[str, Any]) -> str:
        topic = ctx.get("topic_title") or "General Consensus"
        entropy = ctx.get("entropy") or ctx.get("entropy_score") or 0.85
        volatility = ctx.get("volatility") or ctx.get("volatility_index") or 0.25
        classification = ctx.get("classification") or ctx.get("state_classification") or "Genuine Consensus"
        support_pct = ctx.get("support_pct") or ctx.get("support_ratio") or 65.0
        oppose_pct = ctx.get("oppose_pct") or ctx.get("oppose_ratio") or 20.0
        neutral_pct = ctx.get("neutral_pct") or ctx.get("neutral_ratio") or 15.0
        news_articles = ctx.get("news_articles") or ctx.get("news", [])

        news_str = ""
        if news_articles and isinstance(news_articles[0], dict):
            news_str = f"\n\n**Key Media Report**: *\"{news_articles[0].get('title', '')}\"* ({news_articles[0].get('source', 'Press')})"

        return (
            f"### 📰 Intellectual Analysis & Media Briefing: **{topic}**\n\n"
            f"Synthesizing recent press coverage and public stance dynamics for **{topic}**:\n\n"
            f"**1. Public Stance Ratio**: Support **{support_pct}%** | Oppose **{oppose_pct}%** | Neutral **{neutral_pct}%**\n"
            f"**2. Information Entropy**: `{entropy} bits` (Classification: `{classification}`)\n"
            f"**3. Sentiment Volatility**: `{volatility}`"
            f"{news_str}\n\n"
            f"**Analytical Takeaway**: The consensus dynamics around **{topic}** demonstrate key tension points between public sentiment and media reporting, requiring transparent policy communication."
        )

gemini_service = GeminiService()
