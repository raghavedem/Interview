# FastAPI + SQLAlchemy + PostgreSQL: 80/20 Mastery Guide

## The 20% You Need to Know

This guide covers the essential 20% of concepts that handle 80% of real-world use cases. Skip the edge cases and deep dives—focus on building working applications fast.

---

## Part 1: Setup (5 minutes)

### Installation
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv pydantic
```

### Project Structure
```
my_api/
├── main.py              # Entry point
├── database.py          # DB connection
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── crud.py              # Database operations
├── routes.py            # API endpoints
└── .env                 # Credentials
```

### .env File
```
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
```

---

## Part 2: Database Connection (10 minutes)

### database.py
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**What you need to know:**
- `create_engine`: Connects to PostgreSQL
- `SessionLocal`: Factory that creates new database sessions
- `get_db()`: FastAPI dependency that injects DB into routes

---

## Part 3: Models (10 minutes)

### models.py
```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    name = Column(String(100))
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    content = Column(String(5000))
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    author = relationship("User", back_populates="posts")
```

**What you need to know:**
- `Column`: Define database columns with types
- `primary_key=True`: Unique identifier
- `index=True`: Speed up queries on this field
- `ForeignKey`: Link to another table
- `relationship`: Easy object access (e.g., `user.posts`)

---

## Part 4: Pydantic Schemas (10 minutes)

### schemas.py
```python
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# For creating/updating
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

class PostCreate(BaseModel):
    title: str
    content: str

# For returning from API
class UserBase(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True  # Read from ORM objects

class PostBase(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Nested responses
class UserWithPosts(UserBase):
    posts: List[PostBase]

class PostWithAuthor(PostBase):
    author: UserBase
```

**What you need to know:**
- Input schemas (Create): Validate incoming data
- Output schemas (Response): Format database objects
- `from_attributes = True`: Convert SQLAlchemy ORM objects to dicts
- Nested schemas: Return related data in one response

---

## Part 5: CRUD Operations (15 minutes)

### crud.py
```python
from sqlalchemy.orm import Session
from models import User, Post
from schemas import UserCreate, PostCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ========== USER OPERATIONS ==========

def create_user(db: Session, user: UserCreate):
    fake_hashed = pwd_context.hash(user.password)
    db_user = User(
        email=user.email,
        name=user.name,
        hashed_password=fake_hashed
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_all_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(User).offset(skip).limit(limit).all()

def update_user(db: Session, user_id: int, user_update: dict):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    for key, value in user_update.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

# ========== POST OPERATIONS ==========

def create_post(db: Session, post: PostCreate, author_id: int):
    db_post = Post(
        title=post.title,
        content=post.content,
        author_id=author_id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_post(db: Session, post_id: int):
    return db.query(Post).filter(Post.id == post_id).first()

def get_posts_by_author(db: Session, author_id: int):
    return db.query(Post).filter(Post.author_id == author_id).all()

def update_post(db: Session, post_id: int, post_update: dict):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        return None
    for key, value in post_update.items():
        setattr(db_post, key, value)
    db.commit()
    db.refresh(db_post)
    return db_post

def delete_post(db: Session, post_id: int):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post:
        db.delete(db_post)
        db.commit()
    return db_post
```

**What you need to know:**
- `db.query(Model).filter()`: WHERE clause
- `db.add()`, `db.commit()`: Create/update
- `db.delete()`, `db.commit()`: Delete
- `db.refresh()`: Get updated object after commit
- CRUD pattern: Create, Read, Update, Delete

---

## Part 6: API Routes (15 minutes)

### main.py (or routes.py)
```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import crud
import schemas
import models

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="My API")

# ========== USER ENDPOINTS ==========

@app.post("/users", response_model=schemas.UserBase)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    existing = crud.get_user_by_email(db, email=user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/{user_id}", response_model=schemas.UserWithPosts)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID with all posts"""
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users", response_model=list[schemas.UserBase])
def get_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get all users with pagination"""
    return crud.get_all_users(db, skip=skip, limit=limit)

@app.put("/users/{user_id}", response_model=schemas.UserBase)
def update_user(user_id: int, user_update: dict, db: Session = Depends(get_db)):
    """Update user by ID"""
    user = crud.update_user(db, user_id=user_id, user_update=user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete user by ID"""
    user = crud.delete_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted"}

# ========== POST ENDPOINTS ==========

@app.post("/users/{user_id}/posts", response_model=schemas.PostBase)
def create_post(user_id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    """Create a new post"""
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_post(db=db, post=post, author_id=user_id)

@app.get("/posts/{post_id}", response_model=schemas.PostWithAuthor)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get post by ID"""
    post = crud.get_post(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.get("/users/{user_id}/posts", response_model=list[schemas.PostBase])
def get_user_posts(user_id: int, db: Session = Depends(get_db)):
    """Get all posts by user"""
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.get_posts_by_author(db, author_id=user_id)

@app.put("/posts/{post_id}", response_model=schemas.PostBase)
def update_post(post_id: int, post_update: dict, db: Session = Depends(get_db)):
    """Update post by ID"""
    post = crud.update_post(db, post_id=post_id, post_update=post_update)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    """Delete post by ID"""
    post = crud.delete_post(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"detail": "Post deleted"}

# ========== HEALTH CHECK ==========

@app.get("/health")
def health():
    return {"status": "healthy"}
```

**What you need to know:**
- `@app.get/post/put/delete`: HTTP methods
- `Depends(get_db)`: Inject database session
- `response_model`: Validate and format response
- `HTTPException`: Send error to client
- `{path_param}`: Extract from URL path
- `query_param=default`: Extract from query string

---

## Part 7: Run It (5 minutes)

### Run the Server
```bash
uvicorn main:app --reload
```

Visit: `http://localhost:8000/docs` for interactive API documentation

### Test with curl
```bash
# Create user
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","name":"John","password":"secret123"}'

# Get user
curl "http://localhost:8000/users/1"

# Create post
curl -X POST "http://localhost:8000/users/1/posts" \
  -H "Content-Type: application/json" \
  -d '{"title":"My First Post","content":"Hello world!"}'

# Get user with posts
curl "http://localhost:8000/users/1"
```

---

## Part 8: Key Concepts (The 20%)

| Concept | Purpose | Example |
|---------|---------|---------|
| **SQLAlchemy Model** | Define database table | `class User(Base)` |
| **Pydantic Schema** | Validate input/output | `class UserCreate(BaseModel)` |
| **CRUD Functions** | Database operations | `create_user(db, user)` |
| **Dependency Injection** | Pass DB to routes | `Depends(get_db)` |
| **Query Filtering** | WHERE clauses | `.filter(User.id == 1)` |
| **Relationships** | Connect tables | `relationship("Post")` |
| **HTTPException** | Send errors | `HTTPException(status_code=400)` |
| **Pagination** | Limit results | `.offset(skip).limit(limit)` |

---

## Part 9: Common Patterns

### Pattern 1: Pagination
```python
@app.get("/posts")
def list_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Post).offset(skip).limit(limit).all()

# Usage: /posts?skip=0&limit=20
```

### Pattern 2: Search/Filter
```python
@app.get("/posts/search")
def search_posts(q: str, db: Session = Depends(get_db)):
    return db.query(Post).filter(Post.title.ilike(f"%{q}%")).all()

# Usage: /posts/search?q=python
```

### Pattern 3: Bulk Operations
```python
@app.post("/users/bulk")
def create_users(users: list[schemas.UserCreate], db: Session = Depends(get_db)):
    db_users = [User(**user.dict()) for user in users]
    db.add_all(db_users)
    db.commit()
    return db_users
```

### Pattern 4: Error Handling
```python
@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

---

## Part 10: PostgreSQL Setup (If Needed)

### Install PostgreSQL (macOS)
```bash
brew install postgresql@15
brew services start postgresql@15
```

### Create Database
```bash
createdb mydb
psql mydb

# In psql:
CREATE USER myuser WITH PASSWORD 'mypassword';
ALTER ROLE myuser SET client_encoding TO 'utf8';
ALTER ROLE myuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE myuser SET default_transaction_deferrable TO on;
ALTER ROLE myuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE mydb TO myuser;
\q
```

### Update .env
```
DATABASE_URL=postgresql://myuser:mypassword@localhost:5432/mydb
```

---

## What NOT to Worry About (The 80%)

- ❌ Connection pooling (SQLAlchemy handles it)
- ❌ Complex ORM relationships (start simple)
- ❌ Query optimization (premature optimization)
- ❌ Migrations (Alembic—use later)
- ❌ Advanced authentication (JWT—use later)
- ❌ Caching (Redis—use when needed)
- ❌ Background tasks (Celery—use when needed)

---

## Quick Reference

### Database Operations
```python
db.query(User).all()                              # SELECT * FROM users
db.query(User).filter(User.id == 1).first()      # SELECT * FROM users WHERE id = 1
db.query(User).filter(User.name.ilike("%john%")) # LIKE query
db.add(user)                                      # INSERT
db.commit()                                       # Commit transaction
db.delete(user)                                   # DELETE
```

### FastAPI Decorators
```python
@app.get("/path")                    # GET request
@app.post("/path")                   # POST request
@app.put("/path/{id}")               # PUT request
@app.delete("/path/{id}")            # DELETE request
Depends(get_db)                       # Inject dependency
response_model=schemas.UserBase       # Validate response
HTTPException(status_code=400)        # Return error
```

---

## Next Steps (After Mastering This)

1. **Migrations**: Learn Alembic for database versioning
2. **Authentication**: Add JWT tokens and password hashing
3. **Validation**: Use more Pydantic features (validators, custom types)
4. **Testing**: Write pytest tests for your endpoints
5. **Optimization**: Learn query optimization and indexing
6. **Deployment**: Deploy to production with proper configuration

---

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org)
- [PostgreSQL Docs](https://www.postgresql.org/docs)
- [Pydantic Docs](https://docs.pydantic.dev)

**Total Learning Time: ~1-2 hours to understand, 1-2 days to master with practice.**
