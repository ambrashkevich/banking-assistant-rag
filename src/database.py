import os
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, 
    DateTime, Boolean, ForeignKey, text, Index
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from pgvector.sqlalchemy import Vector

from src.config import DATABASE_URL, EMBEDDING_DIM

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Document(Base):
    """Таблица 1: Справочник загруженных документов банка"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)  # "cards", "deposits", "loans"
    created_at = Column(DateTime, default=datetime.utcnow)

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    """Таблица 2: Текстовые чанки с векторными эмбеддингами"""
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Vector(EMBEDDING_DIM))
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="chunks")


class QueryLog(Base):
    """Таблица 3: Логирование запросов клиентов (требование методички стр. 9)"""
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_query = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)
    sources_used = Column(Text)
    latency_ms = Column(Integer, nullable=False)

    feedback = relationship("QueryFeedback", back_populates="log", uselist=False)


class QueryFeedback(Base):
    """Таблица 4: Пользовательские оценки (Like/Dislike) для анализа ошибок"""
    __tablename__ = "query_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(Integer, ForeignKey("query_logs.id", ondelete="CASCADE"), nullable=False)
    is_positive = Column(Boolean, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    log = relationship("QueryLog", back_populates="feedback")


# ==========================================
# СКРИПТ АВТОМАТИЧЕСКОЙ МИГРАЦИИ
# ==========================================

def init_db():
  
    with engine.connect() as conn:
        # Включаем векторное расширение
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    
    # Создаем таблицы через SQLAlchemy
    Base.metadata.create_all(bind=engine)

    # Создаем HNSW индекс для ускорения векторного поиска (косинусное расстояние)
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_chunks_embedding 
            ON document_chunks 
            USING hnsw (embedding vector_cosine_ops);
        """))
        conn.commit()


if __name__ == "__main__":
    print("Запуск автоматического скрипта создания схемы БД...")
    try:
        init_db()
        print("\n УСПЕХ: Структура базы данных полностью создана через Python!")
        print("  - Таблица 'documents' создана")
        print("  - Таблица 'document_chunks' с полем vector(768) создана")
        print("  - Векторный индекс HNSW настроен")
        print("  - Таблица 'query_logs' для мониторинга создана")
        print("  - Таблица 'query_feedbacks' для оценки создана")
    except Exception as e:
        print("\n Ошибка при выполнении скрипта миграции:")
        print(e)