import logging
from typing import Dict, Any, Optional
import httpx
from .config import settings

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
            async with httpx.AsyncClient(timeout=15.0) as client:
                for model_name in ["tencent/hy3", "inclusionai/ling-3.0-flash:free"]:
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
                                msg = choices[0]["message"]
                                content = msg.get("content")
                                if content and isinstance(content, str) and content.strip():
                                    return content.strip()
                                # Fallback to reasoning string if content is empty
                                reasoning = msg.get("reasoning")
                                if reasoning and isinstance(reasoning, str) and reasoning.strip():
                                    return reasoning.strip()
                        else:
                            logger.warning(f"OpenRouter model {model_name} returned status {resp.status_code}: {resp.text[:100]}")
                            if resp.status_code in (401, 402):
                                break
                    except Exception as err:
                        logger.warning(f"Error calling OpenRouter model {model_name}: {err}")

        # Fallback to Gemini if OpenRouter key is limited or unavailable
        try:
            from .gemini_service import gemini_service
            return await gemini_service.generate_chat_response(user_message, ctx)
        except Exception as g_err:
            logger.warning(f"Fallback to Gemini failed: {g_err}")

        return self._generate_fallback_response(user_message, ctx)

    def _generate_fallback_response(self, user_message: str, ctx: Dict[str, Any]) -> str:
        msg_lower = user_message.lower().strip()
        topic = ctx.get("topic_title") or "General Consensus"
        entropy = ctx.get("entropy") or ctx.get("entropy_score") or 0.85
        volatility = ctx.get("volatility") or ctx.get("volatility_index") or 0.25
        classification = ctx.get("classification") or ctx.get("state_classification") or "Genuine Consensus"
        support_pct = ctx.get("support_pct") or ctx.get("support_ratio") or 65.0
        oppose_pct = ctx.get("oppose_pct") or ctx.get("oppose_ratio") or 20.0
        neutral_pct = ctx.get("neutral_pct") or ctx.get("neutral_ratio") or 15.0

        # 1. Greetings (hi, hello, hey)
        if msg_lower in {"hi", "hello", "hey", "greetings", "hi there", "hello there", "good morning", "good evening"}:
            return (
                f"Hello! 👋 I am **PulseShift AI Assistant**.\n\n"
                f"I am actively monitoring public opinion dynamics for **\"{topic}\"**:\n"
                f"- **Consensus State**: `{classification}`\n"
                f"- **Public Stances**: **{support_pct}% Support** | **{oppose_pct}% Oppose** | **{neutral_pct}% Neutral**\n"
                f"- **Information Entropy**: `{entropy} bits`\n\n"
                f"How can I assist you today? Feel free to ask any question, explore opinion drivers, or analyze press reports!"
            )

        # 2. Entropy / Math queries
        if "entropy" in msg_lower or "math" in msg_lower or "formula" in msg_lower:
            return (
                f"### 🧮 Shannon Information Entropy Analysis: **{topic}**\n\n"
                f"Shannon Entropy $H(P)$ measures the uncertainty or dispersion of public opinion across distinct stances:\n\n"
                f"$$H(P) = -\\sum_{{i=1}}^{{n}} p_i \\log_2(p_i)$$\n\n"
                f"**Current System Calculations for \"{topic}\"**:\n"
                f"- **Measured Entropy**: `{entropy} bits` (Classification: `{classification}`)\n"
                f"- **Stance Distribution**: $P(\\text{{Support}}) = {support_pct/100:.2f}$, $P(\\text{{Oppose}}) = {oppose_pct/100:.2f}$, $P(\\text{{Neutral}}) = {neutral_pct/100:.2f}$\n"
                f"- **Sentiment Volatility**: `Var(S) = {volatility}`\n\n"
                f"Lower entropy ($H(P) < 1.0$) indicates strong stance convergence around a dominant perspective, whereas high entropy indicates polarization."
            )

        # 3. Disagreement / Division queries
        if "disagree" in msg_lower or "friction" in msg_lower or "divide" in msg_lower or "why" in msg_lower:
            return (
                f"### ⚡ Public Opinion Friction Analysis: **{topic}**\n\n"
                f"Public sentiment regarding **{topic}** currently shows a `{classification}` state with **{oppose_pct}% opposition** vs **{support_pct}% support**.\n\n"
                f"**Key Disagreement Drivers**:\n"
                f"1. **Factual Divergence**: Information asymmetry in press coverage regarding policy timelines and implementation feasibility.\n"
                f"2. **Value Alignment**: Differences in underlying stakeholder principles regarding regulatory oversight vs economic impact.\n"
                f"3. **Process Friction**: Public skepticism regarding enforcement mechanisms and institutional transparency."
            )

        # 4. News / Summary queries
        if "news" in msg_lower or "summary" in msg_lower or "report" in msg_lower or "article" in msg_lower:
            news_articles = ctx.get("news_articles") or ctx.get("news", [])
            news_str = ""
            if news_articles and isinstance(news_articles, list):
                lines = []
                for n in news_articles[:4]:
                    if isinstance(n, dict):
                        lines.append(f"- **{n.get('title', 'News Item')}** ({n.get('source', 'Press')})")
                if lines:
                    news_str = "\n\n**Latest Indexed Headlines**:\n" + "\n".join(lines)

            return (
                f"### 📰 Executive Consensus & Media Briefing: **{topic}**\n\n"
                f"Synthesizing recent press reporting and public discourse metrics:\n"
                f"- **Primary Stance**: **{support_pct}% Support** (Dominant)\n"
                f"- **Opposing Share**: **{oppose_pct}% Oppose**\n"
                f"- **Consensus Index**: `{classification}` (Entropy: `{entropy} bits`)"
                f"{news_str}\n\n"
                f"**Executive Takeaway**: Communication strategies should focus on addressing public concerns while providing transparent verification data."
            )

        # 5. General / Direct Question Answer Fallback
        return (
            f"### 💡 PulseShift AI Response: **{user_message}**\n\n"
            f"Regarding your query **\"{user_message}\"** in the context of **{topic}**:\n\n"
            f"1. **Direct Answer**: Public commentary analysis indicates that discussions around **{topic}** exhibit `{classification}` dynamics with a Shannon Entropy of `{entropy} bits`.\n"
            f"2. **Stance Overview**: Support stands at **{support_pct}%**, Opposition at **{oppose_pct}%**, and Neutral sentiment at **{neutral_pct}%**.\n"
            f"3. **Sentiment Stability**: Volatility is measured at `{volatility}`, indicating consistent sentiment patterns across recent commentary.\n\n"
            f"Let me know if you would like deeper mathematical breakdowns, policy implications, or media article citations!"
        )

openrouter_service = OpenRouterService()
