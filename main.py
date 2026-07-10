from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from rag import ask_property_question

app = FastAPI(title="Real Estate RAG API")


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    question: str
    answer: str
    sources_used: int


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/ask", response_model=AnswerResponse)
def ask(request: QuestionRequest):
    try:
        return ask_property_question(request.question)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
