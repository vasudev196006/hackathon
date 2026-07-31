import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import TopicModel
from .schemas import ChatRequest, ChatResponse
from .service import chatbot_service

logger = logging.getLogger(__name__)

chatbot_router = APIRouter(tags=["Chatbot"])

@chatbot_router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest, db: Session = Depends(get_db)):
    """
    POST /chat
    Dedicated AI Chatbot Endpoint using poolside/laguna-s-2.1:free model.
    """
    message = req.message.strip() if req.message else ""
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    context_payload = dict(req.context) if req.context else {}
    topic_title = req.topic_title or context_payload.get("topic_title")

    if not topic_title:
        try:
            latest_topic = db.query(TopicModel).order_by(TopicModel.created_at.desc()).first()
            if latest_topic:
                topic_title = latest_topic.title
        except Exception:
            pass

    if topic_title:
        context_payload["topic_title"] = topic_title

    reply_text = await chatbot_service.generate_chat_response(message, context_payload)
    
    # Persist interaction log to database
    from models import ChatbotLogModel
    try:
        log_entry = ChatbotLogModel(
            conversation_id=req.conversation_id or "web-session",
            user_query=message,
            ai_response=reply_text,
            model_used=chatbot_service.PRIMARY_MODEL
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to log chatbot interaction: {e}")

    final_topic = context_payload.get("topic_title") or topic_title or "General"
    return ChatResponse(reply=reply_text, topic=final_topic)
