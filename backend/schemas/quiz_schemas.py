# Ajouter ce schema
from pydantic import BaseModel


class HintRequest(BaseModel):
    session_id: str
    question_id: str