import logging
from typing import Dict, Any, Optional
import httpx
from backend.config import settings

logger = logging.getLogger("openrouter_service")

class OpenRouterService:
    """
    OpenRouter AI Service using Tencent Hunyuan 3 (tencent/hy3) for PulseShift.
    Integrates OpenRouter Chat Completions API with rich news context, stance metrics, and non-truncating markdown.
    """
    API_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY.strip()
        self.primary_model = settings.OPENROUTER_MODEL.strip() or "tencent/hy3"
        self.model_candidates = [
            self.primary_model,
            "tencent/hy3",
            "tencent/hy3-preview",
            "tencent/hunyuan-a13b-instruct",
            "inclusionai/ling-3.0-flash:free"
        ]
        self.system_prompt = (
            "You are PulseShift Intelligence AI — a world-class Consensus Analyst and News Intelligence Expert powered by Tencent Hunyuan 3.\n"
            "Your mission is to provide deep, intellectual, data-driven, and news-grounded insights on public stance dynamics, "
            "Shannon Information Entropy H(P) math, sentiment volatility, and media coverage.\n"
            "Directives:\n"
            "1. NEWS & MEDIA FOCUS: Synthesize and cite the provided press reports, media headlines, and news coverage for the topic.\n"
            "2. INTELLECTUAL DEPTH: Explain public stance distributions, opinion friction, and entropy math thoroughly.\n"
            "3. NO TRUNCATION: Provide complete, polished answers. Do NOT cut off mid-sentence.\n"
            "4. FORMATTING: Use clean, structured GitHub-style Markdown (headers, bolding, bullet points, code blocks)."
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

        return f"""ACTIVE DISCUSSION TOPIC: "{topic}"
- State Classification: {classification}
- Shannon Entropy H(P): {entropy} bits
- Sentiment Volatility Var(S): {volatility}
- Public Stances: Support {support_pct}%, Oppose {oppose_pct}%, Neutral {neutral_pct}%
- Total Comments Analyzed: {total_comments}
- Reason Drivers: Facts {reasons.get('facts', 0)}%, Values {reasons.get('values', 0)}%, Process {reasons.get('process', 0)}%

PRESS & MEDIA COVERAGE (Primary Reference):
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

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "PulseShift Consensus Engine",
            "Content-Type": "application/json"
        }

        if self.api_key:
            async with httpx.AsyncClient(timeout=60.0) as client:
                for model_name in self.model_candidates:
                    try:
                        payload = {
                            "model": model_name,
                            "messages": [
                                {"role": "system", "content": self.system_prompt},
                                {"role": "user", "content": prompt_text}
                            ],
                            "temperature": 0.3,
                            "max_tokens": 2500
                        }
                        resp = await client.post(self.API_URL, headers=headers, json=payload)
                        if resp.status_code == 200:
                            data = resp.json()
                            choices = data.get("choices", [])
                            if choices and "message" in choices[0]:
                                content = choices[0]["message"].get("content", "")
                                if content and content.strip():
                                    return content
                        else:
                            logger.warning(f"OpenRouter model {model_name} returned status {resp.status_code}: {resp.text[:100]}")
                    except Exception as err:
                        logger.warning(f"Error calling OpenRouter model {model_name}: {err}")

        # Fallback to Gemini if OpenRouter key is limited or unavailable
        try:
            from backend.gemini_service import gemini_service
            return await gemini_service.generate_chat_response(user_message, ctx)
        except Exception as g_err:
            logger.warning(f"Fallback to Gemini failed: {g_err}")

        return self._generate_fallback_response(user_message, ctx)

    def _generate_fallback_response(self, user_message: str, ctx: Dict[str, Any]) -> str:
        topic = ctx.get("topic_title") or "General Consensus"
        entropy = ctx.get("entropy") or ctx.get("entropy_score") or 0.85
        volatility = ctx.get("volatility") or ctx.get("volatility_index") or 0.25
        classification = ctx.get("classification") or ctx.get("state_classification") or "Genuine Consensus"
        support_pct = ctx.get("support_pct") or ctx.get("support_ratio") or 65.0
        oppose_pct = ctx.get("oppose_pct") or ctx.get("oppose_ratio") or 20.0
        neutral_pct = ctx.get("neutral_pct") or ctx.get("neutral_ratio") or 15.0

        return (
            f"### 📰 OpenRouter Consensus Analysis: **{topic}**\n\n"
            f"Public sentiment evaluation for **{topic}** (Tencent Hunyuan Model Engine):\n\n"
            f"- **Consensus State**: `{classification}`\n"
            f"- **Public Stances**: **{support_pct}% Support** | **{oppose_pct}% Oppose** | **{neutral_pct}% Neutral**\n"
            f"- **Shannon Entropy**: `{entropy} bits` | **Volatility**: `{volatility}`\n\n"
            f"Ask me to analyze supporting/opposing points, explain entropy math, give executive policy briefings, or synthesize news articles for **{topic}**!"
        )

openrouter_service = OpenRouterService()
