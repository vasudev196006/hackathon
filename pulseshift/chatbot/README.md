# PulseShift Chatbot Package

Dedicated chatbot integration package using `poolside/laguna-s-2.1:free` model and user API key `sky_IwPfcxLg.he03J8BEbhVdHnaZqVJsydnQ5QoTvxzH`.

## Components:
- `service.py`: StandaloneChatbotService calling OpenRouter API with fallbacks.
- `routes.py`: FastAPI router `@chatbot_router.post("/chat")`.
- `schemas.py`: Pydantic request/response validation schemas.
- `chatbot.js`: Glassmorphism floating UI chatbot widget.
- `chatbot.css`: Dark-mode sleek responsive styles.
