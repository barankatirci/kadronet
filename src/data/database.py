"""
database.py — Veritabanı bağlantısı ve session yönetimi
SQLite kullanıyoruz, production'da sadece DATABASE_URL değiştirilir (PostgreSQL vs.)
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# DB dosyası backend klasörünün içinde oluşur
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'personnel.db')}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite için gerekli
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency injection için DB session oluşturucu"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
