from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime


app = FastAPI()

engine = create_engine('postgresql://postgres:password@localhost:900/postgres')

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

Base = declarative_base()

class Author(Base):

    __tablename__ = 'author'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))

class Post(Base):

    __tablename__ = 'post'
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    created = Column(DateTime)
    author_id = Column(Integer, ForeignKey('author.id', ondelete='CASCADE'))
    

    author = relationship("Author")


Base.metadata.create_all(bind=engine)

@app.post("/author")

def create_author(name: str):
    if not name:
        return JSONResponse(content={"error": "Name is required"}, status_code=400)
    
    try:
        author = Author(name=name)
        session.add(author)
        session.commit()
    except Exception as e:
        session.rollback()
        return JSONResponse(content={"error": str(e)}, status_code=500)

    return JSONResponse(content={"id": author.id, "name": author.name}, status_code=201)