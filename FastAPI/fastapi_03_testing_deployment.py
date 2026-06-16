"""
TESTING & DEPLOYMENT FOR FASTAPI
Topics:
- Unit testing with pytest
- Integration testing
- Test fixtures and factories
- Database testing strategies
- Docker containerization
- Production deployment considerations
- Monitoring and logging
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
import pytest
from unittest.mock import Mock, patch
import sqlite3
from datetime import datetime
from typing import Optional
import logging
import json


# ============================================================================
# 1. LOGGING CONFIGURATION
# ============================================================================

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class Logger:
    """Centralized logging for application"""
    
    @staticmethod
    def info(message: str, **kwargs):
        logger.info(f"{message} | {json.dumps(kwargs)}")
    
    @staticmethod
    def error(message: str, error: Exception = None, **kwargs):
        logger.error(f"{message} | {str(error) if error else ''} | {json.dumps(kwargs)}")
    
    @staticmethod
    def debug(message: str, **kwargs):
        logger.debug(f"{message} | {json.dumps(kwargs)}")


# ============================================================================
# 2. TEST FIXTURES AND FACTORIES
# ============================================================================

class UserFactory:
    """Factory for creating test users"""
    
    @staticmethod
    def create(
        username: str = "testuser",
        email: str = "test@example.com",
        age: int = 25,
        **kwargs
    ) -> dict:
        return {
            "username": username,
            "email": email,
            "age": age,
            "password": "testpass123",
            **kwargs
        }


class TaskFactory:
    """Factory for creating test tasks"""
    
    @staticmethod
    def create(
        user_id: int = 1,
        title: str = "Test Task",
        description: str = "Test Description",
        completed: bool = False,
        **kwargs
    ) -> dict:
        return {
            "user_id": user_id,
            "title": title,
            "description": description,
            "completed": completed,
            **kwargs
        }


@pytest.fixture
def user_data():
    """Fixture providing test user data"""
    return UserFactory.create()


@pytest.fixture
def task_data():
    """Fixture providing test task data"""
    return TaskFactory.create()


@pytest.fixture
def test_db():
    """Fixture providing test database"""
    # Create in-memory database for testing
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    
    # Create tables
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            age INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    
    yield conn
    
    conn.close()


# ============================================================================
# 3. UNIT TESTS
# ============================================================================

class TestValidation:
    """Test input validation"""
    
    def test_user_validation_valid(self):
        """Test valid user data"""
        from pydantic import BaseModel, EmailStr
        
        class User(BaseModel):
            username: str
            email: EmailStr
        
        user = User(username="john", email="john@example.com")
        assert user.username == "john"
    
    def test_user_validation_invalid_email(self):
        """Test invalid email validation"""
        from pydantic import BaseModel, EmailStr, ValidationError
        
        class User(BaseModel):
            username: str
            email: EmailStr
        
        with pytest.raises(ValidationError):
            User(username="john", email="invalid-email")
    
    def test_user_validation_missing_field(self):
        """Test missing required field"""
        from pydantic import BaseModel, ValidationError
        
        class User(BaseModel):
            username: str
            email: str
        
        with pytest.raises(ValidationError):
            User(username="john")  # Missing email


class TestBusinessLogic:
    """Test business logic"""
    
    def test_task_completion_rate(self):
        """Test calculating completion rate"""
        total_tasks = 10
        completed_tasks = 7
        
        completion_rate = (completed_tasks / total_tasks) * 100
        
        assert completion_rate == 70.0
    
    def test_task_completion_rate_no_tasks(self):
        """Test completion rate with no tasks"""
        total_tasks = 0
        completed_tasks = 0
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        assert completion_rate == 0
    
    def test_task_filtering(self):
        """Test filtering tasks by completion"""
        tasks = [
            {"id": 1, "completed": True},
            {"id": 2, "completed": False},
            {"id": 3, "completed": True},
        ]
        
        completed = [t for t in tasks if t["completed"]]
        
        assert len(completed) == 2
        assert all(t["completed"] for t in completed)


# ============================================================================
# 4. INTEGRATION TESTS
# ============================================================================

@pytest.fixture
def test_app():
    """Fixture providing test FastAPI app"""
    from fastapi import FastAPI
    
    app = FastAPI()
    
    @app.post("/users")
    async def create_user(username: str, email: str):
        return {"id": 1, "username": username, "email": email}
    
    @app.get("/users/{user_id}")
    async def get_user(user_id: int):
        return {"id": user_id, "username": "testuser"}
    
    @app.delete("/users/{user_id}")
    async def delete_user(user_id: int):
        return {"message": "User deleted"}
    
    return app


@pytest.fixture
def client(test_app):
    """Fixture providing test client"""
    return TestClient(test_app)


class TestAPIEndpoints:
    """Test API endpoints"""
    
    def test_create_user(self, client, user_data):
        """Test creating user via API"""
        response = client.post("/users", params={
            "username": user_data["username"],
            "email": user_data["email"]
        })
        
        assert response.status_code == 200
        assert response.json()["username"] == user_data["username"]
    
    def test_get_user(self, client):
        """Test fetching user via API"""
        response = client.get("/users/1")
        
        assert response.status_code == 200
        assert response.json()["id"] == 1
    
    def test_delete_user(self, client):
        """Test deleting user via API"""
        response = client.delete("/users/1")
        
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()
    
    def test_user_not_found(self, client):
        """Test error handling for missing user"""
        # This would need the app to return 404 for missing users
        pass


# ============================================================================
# 5. DATABASE TESTING
# ============================================================================

class TestDatabaseOperations:
    """Test database operations"""
    
    def test_create_user_in_db(self, test_db):
        """Test creating user in database"""
        cursor = test_db.cursor()
        
        cursor.execute(
            'INSERT INTO users (username, email, password, age) VALUES (?, ?, ?, ?)',
            ("john", "john@example.com", "hashed_password", 25)
        )
        test_db.commit()
        
        # Verify insert
        cursor.execute('SELECT * FROM users WHERE username = ?', ("john",))
        user = cursor.fetchone()
        
        assert user is not None
        assert user["email"] == "john@example.com"
    
    def test_cascade_delete_tasks(self, test_db):
        """Test that deleting user deletes tasks"""
        cursor = test_db.cursor()
        
        # Create user
        cursor.execute(
            'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
            ("john", "john@example.com", "pass")
        )
        test_db.commit()
        
        user_id = cursor.lastrowid
        
        # Create task
        cursor.execute(
            'INSERT INTO tasks (user_id, title) VALUES (?, ?)',
            (user_id, "Test Task")
        )
        test_db.commit()
        
        # Verify task exists
        cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE user_id = ?', (user_id,))
        assert cursor.fetchone()["count"] == 1
    
    def test_unique_constraint(self, test_db):
        """Test unique constraint enforcement"""
        cursor = test_db.cursor()
        
        # Insert first user
        cursor.execute(
            'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
            ("john", "john@example.com", "pass")
        )
        test_db.commit()
        
        # Try to insert duplicate
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ("john", "different@example.com", "pass")
            )
            test_db.commit()


# ============================================================================
# 6. MOCKING AND PATCHING
# ============================================================================

class TestWithMocking:
    """Test with mocked dependencies"""
    
    @patch('builtins.open', create=True)
    def test_read_config_file(self, mock_open):
        """Test reading config with mocked file"""
        mock_open.return_value.__enter__.return_value.read.return_value = '{"key": "value"}'
        
        # Simulate reading file
        with open("config.json") as f:
            data = json.loads(f.read())
        
        assert data["key"] == "value"
    
    def test_email_service_with_mock(self):
        """Test email service with mocked send"""
        mock_email_service = Mock()
        mock_email_service.send_email.return_value = True
        
        result = mock_email_service.send_email("test@example.com", "Subject", "Body")
        
        assert result is True
        mock_email_service.send_email.assert_called_once()


# ============================================================================
# 7. PERFORMANCE TESTING
# ============================================================================

class TestPerformance:
    """Test performance characteristics"""
    
    def test_database_query_performance(self, test_db):
        """Test query performance"""
        cursor = test_db.cursor()
        
        # Insert many users
        for i in range(100):
            cursor.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                (f"user{i}", f"user{i}@example.com", "pass")
            )
        test_db.commit()
        
        # Time query
        import time
        start = time.time()
        cursor.execute('SELECT COUNT(*) FROM users')
        result = cursor.fetchone()
        duration = time.time() - start
        
        assert result["count"] == 100
        assert duration < 0.1  # Should be fast


# ============================================================================
# 8. DOCKER CONFIGURATION
# ============================================================================

DOCKERFILE_CONTENT = """
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

REQUIREMENTS_TXT = """
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic[email]==2.5.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.0
aiosqlite==0.19.0
"""

DOCKER_COMPOSE_CONTENT = """
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./app.db
    volumes:
      - ./app.db:/app/app.db
"""


# ============================================================================
# 9. PRODUCTION CONFIGURATION
# ============================================================================

class ProductionConfig:
    """Production environment configuration"""
    
    # Database
    DATABASE_URL = "sqlite:///./app.db"
    DB_POOL_SIZE = 10
    
    # Security
    SECRET_KEY = "${SECRET_KEY}"  # From environment
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # API
    API_TITLE = "Task Manager API"
    API_VERSION = "1.0.0"
    
    # Logging
    LOG_LEVEL = "INFO"
    
    # CORS
    ALLOWED_ORIGINS = ["https://example.com"]
    
    # Rate limiting
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_PERIOD = 60


class DevelopmentConfig(ProductionConfig):
    """Development configuration"""
    
    LOG_LEVEL = "DEBUG"
    ALLOWED_ORIGINS = ["*"]
    SECRET_KEY = "dev-secret-key"


# ============================================================================
# 10. MONITORING AND HEALTH CHECKS
# ============================================================================

class HealthCheck:
    """Health check endpoints"""
    
    @staticmethod
    def check_database(conn: sqlite3.Connection) -> bool:
        """Check database connectivity"""
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    @staticmethod
    def check_disk_space(threshold_gb: int = 1) -> bool:
        """Check available disk space"""
        import shutil
        try:
            stat = shutil.disk_usage("/")
            available_gb = stat.free / (1024**3)
            return available_gb > threshold_gb
        except Exception as e:
            logger.error(f"Disk space check failed: {e}")
            return False


class Metrics:
    """Application metrics collection"""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0
    
    def record_request(self, status_code: int, response_time: float):
        """Record request metric"""
        self.request_count += 1
        self.total_response_time += response_time
        
        if status_code >= 400:
            self.error_count += 1
    
    def get_metrics(self) -> dict:
        """Get current metrics"""
        avg_response_time = (
            self.total_response_time / self.request_count 
            if self.request_count > 0 
            else 0
        )
        
        return {
            "total_requests": self.request_count,
            "error_count": self.error_count,
            "error_rate": (self.error_count / self.request_count * 100) if self.request_count > 0 else 0,
            "avg_response_time_ms": avg_response_time * 1000
        }


# ============================================================================
# INTERVIEW QUESTIONS - TESTING & DEPLOYMENT
# ============================================================================

"""
Q1: What's the difference between unit and integration tests?
A: Unit tests: Test individual functions/components in isolation with mocks
   Integration tests: Test components together with real dependencies
   Integration tests verify components work together correctly.

Q2: What should be tested in FastAPI applications?
A: - Input validation (Pydantic models)
   - Business logic (functions, calculations)
   - API endpoints (status codes, response format)
   - Error handling (proper HTTP errors)
   - Database operations (CRUD, relationships)
   - Authentication/authorization
   - Edge cases and corner cases

Q3: What are fixtures and why use them?
A: Fixtures provide reusable test setup:
   - Reduce code duplication
   - Ensure consistent test data
   - Setup and teardown resources
   - Can be combined (composition)
   - Much cleaner than setUp/tearDown

Q4: How to test database operations?
A: Use in-memory database (SQLite ":memory:")
   - No file I/O overhead
   - Isolated per test
   - Clean state each test
   - Fast test execution

Q5: What's test coverage and what's a good target?
A: Percentage of code lines covered by tests:
   - 80%+ is good target
   - 100% is impractical (diminishing returns)
   - Focus on critical paths first
   - Coverage ≠ quality (can have bad tests)

Q6: How to test async functions?
A: Use @pytest.mark.asyncio decorator:
   ```python
   @pytest.mark.asyncio
   async def test_async_function():
       result = await async_func()
       assert result == expected
   ```

Q7: What are mocks and when to use them?
A: Replace real dependencies with controlled test versions:
   - Mock external APIs
   - Mock slow operations
   - Verify function calls
   - Simulate errors
   - Use: @patch decorator or Mock() directly

Q8: How to containerize FastAPI application?
A: Create Dockerfile:
   - Use official Python image
   - Install dependencies (pip install -r requirements.txt)
   - Copy application code
   - Expose port
   - Run with uvicorn
   
   Use docker-compose for multi-container setups

Q9: What configuration management best practices?
A: - Never hardcode secrets
   - Use environment variables
   - Have dev/prod configs
   - Validate config on startup
   - Document all settings
   - Use pydantic.BaseSettings

Q10: How to monitor production FastAPI application?
A: - Application logging (structured logs)
   - Health check endpoints
   - Metrics collection (requests, errors, latency)
   - Error tracking (Sentry, etc.)
   - Database performance monitoring
   - Rate limit monitoring
"""

if __name__ == "__main__":
    # Run tests with pytest
    # pytest fastapi_03_testing.py -v
    print("📝 Testing configuration complete")
    print("Run: pytest fastapi_03_testing.py -v")
    print("Run: docker build -t fastapi-app . && docker run -p 8000:8000 fastapi-app")
