
from fastapi.testclient import TestClient
from  .main import app, Base , get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Database setup
DATABASE_URL = "postgresql://postgres:iit123@127.0.0.1:5433/my_pgdb"
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Dependency override for testing database session
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

# Test cases for each endpoint
def test_register_user():
    response = client.post("/register-user/", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword",
        "date_of_birth": "1990-01-01"
    })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"

def test_get_all_users():
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data["users"]) > 0

def test_update_user():
    # Create a user first
    user = client.post("/register-user/", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword",
        "date_of_birth": "1990-01-01"
    }).json()
    
    # Update the user
    response = client.put(f"/update-user/{user['id']}", json={
        "name": "Updated Test User",
        "email": "updated_test@example.com",
        "password": "updatedpassword",
        "date_of_birth": "1990-01-01"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user['id']
    assert data["name"] == "Updated Test User"
    assert data["email"] == "updated_test@example.com"

def test_delete_user():
    # Create a user first
    user = client.post("/register-user/", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword",
        "date_of_birth": "1990-01-01"
    }).json()
    
    # Delete the user
    response = client.delete(f"/delete-user/{user['id']}")
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"

def test_login_user():
    # Create a user first
    client.post("/register-user/", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword",
        "date_of_birth": "1990-01-01"
    })
    
    # Login with the created user
    response = client.post("/login-user", json={
        "email": "test@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_invalid_login():
    response = client.post("/login-user", json={
        "email": "nonexistent@example.com",
        "password": "invalidpassword"
    })
    assert response.status_code == 401

def test_token():
    # Create a user first
    client.post("/register-user/", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword",
        "date_of_birth": "1990-01-01"
    })
    
    # Login to obtain token
    login_response = client.post("/login-user", json={
        "email": "test@example.com",
        "password": "testpassword"
    })
    token = login_response.json()["access_token"]
    
    # Test token endpoint
    token_response = client.post("/token", json={
        "email": "test@example.com",
        "password": "testpassword"
    })
    assert token_response.status_code == 200
    assert "access_token" in token_response.json()
