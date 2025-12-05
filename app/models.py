from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    books = relationship("UserBook", back_populates="user")

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String)
    description = Column(Text)
    published_year = Column(Integer)
    embedding = Column(JSON) # Storing as JSON for SQLite compatibility
    tags = Column(JSON)      # Storing as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user_books = relationship("UserBook", back_populates="book")

class UserBook(Base):
    __tablename__ = "user_books"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    book_id = Column(Integer, ForeignKey("books.id"), primary_key=True)
    status = Column(String, default="finished") # reading, finished, dropped
    rating = Column(Integer)
    progress = Column(Float)
    last_read_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="books")
    book = relationship("Book", back_populates="user_books")
