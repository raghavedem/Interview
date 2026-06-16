# FastAPI + SQLite Complete Learning Project
## For 3-5 Years Experience Level

A comprehensive guide to building production-ready REST APIs with FastAPI and SQLite, covering fundamentals, advanced patterns, testing, security, and deployment.

---

## 📦 Project Contents

### **4 Core Application Files (3,500+ lines)**

1. **fastapi_01_fundamentals.py** (500 lines)
   - FastAPI basics and routing
   - Pydantic models and validation
   - SQLite database setup
   - CRUD operations
   - Error handling
   - Basic authentication

2. **fastapi_02_advanced_patterns.py** (800 lines)
   - Dependency injection with Depends()
   - Connection pooling
   - Query optimization
   - Caching strategies
   - Middleware implementation
   - Background tasks
   - Database indexes

3. **fastapi_03_testing_deployment.py** (700 lines)
   - Unit testing with pytest
   - Integration testing
   - Test fixtures and factories
   - Database testing
   - Docker configuration
   - Production deployment
   - Monitoring and logging

4. **fastapi_04_security_auth.py** (600 lines)
   - Password hashing (bcrypt)
   - JWT authentication
   - OAuth2 implementation
   - Role-based access control (RBAC)
   - SQL injection prevention
   - CSRF protection
   - Rate limiting

### **3 Documentation Files**

- **README.md** (this file) - Project overview
- **FASTAPI_CHEAT_SHEET.md** - Quick reference
- **FASTAPI_STUDY_PLAN.md** - 7-14 day study plan

---

## 🎯 What You'll Learn

### Day 1-2: Fundamentals
- ✅ FastAPI basics (routes, methods, status codes)
- ✅ Pydantic models (validation, serialization)
- ✅ SQLite database setup
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ Error handling with HTTPException
- ✅ Basic request/response models

### Day 3-4: Advanced Patterns
- ✅ Dependency injection pattern
- ✅ Connection pooling
- ✅ Query optimization and indexing
- ✅ Caching with TTL
- ✅ Middleware for logging, rate limiting, CORS
- ✅ Background tasks
- ✅ Pagination and filtering

### Day 5-6: Testing & Deployment
- ✅ Unit tests with pytest
- ✅ Integration tests
- ✅ Test fixtures and factories
- ✅ Database testing
- ✅ Docker containerization
- ✅ Production configuration
- ✅ Monitoring and health checks

### Day 7: Security & Auth
- ✅ Password hashing (bcrypt)
- ✅ JWT token authentication
- ✅ OAuth2 implementation
- ✅ Role-based access control
- ✅ SQL injection prevention
- ✅ Input validation and sanitization
- ✅ CORS security
- ✅ Rate limiting for brute force protection

---

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.8+
pip install fastapi uvicorn pydantic[email] passlib[bcrypt] python-jose[cryptography]
```

### Installation
```bash
# Install all dependencies
pip install -r requirements.txt

# Initialize database
python fastapi_01_fundamentals.py

# Run application
uvicorn fastapi_01_fundamentals:app --reload
```

### First API Call
```bash
# Create user
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@example.com","password":"SecurePass123","age":25}'

# Get user
curl http://localhost:8000/users/1

# Get API documentation
# Open browser: http://localhost:8000/docs
```

---

## 📁 File Organization

```
fastapi_project/
├── fastapi_01_fundamentals.py          # Start here
├── fastapi_02_advanced_patterns.py     # After understanding basics
├── fastapi_03_testing_deployment.py    # For production readiness
├── fastapi_04_security_auth.py         # Add security to APIs
├── requirements.txt                    # Dependencies
├── Dockerfile                          # Container configuration
├── docker-compose.yml                  # Multi-container setup
├── .env.example                        # Environment variables
├── README.md                           # This file
└── fastapi_app.db                      # SQLite database (auto-created)
```

---

## 🎓 Key Concepts

### FastAPI Basics
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.post("/items")
async def create_item(item: Item):
    return {"message": "Item created", "item": item}

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    if item_id < 1:
        raise HTTPException(status_code=400, detail="Invalid ID")
    return {"item_id": item_id}
```

### Database Operations
```python
# Create (with error handling)
try:
    user_id = UserRepository.create(user_data)
    return {"id": user_id, "message": "Created"}
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))

# Read
user = UserRepository.get_by_id(user_id)
if not user:
    raise HTTPException(status_code=404, detail="Not found")

# Update
if UserRepository.update(user_id, user_data):
    return {"message": "Updated"}

# Delete
UserRepository.delete(user_id)
```

### Authentication
```python
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token({"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

---

## 🧪 Testing Examples

### Unit Test
```python
def test_password_hashing():
    password = "MyPassword123"
    hashed = PasswordManager.hash_password(password)
    
    assert PasswordManager.verify_password(password, hashed)
    assert not PasswordManager.verify_password("wrong", hashed)
```

### Integration Test
```python
def test_create_user(client):
    response = client.post("/users", json={
        "username": "john",
        "email": "john@example.com",
        "password": "SecurePass123"
    })
    
    assert response.status_code == 201
    assert response.json()["username"] == "john"
```

### Database Test
```python
def test_user_uniqueness(test_db):
    cursor = test_db.cursor()
    
    cursor.execute(
        "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
        ("john", "john@example.com", "hashed")
    )
    test_db.commit()
    
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            ("john", "different@example.com", "hashed")
        )
```

---

## 📊 API Endpoints Overview

### Users
- `POST /users` - Create user
- `GET /users` - List users
- `GET /users/{user_id}` - Get user
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user

### Tasks
- `POST /users/{user_id}/tasks` - Create task
- `GET /users/{user_id}/tasks` - Get user tasks
- `GET /tasks/{task_id}` - Get task
- `PUT /tasks/{task_id}` - Update task
- `DELETE /tasks/{task_id}` - Delete task

### Statistics
- `GET /stats` - System statistics
- `GET /users/{user_id}/stats` - User statistics

### Authentication
- `POST /register` - Register new user
- `POST /login` - Login and get tokens
- `POST /refresh` - Refresh access token
- `GET /me` - Get current user

### Health
- `GET /health` - Health check

---

## 🔥 Most Important Topics

### Must Know (Interview Essential)
1. **CRUD Operations** - Create, Read, Update, Delete patterns
2. **Pydantic Validation** - Input/output models with validation
3. **HTTP Status Codes** - 200, 201, 400, 401, 403, 404, 500
4. **Authentication** - JWT tokens, password hashing
5. **Error Handling** - HTTPException, try/except, validation errors
6. **Database Transactions** - Commit/rollback, relationships
7. **Testing** - Unit tests, integration tests, fixtures
8. **Middleware** - CORS, rate limiting, logging

### Should Know (Interview Important)
9. **Dependency Injection** - Using Depends() effectively
10. **Async/Await** - Async endpoints and database operations
11. **Query Optimization** - Indexes, EXPLAIN QUERY PLAN
12. **Caching** - TTL-based caching strategies
13. **Background Tasks** - Async operations
14. **SQL Injection Prevention** - Parameterized queries
15. **Pagination** - Skip/limit pattern
16. **RBAC** - Role-based access control

### Nice to Know (Advanced)
17. **Connection Pooling** - Resource management
18. **CSRF Protection** - Token-based protection
19. **Monitoring** - Logging, metrics, health checks
20. **Docker** - Containerization and deployment

---

## 📚 Study Schedule

### 7-Day Intensive (3-4 hours/day)
```
Day 1: File 1 (Fundamentals) - 3 hours
Day 2: File 2 (Advanced Patterns) - 4 hours
Day 3: File 3 (Testing & Deployment) - 3 hours
Day 4: File 4 (Security & Auth) - 4 hours
Day 5: Practice + Modify Examples - 3 hours
Day 6: Mini Project Development - 4 hours
Day 7: Mock Interview - 2 hours
```

### 14-Day Standard (2-3 hours/day)
```
Days 1-2: File 1 - 2 hours/day
Days 3-4: File 2 - 2.5 hours/day
Days 5-6: File 3 - 2 hours/day
Days 7-8: File 4 - 2.5 hours/day
Days 9-10: Practice & Coding - 2 hours/day
Days 11-12: Mini Project - 3 hours/day
Days 13-14: Review & Mock Interview - 2 hours/day
```

---

## 💡 Interview Preparation Tips

### Before Interview
- ✅ Run all code files
- ✅ Understand each endpoint's purpose
- ✅ Explain Pydantic validation flow
- ✅ Know how JWT tokens work
- ✅ Understand database relationships
- ✅ Practice writing tests
- ✅ Know deployment considerations

### Common Interview Questions
1. "How do you structure a FastAPI application?"
2. "How does Pydantic validation work?"
3. "Explain JWT token authentication"
4. "How to prevent SQL injection?"
5. "What's the difference between async and sync endpoints?"
6. "How to implement pagination?"
7. "How do you test FastAPI applications?"
8. "What middleware would you use?"
9. "How to handle database transactions?"
10. "How do you secure an API?"

### Example Answer Structure
1. **Clarify** - Ask clarifying questions
2. **Explain** - Explain your approach
3. **Code** - Write example code
4. **Trade-offs** - Discuss pros and cons
5. **Best practices** - Show production-ready thinking

---

## 🎯 Success Checklist

After completing this project, you should:

- [ ] Understand FastAPI routing and HTTP methods
- [ ] Create Pydantic models with validation
- [ ] Perform CRUD operations with SQLite
- [ ] Handle errors with HTTPException
- [ ] Implement JWT authentication
- [ ] Use Depends() for dependency injection
- [ ] Write unit and integration tests
- [ ] Understand pagination and filtering
- [ ] Know how to cache data
- [ ] Understand middleware
- [ ] Write secure code (SQL injection prevention)
- [ ] Deploy with Docker
- [ ] Implement rate limiting
- [ ] Handle async operations
- [ ] Know production best practices

---

## 🚀 Next Steps After This Project

### Immediate (1-2 weeks)
- [ ] Build a complete small project
- [ ] Deploy to a server (Heroku, PythonAnywhere, etc.)
- [ ] Add more complex features
- [ ] Achieve 80%+ test coverage

### Short Term (1-3 months)
- [ ] Learn async database drivers (SQLAlchemy async, asyncpg)
- [ ] Implement GraphQL
- [ ] Learn containerization best practices
- [ ] Study distributed systems concepts

### Medium Term (3-6 months)
- [ ] Build larger applications
- [ ] Learn caching (Redis)
- [ ] Study message queues (Celery, RabbitMQ)
- [ ] Learn microservices patterns

---

## 📖 Additional Resources

### Official Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [SQLite Docs](https://www.sqlite.org/docs.html)

### Tutorials & Guides
- FastAPI tutorial with database
- Pydantic validation guide
- SQLite optimization guide

### Tools
- Postman or Insomnia (API testing)
- DB Browser for SQLite (database exploration)
- Docker Desktop (containerization)

---

## 🎓 By Experience Level

### Beginner (0-1 years)
Focus: File 1 (Fundamentals) only
- Basic routing
- Request/response models
- Simple CRUD operations
- Error handling

### Intermediate (1-3 years)
Focus: Files 1-2
- Advanced patterns
- Optimization
- Testing basics
- Authentication basics

### Advanced (3-5+ years)
Focus: All files
- Production deployment
- Security hardening
- Performance optimization
- Complex architectures

---

## ✨ Special Features

- ✅ **Production-quality code** with error handling
- ✅ **Comprehensive examples** for each concept
- ✅ **Interview questions** embedded in files
- ✅ **Real-world scenarios** (user management, tasks, auth)
- ✅ **Best practices** throughout
- ✅ **Testing examples** for all patterns
- ✅ **Security first** approach
- ✅ **Deployment ready** with Docker

---

## 📝 File Statistics

| File | Topics | Lines | Difficulty |
|------|--------|-------|-----------|
| fundamentals.py | Basic FastAPI, Pydantic, SQLite | 500 | ⭐⭐ |
| advanced_patterns.py | DI, pooling, caching, middleware | 800 | ⭐⭐⭐ |
| testing_deployment.py | Pytest, fixtures, Docker | 700 | ⭐⭐⭐ |
| security_auth.py | JWT, passwords, RBAC | 600 | ⭐⭐⭐⭐ |

**Total**: 2,600+ lines of code and examples

---

## 🎯 Learning Outcomes

After completing this project, you will be able to:

✅ Build REST APIs with FastAPI
✅ Design database schemas with SQLite
✅ Implement proper error handling
✅ Validate and serialize data with Pydantic
✅ Authenticate users with JWT
✅ Optimize database queries
✅ Test API endpoints
✅ Deploy with Docker
✅ Implement security best practices
✅ Handle production concerns

---

## 💬 Quick Reference

### Run Server
```bash
uvicorn fastapi_01_fundamentals:app --reload
```

### API Documentation
```
http://localhost:8000/docs (Swagger UI)
http://localhost:8000/redoc (ReDoc)
```

### Run Tests
```bash
pytest fastapi_03_testing_deployment.py -v
pytest fastapi_03_testing_deployment.py -v --cov
```

### Create Docker Image
```bash
docker build -t fastapi-app .
docker run -p 8000:8000 fastapi-app
```

---

## 🏆 Final Notes

> "The best way to learn FastAPI is to build with it. Start simple, 
> understand each concept deeply, then build increasingly complex applications."

This project provides:
1. **WHAT** - What each concept does
2. **HOW** - How to implement it
3. **WHY** - Why you'd use it
4. **WHEN** - When to use it
5. **EXAMPLES** - Real working code

That's everything needed for FastAPI mastery at a 3-5 year level.

---

**Happy learning and good luck with your FastAPI journey! 🚀**

*Last Updated: 2024*
*Python: 3.8+*
*FastAPI: 0.104+*
*SQLite: Built-in*
