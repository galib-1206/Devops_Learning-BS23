
import datetime
from fastapi import Depends, FastAPI, HTTPException
import jwt
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, DateTime, ForeignKey, func
from sqlalchemy.orm import declarative_base, Session, sessionmaker
from passlib.context import CryptContext

DATABASE_URL = "postgresql://postgres:iit123@127.0.0.1:5433/my_pgdb"
# DATABASE_URL = "postgresql://postgres:iit123@localhost:5432/my_pgdb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

#hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# jwt
jwt_secretKey = "your_secret_key"
algorithm = "HS256"

def generateToken(user):
    global ACCESS_TOKEN
    token = jwt.encode({"email": user.email}, jwt_secretKey, algorithm=algorithm)
    ACCESS_TOKEN = token


@app.get("/")
async def root():
    return {"message": "CI/CD Pipeline initiated"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# User Model
class UserBase(BaseModel):
    name: str
    email: str
    password: str
    date_of_birth: datetime.date

# Interface Model
class LoginCredentials(BaseModel):
    email: str
    password: str

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String(45), nullable=False)
    email = Column(String(45), unique=True, nullable=False)
    password_hash = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # expenditures = relationship("Expenditure", back_populates="user")

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = pwd_context.hash(password)

# Expenditure model
class Expenditure(BaseModel):
    userID: str
    date: str
    time: str
    event: str
    details: str
    expense: float

class Expenditure(Base):
    __tablename__ = "expenditures"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    date = Column(DateTime, default=datetime.date)
    time = Column(DateTime, default=datetime.time)
    event = Column(String(255), index=True)
    expense = Column(DECIMAL(10, 2))

    # user = relationship("User", back_populates="expenditures")

# Create tables
Base.metadata.create_all(engine)

# User Service 
@app.post("/register-user/")
def create_user(user: UserBase, db: Session = Depends(get_db)):
    try:
        password_hash = pwd_context.hash(user.password) 
        db_user = User(name=user.name, email=user.email, password_hash=password_hash) 
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to register user")

   

@app.get("/users")
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return {"users": users}

@app.put("/update-user/{user_id}")
def update_user(user_id: int, user: UserBase, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db_user.name = user.name
        db_user.email = user.email
        db_user.password = user.password
        db.commit()
        db.refresh(db_user)
        return db_user
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.delete("/delete-user/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return {"message": "User deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")
    

@app.post("/login-user")
def login_user(login_credentials: LoginCredentials, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_credentials.email).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    else:
        verified = pwd_context.verify(login_credentials.password, user.password_hash)

        if verified:
            generateToken(user)
            return {"access_token": ACCESS_TOKEN}
        else:
            raise HTTPException(status_code=401, detail="Wrong credentials")



@app.post("/token")
def login_for_token(login_credentials: LoginCredentials, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_credentials.email).first()

    if not user or not pwd_context.verify(login_credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    generateToken(user)
    return {"access_token": ACCESS_TOKEN, "token_type": "bearer"}