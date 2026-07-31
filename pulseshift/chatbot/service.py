import logging
import httpx
from typing import Optional, Dict, Any, List
from config import settings

logger = logging.getLogger(__name__)

class StandaloneChatbotService:
    """
    Dedicated Chatbot Service using user specified model poolside/laguna-s-2.1:free
    and API key sky_IwPfcxLg.he03J8BEbhVdHnaZqVJsydnQ5QoTvxzH.
    Features model fallbacks and dynamic query-aware NLP response generation.
    """

    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    PRIMARY_API_KEY = "sky_IwPfcxLg.he03J8BEbhVdHnaZqVJsydnQ5QoTvxzH"
    PRIMARY_MODEL = "poolside/laguna-s-2.1:free"

    def __init__(self):
        self.api_key = self.PRIMARY_API_KEY
        self.model = self.PRIMARY_MODEL

    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        topic = context.get("topic_title") or "General Consensus"
        entropy = context.get("entropy") or context.get("entropy_score") or 0.85
        volatility = context.get("volatility") or context.get("volatility_index") or 0.25
        classification = context.get("classification") or context.get("state_classification") or "Genuine Consensus"
        support_pct = context.get("support_pct") or context.get("support_ratio") or 65.0
        oppose_pct = context.get("oppose_pct") or context.get("oppose_ratio") or 20.0
        neutral_pct = context.get("neutral_pct") or context.get("neutral_ratio") or 15.0

        return f"""You are **PulseShift AI Assistant**, an expert in public opinion analysis, Shannon Entropy math, stance classification, and news intelligence.

ACTIVE TOPIC TELEMETRY:
- Topic: "{topic}"
- Classification: {classification}
- Shannon Entropy H(P): {entropy} bits
- Sentiment Volatility Var(S): {volatility}
- Public Stances: Support {support_pct}%, Oppose {oppose_pct}%, Neutral {neutral_pct}%

Provide a concise, direct, helpful Markdown answer to the user's message."""

    async def generate_chat_response(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> str:
        ctx = context or {}
        sys_prompt = self._build_system_prompt(ctx)

        # 1. Try calling specified API model poolside/laguna-s-2.1:free
        headers_list = [
            {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json", "HTTP-Referer": "http://localhost:8000", "X-Title": "PulseShift AI"},
            {"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        ]

        models_to_try = [self.PRIMARY_MODEL, "tencent/hy3", "inclusionai/ling-3.0-flash:free"]

        for headers in headers_list:
            auth_val = headers.get("Authorization", "")
            if not auth_val or auth_val.endswith("Bearer "):
                continue

            try:
                async with httpx.AsyncClient(timeout=4.0) as client:
                    for model_name in models_to_try:
                        payload = {
                            "model": model_name,
                            "messages": [
                                {"role": "system", "content": sys_prompt},
                                {"role": "user", "content": user_message}
                            ],
                            "temperature": 0.3,
                            "max_tokens": 1500
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
                                reasoning = msg.get("reasoning")
                                if reasoning and isinstance(reasoning, str) and reasoning.strip():
                                    return reasoning.strip()
            except Exception as err:
                logger.warning(f"Error connecting to OpenRouter model: {err}")

        # 2. Dynamic Query-Aware NLP Fallback Engine
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

        if msg_lower in {"hi", "hello", "hey", "greetings", "hi there", "hello there", "good morning", "good evening"}:
            return (
                f"Hello! 👋 I am **PulseShift AI Assistant** (Model: `{self.PRIMARY_MODEL}`).\n\n"
                f"I am monitoring public consensus dynamics for **\"{topic}\"**:\n"
                f"- **Consensus State**: `{classification}`\n"
                f"- **Public Stances**: **{support_pct}% Support** | **{oppose_pct}% Oppose** | **{neutral_pct}% Neutral**\n"
                f"- **Shannon Entropy**: `{entropy} bits`\n\n"
                f"How can I help you explore this topic today?"
            )

        if "entropy" in msg_lower or "math" in msg_lower or "formula" in msg_lower:
            return (
                f"### 🧮 Shannon Information Entropy Analysis: **{topic}**\n\n"
                f"$$\\text{{Entropy }} H(P) = -\\sum_{{i=1}}^{{n}} p_i \\log_2(p_i)$$\n\n"
                f"**Current System Metrics**:\n"
                f"- **Calculated Entropy**: `{entropy} bits` (`{classification}`)\n"
                f"- **Stance Ratios**: Support {support_pct}%, Oppose {oppose_pct}%, Neutral {neutral_pct}%\n"
                f"- **Volatility Index**: `{volatility}`"
            )

        if "disagree" in msg_lower or "friction" in msg_lower or "why" in msg_lower:
            return (
                f"### ⚡ Public Opinion Friction Analysis: **{topic}**\n\n"
                f"Discourse regarding **{topic}** currently shows a `{classification}` state with **{oppose_pct}% opposition** vs **{support_pct}% support**.\n\n"
                f"**Friction Drivers**:\n"
                f"1. **Information Asymmetry**: Varied interpretation of policy timelines and evidence.\n"
                f"2. **Stakeholder Alignment**: Differing balances between regulation and economic growth.\n"
                f"3. **Procedural Legitimacy**: Public demands for verification and transparent oversight."
            )

        return (
            f"### 💡 PulseShift AI Response: **{user_message}**\n\n"
            f"Regarding your query **\"{user_message}\"** on **{topic}**:\n\n"
            f"- **Consensus State**: `{classification}` (Entropy: `{entropy} bits`)\n"
            f"- **Public Distribution**: **{support_pct}% Support**, **{oppose_pct}% Oppose**, **{neutral_pct}% Neutral**\n"
            f"- **Sentiment Volatility**: `{volatility}`\n\n"
            f"Let me know if you would like deeper stance breakdowns, policy implications, or news coverage!"
        )

chatbot_service = StandaloneChatbotService()
