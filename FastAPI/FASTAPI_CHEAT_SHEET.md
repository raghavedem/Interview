# FastAPI + SQLite Cheat Sheet
## Quick Reference for All Concepts

---

## 1️⃣ FASTAPI BASICS

### Routing & HTTP Methods
```python
from fastapi import FastAPI, HTTPException, status

app = FastAPI()

@app.get("/items")              # GET request
@app.post("/items")             # POST request (create)
@app.put("/items/{id}")         # PUT request (full update)
@app.patch("/items/{id}")       # PATCH request (partial update)
@app.delete("/items/{id}")      # DELETE request

async def endpoint():           # Can be async
    return {"message": "Hello"}

def endpoint():                 # Or sync
    return {"message": "Hello"}
```

### Path, Query, Body Parameters
```python
@app.get("/users/{user_id}")
async def get_user(
    user_id: int,                           # Path parameter
    skip: int = 0,                          # Query parameter
    limit: int = 10
):
    return {"user_id": user_id, "skip": skip}

@app.post("/items")
async def create_item(item: Item):          # Body parameter
    return item
```

### Status Codes
```python
@app.post("/items", status_code=201)        # HTTP 201 Created
@app.delete("/items/{id}", status_code=204) # HTTP 204 No Content

# Also use status module
from fastapi import status

status_code=status.HTTP_201_CREATED
status_code=status.HTTP_400_BAD_REQUEST
status_code=status.HTTP_401_UNAUTHORIZED
status_code=status.HTTP_403_FORBIDDEN
status_code=status.HTTP_404_NOT_FOUND
status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
```

---

## 2️⃣ PYDANTIC MODELS

### Basic Model
```python
from pydantic import BaseModel, Field, EmailStr, validator

class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    age: int = 18                          # Default value
    is_active: bool = True
    tags: list[str] = []                   # List field
    
    class Config:
        from_attributes = True             # ORM mode

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    age: int = Field(18, ge=0, le=150)     # Range validation
```

### Validation
```python
class Product(BaseModel):
    name: str
    price: float = Field(..., gt=0)        # Must be > 0
    discount: float = Field(0, ge=0, le=1) # 0-1 range
    
    @validator('name')
    def name_alphanumeric(cls, v):
        if not v.replace(' ', '').isalnum():
            raise ValueError('Name must be alphanumeric')
        return v

# Validation runs automatically on model creation
user = User(username="john", email="john@example.com")  # ✓
user = User(username="john", age="invalid")              # ✗ ValidationError
```

### Optional Fields
```python
from typing import Optional

class Item(BaseModel):
    name: str
    description: Optional[str] = None      # Can be None
    price: float

# Usage
item = Item(name="Apple", price=1.99)      # ✓ description is None
item = Item(name="Apple", description="Red apple", price=1.99)  # ✓
```

---

## 3️⃣ DATABASE OPERATIONS

### Connection
```python
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db():
    conn = sqlite3.connect("app.db")
    conn.row_factory = sqlite3.Row         # Access by column name
    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()
```

### CRUD Operations
```python
# CREATE
with get_db() as conn:
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email) VALUES (?, ?)",
        ("john", "john@example.com")
    )
    new_id = cursor.lastrowid

# READ
with get_db() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (1,))
    user = cursor.fetchone()  # One row
    # or
    users = cursor.fetchall()  # All rows

# UPDATE
with get_db() as conn:
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET username = ? WHERE id = ?",
        ("jane", 1)
    )

# DELETE
with get_db() as conn:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (1,))
```

### Schema Creation
```python
def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                completed BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id)')
```

---

## 4️⃣ ERROR HANDLING

### HTTPException
```python
from fastapi import HTTPException, status

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    if user_id < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID must be positive"
        )
    
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
```

### Custom Exception Handler
```python
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

# Usage
@app.post("/users")
async def create_user(user: UserCreate):
    try:
        user_id = UserRepository.create(user)
        return {"id": user_id}
    except ValueError as e:
        raise  # Will use exception handler
```

---

## 5️⃣ DEPENDENCY INJECTION

### Basic Dependency
```python
from fastapi import Depends

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from token"""
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    return get_user_from_token(token)

@app.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

### Reusable Dependencies
```python
def get_db() -> Generator:
    """Database dependency"""
    db = sqlite3.connect("app.db")
    try:
        yield db
    finally:
        db.close()

@app.post("/users")
async def create_user(user: UserCreate, db = Depends(get_db)):
    # db is automatically injected
    cursor = db.cursor()
    cursor.execute("INSERT INTO users ...")
```

### Dependency with Validation
```python
def validate_pagination(skip: int = 0, limit: int = 10):
    if skip < 0:
        raise HTTPException(status_code=400, detail="skip >= 0")
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="1 <= limit <= 100")
    return {"skip": skip, "limit": limit}

@app.get("/users")
async def list_users(pagination = Depends(validate_pagination)):
    skip = pagination["skip"]
    limit = pagination["limit"]
```

---

## 6️⃣ AUTHENTICATION & SECURITY

### Password Hashing
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hash: str) -> bool:
    return pwd_context.verify(password, hash)

# Store hashed password in DB
hashed = hash_password("MyPassword123")
# Later verify
if verify_password("MyPassword123", hashed):
    print("Password correct!")
```

### JWT Tokens
```python
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def create_token(data: dict, expires_in: int = 30):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_in)
    to_encode.update({"exp": expire})
    
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        return None
```

### OAuth2 Login
```python
from fastapi.security import OAuth2PasswordRequestForm

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_username(form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_token({"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
```

---

## 7️⃣ MIDDLEWARE

### CORS
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],                    # ["https://example.com"] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Custom Middleware
```python
@app.middleware("http")
async def add_process_time_header(request, call_next):
    import time
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    return response
```

### Built-in Middleware
```python
from fastapi.middleware.gzip import GZIPMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(GZIPMiddleware, minimum_size=1000)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["example.com"])
```

---

## 8️⃣ TESTING

### Test Client
```python
from fastapi.testclient import TestClient
import pytest

@pytest.fixture
def client():
    return TestClient(app)

def test_create_user(client):
    response = client.post("/users", json={
        "username": "john",
        "email": "john@example.com",
        "password": "SecurePass123"
    })
    
    assert response.status_code == 201
    assert response.json()["username"] == "john"

def test_get_user(client):
    response = client.get("/users/1")
    assert response.status_code == 200
```

### Test Fixtures
```python
@pytest.fixture
def user_data():
    return {
        "username": "john",
        "email": "john@example.com",
        "password": "SecurePass123"
    }

@pytest.fixture
def test_db():
    conn = sqlite3.connect(":memory:")
    init_db_tables(conn)
    yield conn
    conn.close()

def test_with_fixtures(client, user_data, test_db):
    # Use fixtures
    pass
```

---

## 9️⃣ ASYNC DATABASE

### Async Operations
```python
import asyncio

@app.get("/users")
async def list_users():
    # This runs in an event loop
    # Don't block with long operations!
    users = get_users_from_db()  # ✓ Fast database query
    # users = time.sleep(5)       # ✗ Blocks entire server!
    return users

# For blocking operations, use run_in_executor
import concurrent.futures

@app.get("/slow-operation")
async def slow_operation():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, blocking_function)
    return result
```

---

## 🔟 DEPLOYMENT

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./test.db"
    secret_key: str
    api_title: str = "My API"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Production Server
```bash
# Development
uvicorn main:app --reload

# Production
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

---

## 🎯 COMMON PATTERNS

### Repository Pattern
```python
class UserRepository:
    @staticmethod
    def create(user_data: UserCreate) -> int:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (user_data.username, user_data.email, user_data.password)
            )
            return cursor.lastrowid
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional[dict]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

# Usage in endpoint
@app.post("/users")
async def create_user(user: UserCreate):
    user_id = UserRepository.create(user)
    return {"id": user_id}
```

### Pagination
```python
@app.get("/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    users = db.get_users(skip=skip, limit=limit)
    return users

# URL: /users?skip=0&limit=10
```

### Caching
```python
from functools import lru_cache
from datetime import datetime, timedelta

cache = {}
cache_ttl = {}

def get_cached(key: str, ttl_seconds: int = 300):
    if key in cache:
        if datetime.now() - cache_ttl[key] < timedelta(seconds=ttl_seconds):
            return cache[key]
    return None

def set_cached(key: str, value):
    cache[key] = value
    cache_ttl[key] = datetime.now()
```

---

## 🔒 SECURITY CHECKLIST

- ✅ Hash passwords with bcrypt
- ✅ Use HTTPS in production
- ✅ Use parameterized queries (prevent SQL injection)
- ✅ Validate all inputs
- ✅ Use strong secret keys
- ✅ Set secure CORS
- ✅ Implement rate limiting
- ✅ Add security headers
- ✅ Use environment variables for secrets
- ✅ Keep dependencies updated

---

## 💡 QUICK TIPS

| Task | Solution |
|------|----------|
| Auto reload | `--reload` flag in development |
| View docs | http://localhost:8000/docs |
| Validate input | Use Pydantic models |
| Protect endpoint | Use `Depends(get_current_user)` |
| Return 404 | `raise HTTPException(status_code=404)` |
| Return 201 (created) | `status_code=201` in decorator |
| Test endpoint | Use `TestClient` from `fastapi.testclient` |
| Run async task | Use `BackgroundTasks` |
| Access query params | Function parameter with default value |
| Access path params | Function parameter with type hint |
| Access body | Pydantic model parameter |

---

## 🚀 STARTUP CHECKLIST

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Initialize database: `python -c "from app import init_db; init_db()"`
- [ ] Set environment variables: `cp .env.example .env`
- [ ] Run tests: `pytest tests/ -v`
- [ ] Start server: `uvicorn main:app --reload`
- [ ] Open browser: `http://localhost:8000/docs`

---

*Last Updated: 2024*
*FastAPI 0.104+ | SQLite 3.31+*
