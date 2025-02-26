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
    similarity_count: int

class WordCheckResponse(BaseModel):
    match_count: int
    
class WordCheckRequest(BaseModel):
    text: str