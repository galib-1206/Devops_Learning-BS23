from ast import List
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


#   ## Pydantic Model
# class UserCreate(BaseModel):
#     id: int
#     name: str
#     age: int

# class UserResponse(BaseModel):
#     id: int
#     name: str
#     age: int




# # Create User
# @app.post("/users/", response_model=UserResponse)
# async def create_user(user: User, db: Session = Depends(get_db)):
#     db.add(user)
#     db.commit()
#     db.refresh(user)
#     return UserResponse(id=user.id, name=user.name, age=user.age)

# ## Get all Users
# @app.get("/users/", response_model=List[User])
# async def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#     users = db.query(User).offset(skip).limit(limit).all()
#     return users
