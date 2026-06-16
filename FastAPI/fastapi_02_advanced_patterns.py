"""
ADVANCED FASTAPI PATTERNS & DATABASE OPTIMIZATION
Topics:
- Dependency injection and middleware
- Database connection pooling
- Query optimization and indexing
- Caching strategies
- Async database operations
- Background tasks
- Custom exception handling
"""

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from pydantic import BaseModel
from typing import Optional, List, Callable
import sqlite3
from datetime import datetime, timedelta
import asyncio
from functools import lru_cache
import time


# ============================================================================
# 1. DEPENDENCY INJECTION (Depends)
# ============================================================================

class DatabaseConfig:
    """Database configuration"""
    def __init__(self, db_path: str = "app.db", timeout: float = 5.0):
        self.db_path = db_path
        self.timeout = timeout


# Singleton-like config
config = DatabaseConfig()


def get_db_config() -> DatabaseConfig:
    """Get database configuration - can be overridden in tests"""
    return config


async def verify_api_key(
    api_key: str,
    config: DatabaseConfig = Depends(get_db_config)
) -> str:
    """Verify API key dependency"""
    if api_key != "test-key-123":
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key


# Use in endpoint:
# @app.get("/protected")
# async def protected_endpoint(api_key: str = Depends(verify_api_key)):
#     return {"message": "Access granted"}


# ============================================================================
# 2. CONNECTION POOLING
# ============================================================================

class ConnectionPool:
    """Simple connection pool for SQLite"""
    
    def __init__(self, db_path: str, pool_size: int = 5):
        self.db_path = db_path
        self.pool_size = pool_size
        self.connections: List[sqlite3.Connection] = []
        self.available = asyncio.Queue()
        self._initialized = False
    
    async def initialize(self):
        """Initialize connection pool"""
        if self._initialized:
            return
        
        for _ in range(self.pool_size):
            conn = sqlite3.connect(self.db_path, timeout=5.0)
            conn.row_factory = sqlite3.Row
            self.connections.append(conn)
            await self.available.put(conn)
        
        self._initialized = True
        print(f"✅ Connection pool initialized with {self.pool_size} connections")
    
    async def acquire(self) -> sqlite3.Connection:
        """Get connection from pool"""
        if not self._initialized:
            await self.initialize()
        return await self.available.get()
    
    async def release(self, conn: sqlite3.Connection):
        """Return connection to pool"""
        await self.available.put(conn)
    
    async def close_all(self):
        """Close all connections"""
        for conn in self.connections:
            conn.close()
        self._initialized = False


# Global pool instance
pool = ConnectionPool("app.db", pool_size=5)


async def get_db_connection() -> sqlite3.Connection:
    """Get connection from pool for dependency injection"""
    conn = await pool.acquire()
    try:
        yield conn
    finally:
        await pool.release(conn)


# ============================================================================
# 3. QUERY OPTIMIZATION
# ============================================================================

class QueryBuilder:
    """Build optimized SQL queries"""
    
    def __init__(self, table: str):
        self.table = table
        self.select_fields = ["*"]
        self.where_clauses = []
        self.params = []
        self.order_by = None
        self.limit_val = None
        self.offset_val = None
    
    def select(self, *fields) -> 'QueryBuilder':
        """Select specific fields"""
        self.select_fields = list(fields)
        return self
    
    def where(self, condition: str, *params) -> 'QueryBuilder':
        """Add WHERE clause"""
        self.where_clauses.append(condition)
        self.params.extend(params)
        return self
    
    def order_by(self, field: str, desc: bool = False) -> 'QueryBuilder':
        """Add ORDER BY"""
        self.order_by = f"{field} {'DESC' if desc else 'ASC'}"
        return self
    
    def limit(self, limit: int, offset: int = 0) -> 'QueryBuilder':
        """Add LIMIT and OFFSET"""
        self.limit_val = limit
        self.offset_val = offset
        return self
    
    def build(self) -> tuple:
        """Build SQL query and return (query, params)"""
        query = f"SELECT {', '.join(self.select_fields)} FROM {self.table}"
        
        if self.where_clauses:
            query += " WHERE " + " AND ".join(self.where_clauses)
        
        if self.order_by:
            query += f" ORDER BY {self.order_by}"
        
        if self.limit_val is not None:
            query += f" LIMIT {self.limit_val}"
            if self.offset_val:
                query += f" OFFSET {self.offset_val}"
        
        return query, self.params


# Usage:
# query, params = (QueryBuilder("users")
#     .select("id", "username", "email")
#     .where("age > ?", 18)
#     .order_by("created_at", desc=True)
#     .limit(10)
#     .build())


# ============================================================================
# 4. CACHING STRATEGIES
# ============================================================================

class Cache:
    """Simple cache with TTL"""
    
    def __init__(self, ttl_seconds: int = 300):
        self.ttl = ttl_seconds
        self.cache = {}
        self.timestamps = {}
    
    def get(self, key: str) -> Optional[any]:
        """Get cached value if not expired"""
        if key in self.cache:
            if time.time() - self.timestamps[key] < self.ttl:
                return self.cache[key]
            else:
                del self.cache[key]
                del self.timestamps[key]
        return None
    
    def set(self, key: str, value: any):
        """Cache value with timestamp"""
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    def invalidate(self, key: str = None):
        """Clear cache"""
        if key:
            self.cache.pop(key, None)
            self.timestamps.pop(key, None)
        else:
            self.cache.clear()
            self.timestamps.clear()


# Global caches
user_cache = Cache(ttl_seconds=300)  # 5 minutes
stats_cache = Cache(ttl_seconds=60)   # 1 minute


def cached(cache: Cache, key: str):
    """Decorator for caching function results"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            cached_result = cache.get(key)
            if cached_result is not None:
                return cached_result
            
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            cache.set(key, result)
            return result
        return wrapper
    return decorator


# ============================================================================
# 5. MIDDLEWARE
# ============================================================================

class RequestLoggingMiddleware:
    """Middleware to log all requests"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request_time = time.time()
        method = scope["method"]
        path = scope["path"]
        
        async def send_with_logging(message):
            if message["type"] == "http.response.start":
                status = message["status"]
                duration = time.time() - request_time
                print(f"📊 {method} {path} - {status} - {duration:.3f}s")
            await send(message)
        
        await self.app(scope, receive, send_with_logging)


class RateLimitMiddleware:
    """Simple rate limiting middleware"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        self.app = app
        self.requests_per_minute = requests_per_minute
        self.requests = {}  # IP -> list of timestamps
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        client_ip = scope["client"][0]
        now = time.time()
        
        # Clean old requests
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if now - req_time < 60
            ]
        else:
            self.requests[client_ip] = []
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            await send({
                "type": "http.response.start",
                "status": 429,
                "headers": [[b"content-type", b"application/json"]],
            })
            await send({
                "type": "http.response.body",
                "body": b'{"detail": "Rate limit exceeded"}',
            })
            return
        
        self.requests[client_ip].append(now)
        await self.app(scope, receive, send)


# ============================================================================
# 6. BACKGROUND TASKS
# ============================================================================

class EmailService:
    """Send emails in background"""
    
    @staticmethod
    async def send_email(email: str, subject: str, body: str):
        """Simulate sending email"""
        await asyncio.sleep(2)  # Simulate network delay
        print(f"📧 Email sent to {email}: {subject}")
        return True


class NotificationService:
    """Send notifications in background"""
    
    @staticmethod
    async def notify_user(user_id: int, message: str):
        """Simulate sending notification"""
        await asyncio.sleep(1)
        print(f"🔔 Notification sent to user {user_id}: {message}")


# Usage in endpoint:
# @app.post("/register")
# async def register(email: str, background_tasks: BackgroundTasks):
#     # Create user immediately
#     user = create_user(email)
#     
#     # Send welcome email in background
#     background_tasks.add_task(
#         EmailService.send_email, 
#         email, 
#         "Welcome!", 
#         "Thanks for joining!"
#     )
#     
#     return user


# ============================================================================
# 7. DATABASE INDEXES AND OPTIMIZATION
# ============================================================================

class IndexManager:
    """Manage database indexes for optimization"""
    
    @staticmethod
    def create_indexes(conn: sqlite3.Connection):
        """Create essential indexes"""
        cursor = conn.cursor()
        
        indexes = [
            # User indexes
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            
            # Task indexes
            "CREATE INDEX IF NOT EXISTS idx_tasks_user_completed ON tasks(user_id, completed)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at DESC)",
            
            # Compound indexes for common queries
            "CREATE INDEX IF NOT EXISTS idx_user_tasks ON tasks(user_id, completed, created_at DESC)",
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        print("✅ Indexes created")
    
    @staticmethod
    def analyze_query_performance(conn: sqlite3.Connection, query: str):
        """Show query execution plan"""
        cursor = conn.cursor()
        cursor.execute(f"EXPLAIN QUERY PLAN {query}")
        plan = cursor.fetchall()
        for row in plan:
            print(row)


# ============================================================================
# 8. CUSTOM VALIDATORS
# ============================================================================

from pydantic import validator, BaseModel, field_validator


class PaginationParams(BaseModel):
    """Reusable pagination parameters"""
    skip: int = 0
    limit: int = 10
    
    @field_validator('skip')
    @classmethod
    def skip_non_negative(cls, v):
        if v < 0:
            raise ValueError('skip must be non-negative')
        return v
    
    @field_validator('limit')
    @classmethod
    def limit_range(cls, v):
        if v < 1 or v > 100:
            raise ValueError('limit must be between 1 and 100')
        return v


class DateRangeQuery(BaseModel):
    """Date range for queries"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    @field_validator('end_date')
    @classmethod
    def end_after_start(cls, v, values):
        if v and values.get('start_date') and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


# ============================================================================
# 9. FASTAPI APPLICATION WITH ADVANCED PATTERNS
# ============================================================================

app = FastAPI(title="Advanced FastAPI App")

# Add middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)
app.add_middleware(GZIPMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    await pool.initialize()


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    await pool.close_all()


# ============================================================================
# 10. EXAMPLE ENDPOINTS
# ============================================================================

@app.get("/users/cached/{user_id}")
async def get_user_cached(user_id: int):
    """Get user with caching"""
    cache_key = f"user_{user_id}"
    
    # Check cache
    cached_user = user_cache.get(cache_key)
    if cached_user:
        return {"data": cached_user, "source": "cache"}
    
    # Simulate database fetch
    await asyncio.sleep(0.1)
    user = {"id": user_id, "username": f"user_{user_id}"}
    
    # Cache result
    user_cache.set(cache_key, user)
    
    return {"data": user, "source": "database"}


@app.post("/email-notification")
async def send_email_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    """Send email in background"""
    background_tasks.add_task(
        EmailService.send_email,
        email,
        "Notification",
        "This is a background task"
    )
    return {"status": "Email queued"}


@app.get("/optimized-search")
async def optimized_search(
    pagination: PaginationParams = Depends(),
    date_range: DateRangeQuery = Depends(),
):
    """Example with multiple dependencies and validation"""
    return {
        "skip": pagination.skip,
        "limit": pagination.limit,
        "start_date": date_range.start_date,
        "end_date": date_range.end_date,
        "message": "Query optimized with indexes"
    }


# ============================================================================
# INTERVIEW QUESTIONS - ADVANCED TOPICS
# ============================================================================

"""
Q1: What's dependency injection and why use Depends()?
A: Dependency injection (DI) allows passing dependencies to functions.
   Depends() integrates with FastAPI's DI system:
   - Easy to test (inject mock dependencies)
   - Reusable across endpoints
   - Automatic validation
   - Cleaner code

Q2: How to implement connection pooling?
A: Keep pre-created connections ready to reuse:
   - Reduces connection overhead
   - Better resource management
   - More concurrent requests
   - Important for production apps

Q3: What are N+1 query problems and how to avoid?
A: N+1 happens when fetching 1 item + N items per item:
   SELECT * FROM users;  -- 1 query
   FOR each user:
       SELECT * FROM tasks WHERE user_id = ?;  -- N queries
   
   Solution: Use JOINs or eager loading in single query

Q4: How to optimize database queries?
A: - Use indexes on frequently searched columns
   - Select only needed fields (no SELECT *)
   - Use LIMIT for pagination
   - Use prepared statements
   - Analyze query plans with EXPLAIN
   - Cache frequently accessed data

Q5: What's the difference between sync and async endpoints?
A: Sync: blocks on I/O operations (database, external APIs)
   Async: non-blocking, can handle multiple requests concurrently
   Async is faster for I/O-bound operations.

Q6: How to implement rate limiting?
A: Track requests per IP/user:
   - Middleware checks request count in time window
   - Return 429 if exceeded
   - Can use Redis for distributed systems
   - Configure per-endpoint limits

Q7: When to use background tasks?
A: For operations that don't affect response:
   - Sending emails
   - Processing data
   - Generating reports
   - Cleaning up resources
   - Return response immediately, process asynchronously

Q8: How to cache effectively?
A: - Set appropriate TTL based on data freshness needs
   - Invalidate cache when data changes
   - Cache expensive operations (DB queries, API calls)
   - Use cache decorators for cleaner code
   - Monitor cache hit rate

Q9: What middleware should be added to every API?
A: - CORS: Cross-origin requests
   - Request logging: Debug and monitoring
   - Error handling: Custom error responses
   - Rate limiting: Prevent abuse
   - Authentication: Verify requests
   - Compression: Reduce response size

Q10: How to handle transactions in async code?
A: FastAPI with async requires async database drivers (asyncpg, aiosqlite).
   For SQLite: use synchronous operations or offload to thread pool.
   Always handle rollback on errors.
"""

if __name__ == "__main__":
    import uvicorn
    print("Starting advanced FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
