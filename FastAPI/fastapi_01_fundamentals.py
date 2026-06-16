"""
FASTAPI + SQLITE FUNDAMENTALS
Complete guide to building REST APIs with FastAPI and SQLite

Topics:
- FastAPI basics and routing
- Request/response models with Pydantic
- SQLite database setup and migrations
- CRUD operations
- Error handling
- Async/await in FastAPI
- Type hints and validation
"""

from fastapi import FastAPI, HTTPException, Path, Query, Depends, status
from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional
import sqlite3
from datetime import datetime
from contextlib import contextmanager
import json


# ============================================================================
# 1. PYDANTIC MODELS (Request/Response Schemas)
# ============================================================================

class UserBase(BaseModel):
    """Base user model - shared fields"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr  # Validates email format
    age: Optional[int] = Field(None, ge=0, le=150)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        """Username must be alphanumeric"""
        if not v.replace('_', '').isalnum():
            raise ValueError('Username must be alphanumeric')
        return v


class UserCreate(UserBase):
    """Schema for creating user"""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating user - all fields optional"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None


class User(UserBase):
    """Complete user schema - returned from API"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True  # ORM mode - convert DB objects


class TaskBase(BaseModel):
    """Base task model"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: bool = False
    
    @validator('title')
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be whitespace only')
        return v.strip()


class TaskCreate(TaskBase):
    """Schema for creating task"""
    user_id: int


class Task(TaskBase):
    """Complete task schema"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskWithUser(Task):
    """Task with associated user"""
    user: User


# ============================================================================
# 2. DATABASE SETUP
# ============================================================================

DATABASE_URL = "fastapi_app.db"


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row  # Access columns by name
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize database with tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                age INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes for better query performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed)')
        
        conn.commit()


# ============================================================================
# 3. DATABASE OPERATIONS (Repository Pattern)
# ============================================================================

class UserRepository:
    """Handles all user database operations"""
    
    @staticmethod
    def create(user_data: UserCreate) -> int:
        """Create new user and return ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO users (username, email, password, age)
                    VALUES (?, ?, ?, ?)
                ''', (user_data.username, user_data.email, user_data.password, user_data.age))
                return cursor.lastrowid
            except sqlite3.IntegrityError as e:
                if 'username' in str(e):
                    raise ValueError("Username already exists")
                elif 'email' in str(e):
                    raise ValueError("Email already exists")
                raise
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional[dict]:
        """Fetch user by ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def get_all(skip: int = 0, limit: int = 100) -> List[dict]:
        """Fetch all users with pagination"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?',
                (limit, skip)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def update(user_id: int, user_data: UserUpdate) -> bool:
        """Update user - only provided fields"""
        update_fields = []
        values = []
        
        for field, value in user_data.dict(exclude_unset=True).items():
            update_fields.append(f"{field} = ?")
            values.append(value)
        
        if not update_fields:
            return False
        
        values.append(user_id)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE users SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP "
                f"WHERE id = ?",
                values
            )
            return cursor.rowcount > 0
    
    @staticmethod
    def delete(user_id: int) -> bool:
        """Delete user and cascade delete tasks"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            return cursor.rowcount > 0


class TaskRepository:
    """Handles all task database operations"""
    
    @staticmethod
    def create(task_data: TaskCreate) -> int:
        """Create new task"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tasks (user_id, title, description, completed)
                VALUES (?, ?, ?, ?)
            ''', (task_data.user_id, task_data.title, task_data.description, task_data.completed))
            return cursor.lastrowid
    
    @staticmethod
    def get_by_id(task_id: int) -> Optional[dict]:
        """Fetch task by ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def get_user_tasks(user_id: int, completed: Optional[bool] = None) -> List[dict]:
        """Get all tasks for a user"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if completed is None:
                cursor.execute(
                    'SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC',
                    (user_id,)
                )
            else:
                cursor.execute(
                    'SELECT * FROM tasks WHERE user_id = ? AND completed = ? ORDER BY created_at DESC',
                    (user_id, completed)
                )
            
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def update(task_id: int, task_data: TaskBase) -> bool:
        """Update task"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE tasks 
                SET title = ?, description = ?, completed = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (task_data.title, task_data.description, task_data.completed, task_id))
            return cursor.rowcount > 0
    
    @staticmethod
    def delete(task_id: int) -> bool:
        """Delete task"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            return cursor.rowcount > 0


# ============================================================================
# 4. FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Task Manager API",
    description="Complete REST API with FastAPI and SQLite",
    version="1.0.0"
)


# Startup event
@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    init_db()
    print("✅ Database initialized")


# ============================================================================
# 5. USER ENDPOINTS
# ============================================================================

@app.post("/users", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """
    Create a new user
    
    - **username**: Must be alphanumeric, 3-50 chars
    - **email**: Valid email format
    - **password**: Minimum 8 characters
    - **age**: Optional, 0-150
    """
    try:
        user_id = UserRepository.create(user)
        return {
            "id": user_id,
            "message": "User created successfully",
            "username": user.username
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/users/{user_id}", response_model=User)
async def get_user(
    user_id: int = Path(..., gt=0, description="User ID must be positive")
):
    """Get user by ID"""
    user = UserRepository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users", response_model=List[User])
async def list_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of users to return")
):
    """List all users with pagination"""
    return UserRepository.get_all(skip=skip, limit=limit)


@app.put("/users/{user_id}", response_model=dict)
async def update_user(
    user_id: int = Path(..., gt=0),
    user_data: UserUpdate = None
):
    """Update user fields"""
    # Check if user exists
    if not UserRepository.get_by_id(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    if UserRepository.update(user_id, user_data):
        return {"message": "User updated successfully"}
    return {"message": "No changes made"}


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int = Path(..., gt=0)):
    """Delete user and all associated tasks"""
    if not UserRepository.delete(user_id):
        raise HTTPException(status_code=404, detail="User not found")


# ============================================================================
# 6. TASK ENDPOINTS
# ============================================================================

@app.post("/users/{user_id}/tasks", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: int = Path(..., gt=0),
    task: TaskCreate = None
):
    """Create a new task for a user"""
    # Verify user exists
    if not UserRepository.get_by_id(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    task.user_id = user_id
    task_id = TaskRepository.create(task)
    return {
        "id": task_id,
        "message": "Task created successfully"
    }


@app.get("/users/{user_id}/tasks", response_model=List[Task])
async def get_user_tasks(
    user_id: int = Path(..., gt=0),
    completed: Optional[bool] = Query(None, description="Filter by completion status")
):
    """Get all tasks for a user"""
    if not UserRepository.get_by_id(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    return TaskRepository.get_user_tasks(user_id, completed=completed)


@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: int = Path(..., gt=0)):
    """Get task by ID"""
    task = TaskRepository.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=dict)
async def update_task(
    task_id: int = Path(..., gt=0),
    task_data: TaskBase = None
):
    """Update task"""
    if not TaskRepository.get_by_id(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    
    if TaskRepository.update(task_id, task_data):
        return {"message": "Task updated successfully"}
    return {"message": "No changes made"}


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int = Path(..., gt=0)):
    """Delete task"""
    if not TaskRepository.delete(task_id):
        raise HTTPException(status_code=404, detail="Task not found")


# ============================================================================
# 7. AGGREGATE ENDPOINTS
# ============================================================================

@app.get("/stats")
async def get_stats():
    """Get API statistics"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM users')
        user_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM tasks')
        task_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE completed = 1')
        completed_count = cursor.fetchone()['count']
        
        return {
            "total_users": user_count,
            "total_tasks": task_count,
            "completed_tasks": completed_count,
            "pending_tasks": task_count - completed_count
        }


@app.get("/users/{user_id}/stats")
async def get_user_stats(user_id: int = Path(..., gt=0)):
    """Get stats for a specific user"""
    if not UserRepository.get_by_id(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE user_id = ?', (user_id,))
        total = cursor.fetchone()['count']
        
        cursor.execute(
            'SELECT COUNT(*) as count FROM tasks WHERE user_id = ? AND completed = 1',
            (user_id,)
        )
        completed = cursor.fetchone()['count']
        
        return {
            "user_id": user_id,
            "total_tasks": total,
            "completed_tasks": completed,
            "pending_tasks": total - completed,
            "completion_rate": (completed / total * 100) if total > 0 else 0
        }


# ============================================================================
# 8. ERROR HANDLERS
# ============================================================================

from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Custom validation error response"""
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Catch-all exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# ============================================================================
# 9. HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# INTERVIEW QUESTIONS
# ============================================================================

"""
Q1: What is FastAPI and why use it over Flask?
A: FastAPI is a modern async web framework with:
   - Automatic API documentation (Swagger UI)
   - Type hints for validation
   - Async/await support for better performance
   - Built-in Pydantic validation
   - Faster development and fewer bugs

Q2: How does Pydantic validation work?
A: Pydantic validates data based on type hints and Field constraints:
   - Type coercion (converts compatible types)
   - Field validators for custom logic
   - Default values and Optional fields
   - Nested models for complex structures

Q3: What's the difference between request and response models?
A: Request model (e.g., UserCreate): validates incoming data
   Response model (e.g., User): serializes outgoing data
   Can be different! UserCreate has password, User doesn't.

Q4: Why use Repository pattern with FastAPI?
A: Separates data access from API logic:
   - Easy to test database operations
   - Can switch databases without changing endpoints
   - Reusable across endpoints
   - Cleaner code organization

Q5: How to handle database transactions in SQLite?
A: Use context managers for automatic commit/rollback.
   Try block executes SQL, commit on success, rollback on error.

Q6: What's the difference between Path, Query, and Body parameters?
A: Path: {user_id} in URL
   Query: ?skip=0&limit=10 in URL
   Body: JSON data in request body

Q7: How to implement authentication in FastAPI?
A: Use Depends() for dependency injection:
   - OAuth2 with JWT tokens
   - API keys
   - Custom authentication logic
   - Can protect endpoints with @app.get(..., dependencies=[Depends()])

Q8: How does async/await improve performance?
A: Allows handling multiple requests concurrently without threads.
   While waiting for I/O, FastAPI handles other requests.
   Much more efficient than synchronous Flask.

Q9: How to handle database migrations with SQLite?
A: Create migrations manually or use tools like Alembic.
   Version control your schema changes.
   Run migrations on startup or via CLI.

Q10: How to implement pagination properly?
A: Use skip/limit parameters with defaults.
   Limit maximum results to prevent DoS.
   Order results consistently (by creation time).
   Return total count for pagination UI.
"""

if __name__ == "__main__":
    import uvicorn
    
    # Initialize database
    init_db()
    
    # Run server
    print("Starting FastAPI server...")
    print("📚 API Docs: http://localhost:8000/docs")
    print("📖 ReDoc: http://localhost:8000/redoc")
    uvicorn.run(app, host="0.0.0.0", port=8000)
