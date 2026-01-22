from sqlalchemy.orm import Session,sessionmaker,declarative_base
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Load enviroment variables
load_dotenv()

# Load credentials
DATABASE_URL=os.getenv("DATABASE_URL")

# Create Engine
engine=create_engine(DATABASE_URL,echo=True)

# Create sessions factory
SessionLocal = sessionmaker(bind=engine,class_=Session,expire_on_commit=False)

# Base Models
Base=declarative_base()

# Dependency to get sessions
def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()