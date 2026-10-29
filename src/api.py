from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Bank FAQ Assistant API",
    description="REST API для вопросно-ответной системы по банковским продуктам",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "service": "bank-faq-api"}

@app.post("/api/v1/chat", response_model=QueryResponse, tags=["Chat"])
def chat_endpoint(request: QueryRequest):
    # Заглушка, сюда позже подключим RAG
    return QueryResponse(
        answer=f"Ваш вопрос принят: '{request.question}'. Пайплайн RAG находится в разработке.",
        sources=["Регламент №1", "Тарифы банка (заглушка)"]
    )