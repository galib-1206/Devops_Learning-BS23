import datetime
from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, Session, relationship
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "mysql+mysqlconnector://root:iit123@localhost:3306/exampleDB"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}



# Dependency to get the database session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    age = Column(Integer)

    expenditures = relationship("Expenditure", back_populates="user")

# Expenditure model
class Expenditure(Base):
    __tablename__ = "expenditures"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    date = Column(DateTime, default=datetime.date)
    time = Column(DateTime, default=datetime.time)
    event = Column(String(255), index=True)
    expense = Column(DECIMAL(10, 2))

    user = relationship("User", back_populates="expenditures")

# # Create tables
Base.metadata.create_all(bind=engine)


