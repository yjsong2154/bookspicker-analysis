from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    id_backend = Column(Integer, unique=True, index=True, nullable=True)
    
    # New fields for recommendation
    preference_embedding = Column(JSON)  # Average vector of read books
    preferred_tags = Column(JSON)        # Accumulated tag counts e.g., {"fantasy": 10, "scifi": 5}

    # Relationship to books read
    read_books = relationship("UserBook", back_populates="user")

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String, unique=True, index=True, nullable=False) # ISBN as unique identifier
    title = Column(String, nullable=False)
    author = Column(String)
    description = Column(Text)
    published_year = Column(Integer)
    
    # AI Analysis Data
    embedding = Column(JSON) # Vector
    tags = Column(JSON)      # Analysis Tags
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    read_by_users = relationship("UserBook", back_populates="book")

class UserBook(Base):
    """
    Mapping table for 'User read Book'.
    Simple interaction log as requested.
    """
    __tablename__ = "user_books"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    book_id = Column(Integer, ForeignKey("books.id"), primary_key=True)
    read_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="read_books")
    book = relationship("Book", back_populates="read_by_users")
