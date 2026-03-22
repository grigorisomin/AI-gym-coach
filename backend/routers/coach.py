from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session

from db.database import get_session, CoachMessage
from services import llm_service
from sqlmodel import select

router = APIRouter(prefix="/coach", tags=["coach"])

SessionDep = Annotated[Session, Depends(get_session)]


class ChatRequest(BaseModel):
    message: str
    stream: bool = False


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, session: SessionDep):
    """Send a message to the AI coach and get a response."""
    if req.stream:
        def generator():
            for token in llm_service.chat_stream(session, req.message):
                yield token

        return StreamingResponse(generator(), media_type="text/plain")

    try:
        reply = llm_service.chat(session, req.message)
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {str(e)}")


@router.get("/history")
def get_history(session: SessionDep, limit: int = 50):
    """Return recent chat history."""
    messages = session.exec(
        select(CoachMessage)
        .order_by(CoachMessage.created_at.desc())
        .limit(limit)
    ).all()
    return list(reversed(messages))


@router.delete("/history")
def clear_history(session: SessionDep):
    """Clear all chat history."""
    count = llm_service.clear_history(session)
    return {"deleted": count}
