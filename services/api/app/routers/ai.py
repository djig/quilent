from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.models import Entity, User
from app.schemas.api import SummarizeResponse, AskRequest, AskResponse
from app.services.ai_service import generate_summary, answer_question, PROMPTS
from app.middleware.auth import get_current_user

router = APIRouter()


@router.post("/summarize/{entity_id}", response_model=SummarizeResponse)
async def summarize_entity(
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    entity = await db.get(Entity, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Return cached summary if exists
    if entity.summary:
        return SummarizeResponse(summary=entity.summary, cached=True)

    # Generate new summary
    prompt = PROMPTS.get(entity.product_id, {}).get("summarize", "Summarize: {{content}}")
    content = str(entity.data)

    summary = await generate_summary(content, prompt)

    # Cache the summary
    entity.summary = summary
    await db.commit()

    return SummarizeResponse(summary=summary, cached=False)


@router.post("/ask/{entity_id}", response_model=AskResponse)
async def ask_about_entity(
    entity_id: UUID,
    request: AskRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    entity = await db.get(Entity, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    context = str(entity.data)
    if entity.summary:
        context = f"Summary: {entity.summary}\n\nFull details: {context}"

    answer = await answer_question(context, request.question)

    return AskResponse(answer=answer)


@router.post("/analyze/{entity_id}")
async def analyze_entity(
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Deep analysis of an entity (premium feature)"""
    entity = await db.get(Entity, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Import here to avoid circular imports
    from app.services.ai_service import analyze_contract

    prompt = PROMPTS.get(entity.product_id, {}).get("analyze", "Analyze: {{content}}")
    content = str(entity.data)

    analysis = await analyze_contract(content, prompt)

    return {"analysis": analysis}
