from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends
from sqlalchemy.future import select
from sqlalchemy import Column, Integer, String, Boolean, Text, TIMESTAMP, ARRAY
from sqlalchemy.dialects.postgresql import VARCHAR, INTEGER, BOOLEAN, TEXT, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship 
from sqlalchemy import Column, Integer, String, TIMESTAMP, func

SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:S%40r%40th%40ceo@34.93.93.205/postgres'

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class DefaultStory(Base):
    __tablename__ = 'defaultstories'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(VARCHAR(255), nullable=False)
    sub_title = Column(VARCHAR(255), nullable=False)
    description = Column(VARCHAR(500), nullable=False)
    image_url = Column(VARCHAR(500), nullable=True)
    audio_url = Column(VARCHAR(500), nullable=True)
    genre = Column(VARCHAR(100), nullable=True)
    popularity_score = Column(Integer, default=0, nullable=True)
    author = Column(VARCHAR(255), nullable=True)
    is_public = Column(Boolean, default=True, nullable=True)
    story_length = Column(Integer, nullable=True)
    language = Column(VARCHAR(50), nullable=True)
    age_group = Column(VARCHAR(50), nullable=True)
    is_active = Column(Boolean, default=False, nullable=True)
    featured = Column(Boolean, default=False, nullable=True)
    tags = Column(ARRAY(TEXT), nullable=True)
    is_premium = Column(Boolean, default=False, nullable=True)
    story = Column(Text, nullable=False)
    created_by = Column(VARCHAR(255), nullable=True)
    modified_by = Column(VARCHAR(255), nullable=True)
    created_date = Column(TIMESTAMP, default="CURRENT_TIMESTAMP", nullable=True)
    last_updated_date = Column(TIMESTAMP, default="CURRENT_TIMESTAMP", nullable=True)

    # To ensure the default primary key constraint
    __table_args__ = (
        {"schema": "public"},
    )


class StoryResponse(BaseModel):
    id: int
    title: str
    sub_title: str
    description: str
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    genre: Optional[str] = None
    popularity_score: Optional[int] = 0
    author: Optional[str] = None
    is_public: Optional[bool] = True
    story_length: Optional[int] = None
    language: Optional[str] = None
    age_group: Optional[str] = None
    is_active: Optional[bool] = False
    featured: Optional[bool] = False
    tags: Optional[List[str]] = None
    is_premium: Optional[bool] = False
    story: str
    created_by: Optional[str] = None
    modified_by: Optional[str] = None
    created_date: Optional[datetime] = None
    last_updated_date: Optional[datetime] = None

    class Config:
        orm_mode = True  # Allow ORM models to be serialized into Pydantic models
    
class Banner(Base):
    __tablename__ = 'banners'

    id: int = Column(Integer, primary_key=True, index=True)  # Annotate with type
    name: str = Column(String, nullable=False)              # Annotate with type
    image_url: str = Column(String, nullable=False)         # Annotate with type
    banner_story_id: int = Column(Integer, nullable=False) 

class BannerResponse(BaseModel):
    id: int
    name: str
    image_url: str
    banner_story_id: int

    class Config:
        orm_mode = True

class MetadataResponse(BaseModel):
    id: int
    title: str
    sub_title: str
    description: str
    image_url: Optional[str] = None

    class Config:
        orm_mode = True  # Allow ORM models to be serialized into Pydantic models

class Genre(Base):
    __tablename__ = "tblgenres"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(255), unique=True, nullable=False)

    # Relationship to SubGenres
    subgenres = relationship("SubGenre", back_populates="genre", cascade="all, delete")

class GenreResponse(BaseModel): 
    id   : int
    name : str

    class Config:
        orm_mode = True

class SubGenre(Base):
    __tablename__ = "tblsubgenres"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(255), nullable=False)
    genre_id = Column(Integer, ForeignKey("tblgenres.id", ondelete="CASCADE"), nullable=False)

    # Relationship to Genre
    genre = relationship("Genre", back_populates="subgenres")

class SubGenreResponse(BaseModel):
    id: int
    name: str
    genre_id: int

    class Config:
        orm_mode = True

class User(Base):
    __tablename__ = "tblusers"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, default=func.now())

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
