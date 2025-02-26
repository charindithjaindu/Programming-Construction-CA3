from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class QuestionInput(BaseModel):
    text: str

class Question(BaseModel):
    id: str
    text: str
    created_at: datetime

class SimilarityRequest(BaseModel):
    text: str

class SimilarityResponse(BaseModel):
    similar_questions: list[dict]
    similarity_count: int
    
class WordCheckRequest(BaseModel):
    text: str

class WordCheckResponse(BaseModel):
    matching_questions: list[dict]
    match_count: int