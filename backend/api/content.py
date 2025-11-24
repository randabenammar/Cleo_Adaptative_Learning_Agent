from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/content", tags=["content"])


def get_content_agent():
    from backend.app import _state
    agent = _state.get("content_agent")
    if not agent:
        raise HTTPException(status_code=503, detail="ContentAgent not initialized")
    return agent


class ConceptRequest(BaseModel):
    concept: str
    subject: str
    bloom_level: int = 2
    learner_background: Optional[str] = None


class LessonSummaryRequest(BaseModel):
    subject: str
    lesson_title: str
    key_concepts: List[str]


class StudyGuideRequest(BaseModel):
    subject: str
    topics: List[str]
    exam_type: str = "conceptual"


class ScenarioRequest(BaseModel):
    subject: str
    concept: str
    difficulty: int = 3


@router.post("/concept-explanation")
def get_concept_explanation(
    payload: ConceptRequest,
    agent = Depends(get_content_agent)
):
    """Génère une explication détaillée d'un concept."""
    try:
        result = agent.generate_concept_explanation(
            concept=payload.concept,
            subject=payload.subject,
            bloom_level=payload.bloom_level,
            learner_background=payload.learner_background
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lesson-summary")
def get_lesson_summary(
    payload: LessonSummaryRequest,
    agent = Depends(get_content_agent)
):
    """Génère un résumé de leçon."""
    try:
        result = agent.generate_lesson_summary(
            subject=payload.subject,
            lesson_title=payload.lesson_title,
            key_concepts=payload.key_concepts
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/study-guide")
def get_study_guide(
    payload: StudyGuideRequest,
    agent = Depends(get_content_agent)
):
    """Génère un guide d'étude personnalisé."""
    try:
        result = agent.generate_study_guide(
            subject=payload.subject,
            topics=payload.topics,
            exam_type=payload.exam_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/practice-scenarios")
def get_practice_scenarios(
    payload: ScenarioRequest,
    agent = Depends(get_content_agent)
):
    """Génère des scénarios pratiques."""
    try:
        result = agent.generate_practice_scenarios(
            subject=payload.subject,
            concept=payload.concept,
            difficulty=payload.difficulty
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))