from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from models import Question, SimilarityResponse, QuestionInput, SimilarityRequest, WordCheckRequest, WordCheckResponse
from datetime import datetime
from difflib import SequenceMatcher
from bson import ObjectId

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
    app.mongodb = app.mongodb_client[settings.DATABASE_NAME]

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

@app.post("/questions/", response_model=Question)
async def create_question(question: QuestionInput):
    # Check if there are already 10 questions
    count = await app.mongodb.questions.count_documents({})
    if count >= 10:
        raise HTTPException(status_code=400, detail="Maximum number of questions (10) reached")
    
    question_data = {
        "text": question.text,
        "created_at": datetime.utcnow()
    }
    
    result = await app.mongodb.questions.insert_one(question_data)
    return Question(
        id=str(result.inserted_id),
        text=question.text,
        created_at=question_data["created_at"]
    )

@app.delete("/questions/{question_id}")
async def delete_question(question_id: str):
    result = await app.mongodb.questions.delete_one({"_id": ObjectId(question_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"message": "Question deleted successfully"}

@app.post("/questions/check-similarity/", response_model=SimilarityResponse)
async def check_similarity(question: SimilarityRequest):
    similar_questions = []
    cursor = app.mongodb.questions.find({})
    
    # Clean input text by removing extra whitespace and line breaks
    input_text = ' '.join(question.text.split())
    
    async for existing_question in cursor:
        # Clean existing question text
        existing_text = ' '.join(existing_question["text"].split())
        
        similarity = SequenceMatcher(
            None, 
            input_text.lower(), 
            existing_text.lower()
        ).ratio()
        
        if similarity > 0.6:
            similar_questions.append({
                "id": str(existing_question["_id"]),
                "text": existing_question["text"],
                "similarity": round(similarity * 100, 2)
            })
    
    return SimilarityResponse(
        similar_questions=similar_questions,
        similarity_count=len(similar_questions)
    )

@app.get("/questions/")
async def get_questions():
    questions = []
    cursor = app.mongodb.questions.find({})
    async for question in cursor:
        questions.append({
            "id": str(question["_id"]),
            "text": question["text"],
            "created_at": question["created_at"]
        })
    return questions

@app.post("/questions/check-words/", response_model=WordCheckResponse)
async def check_words(request: WordCheckRequest):
    # Split input into words and convert to lowercase
    input_words = set(word.lower() for word in request.text.split())
    
    matching_questions = []
    cursor = app.mongodb.questions.find({})
    
    async for existing_question in cursor:
        # Split existing question into words
        question_words = set(word.lower() for word in existing_question["text"].split())
        
        # Find common words
        common_words = input_words.intersection(question_words)
        
        if common_words:  # If there are any matching words
            matching_questions.append({
                "id": str(existing_question["_id"]),
                "text": existing_question["text"],
                "matching_words": list(common_words)
            })
    
    return WordCheckResponse(
        matching_questions=matching_questions,
        match_count=len(matching_questions)
    )

@app.get("/",
    summary="API Root",
    description="Redirects to API documentation"
)
async def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")
