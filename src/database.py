import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker
from pgvector.sqlalchemy import Vector

from src.config import DATABASE_URL, EMBEDDING_DIM

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    doc_name = Column(String(255), nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Vector(EMBEDDING_DIM))

class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_query = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)
    sources_used = Column(Text)

def init_db():
    """Создает расширение pgvector и таблицы в Postgres."""
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Подключение к Supabase PostgreSQL...")
    try:
        init_db()
        print("\n УСПЕХ! Таблицы и расширение pgvector созданы в Supabase.")
    except Exception as e:
        print("\n Ошибка при подключении/создании таблиц:")
        print(e)