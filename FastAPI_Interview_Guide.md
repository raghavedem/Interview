# ADVANCED FastAPI Interview Preparation Guide

## Interview Preparation for 5+ Years Experience | 80/20 Method

Complete Week Study Plan with Concepts, Patterns, Performance & Optimization

---

## TABLE OF CONTENTS

1. [Introduction](#introduction)
2. [Day 1: Async Fundamentals & Dependency Injection](#day-1-async-fundamentals--dependency-injection)
3. [Day 2: Middleware, Exception Handling & Request Lifecycle](#day-2-middleware-exception-handling--request-lifecycle)
4. [Day 3: WebSockets, Streaming & Background Tasks](#day-3-websockets-streaming--background-tasks)
5. [Day 4: Performance Optimization & Production Patterns](#day-4-performance-optimization--production-patterns)
6. [Day 5: Testing, Deployment & Interview Mastery](#day-5-testing-deployment--interview-mastery)
7. [Summary: 80/20 Concept Map](#summary-8020-concept-map)

---

## INTRODUCTION

This guide is designed for engineers with 5+ years of experience preparing for advanced FastAPI interviews. It uses the 80/20 principle to focus on the most essential concepts that will define your interview performance.

### What This Guide Covers:

- Advanced dependency injection and async patterns
- Middleware, exception handling, and request lifecycle
- WebSockets, background tasks, and streaming responses
- Performance optimization and database connection pooling
- Production patterns, testing strategies, and deployment
- Real-world interview questions and solutions

---

## DAY 1: Async Fundamentals & Dependency Injection

**Core Concepts:** Async/await, Event loop, Dependency injection, Scopes

### 1.1 AsyncIO Deep Dive

FastAPI is built on asyncio. Understanding the event loop is critical.

#### KEY CONCEPTS:
- Event loop runs one coroutine at a time
- `await` yields control back to the event loop
- Tasks and coroutines are different
- `gather` vs `create_task` have different behaviors

#### EXAMPLE - Event Loop Blocking:

```python
from fastapi import FastAPI
import asyncio
import time

app = FastAPI()

@app.get("/wrong-blocking")
async def wrong_blocking():
    # WRONG: blocking call in async function
    time.sleep(2)  # Blocks entire event loop!
    return {"message": "done"}

@app.get("/correct-async")
async def correct_async():
    # CORRECT: use asyncio
    await asyncio.sleep(2)  # Yields to event loop
    return {"message": "done"}

@app.get("/cpu-bound")
async def cpu_bound():
    # WRONG: CPU-bound work blocks event loop
    sum(i*i for i in range(10**8))  # CPU intensive!
    
    # CORRECT: use run_in_executor for blocking operations
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, cpu_intensive_function)
    return {"result": result}

def cpu_intensive_function():
    return sum(i*i for i in range(10**8))
```

#### KEY TAKEAWAY:
- Always use `await asyncio.sleep()` instead of `time.sleep()`
- Use `loop.run_in_executor()` for blocking I/O operations
- Never call blocking functions directly in async context

---

### 1.2 Advanced Dependency Injection

FastAPI's DI system is one of its greatest features. It's much more powerful than basic examples show.

#### KEY CONCEPTS:
- Dependency functions can be sync or async
- Dependencies can depend on other dependencies (composition)
- Scopes: function, path, app
- Callable classes can be used as dependencies
- Use `Depends()` for explicit dependency declaration

#### EXAMPLE - Complex DI Pattern:

```python
from fastapi import FastAPI, Depends, HTTPException
from typing import Optional
import logging
import asyncio

app = FastAPI()

# Logger dependency
def get_logger():
    return logging.getLogger(__name__)

# Database dependency with context
class DatabaseConnection:
    def __init__(self):
        self.connected = False
    
    async def connect(self):
        # Simulate DB connection
        await asyncio.sleep(0.1)
        self.connected = True
    
    async def disconnect(self):
        self.connected = False
    
    async def query(self, sql: str):
        if not self.connected:
            raise Exception("Not connected")
        return {"result": "data"}

async def get_db() -> DatabaseConnection:
    db = DatabaseConnection()
    await db.connect()
    try:
        yield db
    finally:
        await db.disconnect()

# Auth dependency that uses DB
async def get_current_user(
    db: DatabaseConnection = Depends(get_db),
    token: Optional[str] = None
):
    if not token:
        raise HTTPException(status_code=401, detail="No token")
    # Validate token using DB
    user = await db.query(f"SELECT * FROM users WHERE token={token}")
    return user

# Endpoint that uses both dependencies
@app.get("/protected")
async def protected_route(
    current_user = Depends(get_current_user),
    logger = Depends(get_logger)
):
    logger.info(f"User accessed: {current_user}")
    return {"user": current_user}

# Dependency cache: same dependency called once per request
@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db: DatabaseConnection = Depends(get_db)
):
    # Even if other functions also depend on get_db,
    # only ONE DatabaseConnection is created per request
    user = await db.query(f"SELECT * FROM users WHERE id={user_id}")
    return user
```

#### KEY TAKEAWAY:
- Dependencies are cached within a single request
- Use `yield` for cleanup (like context managers)
- Dependency functions can be async or sync
- Compose dependencies for complex logic

---

### 1.3 Dependency Scopes Deep Dive

#### SCOPE TYPES:

1. **request:** New instance per request (default)
2. **app:** Single instance for entire app lifetime
3. **middleware:** Created once, reused
4. **background:** For background tasks

#### INTERVIEW QUESTION:
**What happens if you make DB connection pool scope='app'?**

**ANSWER:**
- ✓ **Good!** Single pool shared across all requests, more efficient
- ✗ **Don't** recreate pool per request, that's wasteful
- ✗ **Make sure** it's thread-safe / async-safe

#### EXAMPLE - Database Connection Pool Scoping:

```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# APP SCOPE - Single engine for entire app
engine = None
async_session_maker = None

@app.on_event("startup")
async def startup():
    global engine, async_session_maker
    engine = create_async_engine(
        "postgresql+asyncpg://user:pass@localhost/db",
        echo=False,
        pool_size=20,
        max_overflow=0
    )
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

@app.on_event("shutdown")
async def shutdown():
    global engine
    await engine.dispose()

# REQUEST SCOPE - New session per request
async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

@app.get("/users")
async def get_users(session: AsyncSession = Depends(get_session)):
    # Session is fresh for this request
    # Multiple endpoints share same engine/pool
    pass
```

#### KEY TAKEAWAY:
- Engine should be app-scoped (created once)
- Sessions should be request-scoped (created per request)
- This prevents connection pool exhaustion

---

## DAY 2: Middleware, Exception Handling & Request Lifecycle

**Core Concepts:** Middleware layers, Request/response cycle, Exception handlers, Context

### 2.1 Middleware Order & Execution

Order matters! Middleware wraps like nested functions.

#### EXECUTION ORDER:
1. `App.add_middleware()` - reversed order (last added = first executed)
2. HTTPException handlers
3. Endpoint
4. Response processing

#### KEY INSIGHT: 
**LIFO (Last In, First Out)** for `add_middleware`

#### EXAMPLE - Middleware Order & Execution:

```python
from fastapi import FastAPI, Request
import time
import logging

app = FastAPI()

# Added LAST, executes FIRST
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logging.info(f"Path: {request.url.path} Duration: {process_time}s")
    return response

# Added FIRST, executes LAST
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # This wraps around logging_middleware
    if request.headers.get("Authorization"):
        request.state.user = "authenticated"
    else:
        request.state.user = "anonymous"
    response = await call_next(request)
    return response

@app.get("/")
async def root(request: Request):
    user = getattr(request.state, "user", "unknown")
    return {"user": user}

# ADVANCED: Custom middleware class
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get(
            "X-Correlation-ID",
            str(time.time())
        )
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response

app.add_middleware(CorrelationIdMiddleware)
```

#### KEY TAKEAWAY:
- Last middleware added = first to execute (LIFO)
- Middleware can modify request before endpoint
- Use `request.state` to pass data through middleware chain

---

### 2.2 Exception Handling Hierarchy

#### CRITICAL:
Exception handlers are checked in order registered. **First match wins!**

#### HANDLER HIERARCHY (most specific to least specific):
1. `@app.exception_handler(CustomException)`
2. `@app.exception_handler(HTTPException)`
3. `@app.exception_handler(Exception)` - catches all

#### BEST PRACTICE:
Catch specific exceptions first, general last

#### EXAMPLE - Exception Handling Hierarchy:

```python
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
import logging

app = FastAPI()

class DatabaseError(Exception):
    def __init__(self, detail: str, status_code: int = 500):
        self.detail = detail
        self.status_code = status_code

class ValidationError(Exception):
    pass

# SPECIFIC handlers first
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": "validation_failed", "detail": str(exc)}
    )

@app.exception_handler(DatabaseError)
async def db_exception_handler(request, exc):
    # Log the error for monitoring
    logging.error(f"DB Error: {exc.detail}")
    # Return user-friendly message
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "database_error", "detail": "Internal error occurred"}
    )

# GENERAL handler last
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logging.critical(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error"}
    )

@app.get("/data/{item_id}")
async def get_data(item_id: int):
    if item_id < 0:
        raise ValidationError("Item ID must be positive")
    
    if item_id == 999:
        raise DatabaseError("Connection timeout", 503)
    
    return {"item_id": item_id}
```

#### KEY TAKEAWAY:
- Register handlers from specific → general
- Log with context (don't expose internals to client)
- Always have a catch-all handler

---

### 2.3 Request Context & State

Store request-specific data in `request.state` for access across dependency chain.

#### USE CASES:
- User information (from auth middleware)
- Database sessions
- Tracing/correlation IDs
- Request-scoped configuration

#### ANTI-PATTERN:
Global variables - they're shared across requests!

#### EXAMPLE - Request Context & State:

```python
from fastapi import FastAPI, Request, Depends
import contextvars

app = FastAPI()

# Context variable for async context (better than global!)
request_id_var = contextvars.ContextVar('request_id', default='unknown')

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", "generated-123")
    request_id_var.set(request_id)  # Set in context
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Access from anywhere in async code
async def get_logging_context():
    return {
        "request_id": request_id_var.get()
    }

@app.get("/operation")
async def operation(
    request: Request,
    context = Depends(get_logging_context)
):
    return {
        "from_state": request.state.request_id,
        "from_context": context["request_id"],
        "are_same": request.state.request_id == context["request_id"]
    }
```

#### KEY TAKEAWAY:
- Use `contextvars` for async-safe context (not globals)
- Use `request.state` for request-scoped data
- Pass correlation IDs through entire request lifecycle

---

## DAY 3: WebSockets, Streaming & Background Tasks

**Core Concepts:** Real-time communication, Streaming responses, Long-running tasks, Task queues

### 3.1 WebSocket Advanced Patterns

WebSockets maintain persistent connections. Handle disconnections gracefully!

#### KEY CHALLENGES:
- Handle unexpected disconnects
- Broadcast to multiple clients
- Manage connection state
- Handle errors in receive loop

#### INTERVIEW Q:
**How do you broadcast messages to all connected clients?**

**ANSWER:**
Maintain a set of active connections, iterate and send to each

#### EXAMPLE - WebSocket Advanced Patterns:

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                # Connection might be closed
                disconnected.append(connection)
        
        # Clean up dead connections
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = {
                "from": client_id,
                "data": data,
                "timestamp": asyncio.get_event_loop().time()
            }
            # Broadcast to all clients
            await manager.broadcast(message)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast({
            "message": f"Client {client_id} left the chat"
        })
    except Exception as e:
        manager.disconnect(websocket)
        raise

# ADVANCED: Connection with authentication
@app.websocket("/ws/secure/{token}")
async def secure_websocket(websocket: WebSocket, token: str):
    # Validate token before accepting
    if not validate_token(token):
        await websocket.close(code=4001, reason="Unauthorized")
        return
    
    await manager.connect(websocket)
    # ... rest of implementation

def validate_token(token: str) -> bool:
    return token.startswith("valid_")
```

#### KEY TAKEAWAY:
- Always catch `WebSocketDisconnect` exception
- Track active connections in a manager class
- Clean up dead connections on broadcast
- Validate auth before accepting connection

---

### 3.2 Streaming Responses

Return large datasets without loading everything in memory.

#### USE CASES:
- Large file downloads
- Real-time data feeds
- CSV exports with millions of rows
- Server-sent events

#### IMPORTANT:
Generator must be async or sync (not mixed)

#### EXAMPLE - Streaming Responses:

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import io

app = FastAPI()

async def generate_large_file():
    """Async generator - must be used with StreamingResponse"""
    for i in range(10000):
        line = f"Line {i}: " + ("x" * 100) + "\n"
        yield line.encode()
        if i % 1000 == 0:
            # Allow other requests to be processed
            await asyncio.sleep(0)

@app.get("/large-file")
async def download_large_file():
    return StreamingResponse(
        generate_large_file(),
        media_type="text/plain",
        headers={"Content-Disposition": "attachment; filename=large.txt"}
    )

def sync_generate_csv():
    """Sync generator for simple file generation"""
    yield "id,name,email\n"
    for i in range(100000):
        yield f"{i},User{i},user{i}@example.com\n"

@app.get("/export-csv")
async def export_csv():
    return StreamingResponse(
        sync_generate_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=export.csv"}
    )

# Server-Sent Events (SSE) for real-time updates
async def event_generator():
    for i in range(100):
        yield f"data: {{\"count\": {i}}}\n\n"
        await asyncio.sleep(1)

@app.get("/events")
async def get_events():
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )
```

#### KEY TAKEAWAY:
- Use async generators for `StreamingResponse`
- Generators don't load entire dataset in memory
- Perfect for large exports and real-time feeds

---

### 3.3 Background Tasks

Use `BackgroundTasks` for operations that don't need to complete before response.

#### DIFFERENCES:

| Type | Use Case | Pros | Cons |
|------|----------|------|------|
| BackgroundTasks | Logging, notifications | Simple, in-process | Can't guarantee execution |
| Celery/RQ | Heavy computation | Distributed, persistent, retries | Complex setup |
| Thread pool | Blocking operations | Parallelism | Thread safety issues |

#### WHEN TO USE EACH:
- ✓ **BackgroundTasks:** Logging, notifications, non-critical updates
- ✓ **Celery:** Heavy computation, retries, scheduling, distributed tasks
- ✗ **BackgroundTasks:** Can't guarantee execution (process might crash)

#### EXAMPLE - Background Tasks:

```python
from fastapi import FastAPI, BackgroundTasks
from typing import Optional
import asyncio
import time

app = FastAPI()

def write_notification(
    email: str,
    message: str = "",
    retry_count: int = 0,
    max_retries: int = 3
):
    """Simulated notification sending"""
    print(f"Sending notification to {email}")
    time.sleep(2)  # Simulate work
    print(f"Notification sent to {email}")

async def async_task(item_id: int, delay: int = 5):
    """Async background task"""
    await asyncio.sleep(delay)
    print(f"Processed item {item_id}")

@app.post("/send-notification")
async def send_notification(
    email: str,
    message: str,
    background_tasks: BackgroundTasks
):
    # Add background task
    background_tasks.add_task(
        write_notification,
        email=email,
        message=message
    )
    # Response is sent immediately
    return {"message": "Notification sent"}

@app.post("/process/{item_id}")
async def process_item(
    item_id: int,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(async_task, item_id=item_id, delay=10)
    return {"item_id": item_id, "status": "processing"}

# ADVANCED: Background task with retry logic
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def send_email_with_retry(email: str, subject: str):
    """Automatically retries with exponential backoff"""
    print(f"Attempting to send email to {email}")
    # if random.random() > 0.5: raise Exception("Send failed")
    print(f"Email sent to {email}")

@app.post("/critical-notification")
async def critical_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(
        send_email_with_retry,
        email=email,
        subject="Important"
    )
    return {"status": "notification queued"}
```

#### KEY TAKEAWAY:
- Use `BackgroundTasks` for simple, non-critical work
- Use Celery for distributed, reliable task execution
- Always handle exceptions in background tasks

---

## DAY 4: Performance Optimization & Production Patterns

**Core Concepts:** Async DB operations, Caching, Connection pooling, Load testing

### 4.1 Database Connection Pooling

#### CRITICAL for production:
Reuse connections instead of creating new ones!

#### CONNECTION POOL BENEFITS:
- Reduces handshake overhead
- Limits resource usage
- Prevents connection exhaustion
- Enables multiple concurrent requests

#### SIZING RULES OF THUMB:
- `pool_size = (core_count * 2) + 1`
- `max_overflow = pool_size * 2` for burst handling
- For FastAPI: `pool_size = 20, overflow = 20` is common

#### INTERVIEW Q:
**What happens if pool is exhausted?**

**ANSWER:**
- New requests wait for a connection to be released
- If timeout expires, request fails with 500/503

#### EXAMPLE - Database Connection Pooling:

```python
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.pool import NullPool, AssertionPool

# PRODUCTION CONFIG - Connection pooling
engine = create_async_engine(
    "postgresql+asyncpg://user:password@localhost/db",
    echo=False,
    pool_size=20,           # Minimum connections to maintain
    max_overflow=20,        # Additional connections allowed
    pool_timeout=30,        # Timeout waiting for connection
    pool_recycle=3600,      # Recycle connections after 1 hour
    pool_pre_ping=True,     # Verify connection before use
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# TEST CONFIG - No pooling (simpler)
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    echo=True,
    poolclass=NullPool,  # No pooling for tests
)

# DEBUG CONFIG - Assert pool (catches issues)
debug_engine = create_async_engine(
    "postgresql+asyncpg://...",
    poolclass=AssertionPool,  # Fails if used from different thread
)
```

#### KEY TAKEAWAY:
- Production: pool_size=20, max_overflow=20
- Test: Use NullPool for simplicity
- Always use pool_pre_ping=True
- Recycle connections periodically

---

### 4.2 Caching Strategies

#### CACHE LAYERS (fastest to slowest):
1. In-memory (Redis) - microseconds
2. Database - milliseconds
3. External API - seconds+

#### CACHE INVALIDATION PROBLEM:
- **TTL-based:** Simple, might serve stale data
- **Event-based:** Complex, but always fresh
- **Hybrid:** Use both

#### INTERVIEW Q:
**How do you cache expensive computations?**

**ANSWER:**
1. Check cache first
2. If miss, compute result
3. Store in cache with TTL
4. Return result

#### EXAMPLE - Caching Strategies:

```python
from fastapi import FastAPI, Depends
from typing import Optional
import redis.asyncio as redis
import json
import hashlib
from functools import wraps
import time

app = FastAPI()
redis_client = None

@app.on_event("startup")
async def startup():
    global redis_client
    redis_client = await redis.from_url(
        "redis://localhost:6379/0",
        encoding="utf8",
        decode_responses=True
    )

@app.on_event("shutdown")
async def shutdown():
    await redis_client.close()

def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments"""
    key_str = json.dumps({
        "args": args,
        "kwargs": sorted(kwargs.items())
    })
    return hashlib.md5(key_str.encode()).hexdigest()

async def get_cached_data(
    user_id: int,
    cache_ttl: int = 3600
) -> dict:
    """Get data with caching"""
    key = f"user:{user_id}"
    
    # Try cache first
    cached = await redis_client.get(key)
    if cached:
        return json.loads(cached)
    
    # Cache miss - fetch from DB
    data = await fetch_from_db(user_id)
    
    # Store in cache
    await redis_client.setex(
        key,
        cache_ttl,
        json.dumps(data)
    )
    
    return data

@app.get("/user/{user_id}")
async def get_user(user_id: int):
    data = await get_cached_data(user_id)
    return data

# ADVANCED: Cache decorator
def cached(ttl: int = 3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{cache_key(args, kwargs)}"
            
            cached_value = await redis_client.get(key)
            if cached_value:
                return json.loads(cached_value)
            
            result = await func(*args, **kwargs)
            await redis_client.setex(key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

@cached(ttl=1800)
async def expensive_computation(x: int, y: int):
    """This result will be cached for 30 minutes"""
    await asyncio.sleep(2)  # Simulate expensive work
    return {"x": x, "y": y, "result": x * y}

async def fetch_from_db(user_id: int):
    # Simulate DB query
    return {"id": user_id, "name": f"User {user_id}"}
```

#### KEY TAKEAWAY:
- Use Redis for caching expensive computations
- Implement cache decorator for reusability
- Set appropriate TTL based on data staleness tolerance

---

### 4.3 Load Testing & Metrics

#### LOAD TESTING TOOLS:
- **Apache Bench (ab):** Simple GET requests
- **Locust:** Python-based, distributed
- **wrk:** High-performance HTTP load tester
- **K6:** Modern load testing

#### METRICS TO TRACK:
- Response time (p50, p95, p99)
- Throughput (requests/sec)
- Error rate
- Resource usage (CPU, memory, connections)

#### PROFILING:
- **Python profiler:** cProfile
- **Async profiler:** py-spy
- **Memory:** memory_profiler

#### EXAMPLE - Load Testing & Metrics:

```python
import asyncio
from locust import HttpUser, task, between
import cProfile
import pstats
import io

# LOCUST LOAD TEST
class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def index(self):
        self.client.get("/")
    
    @task(1)
    def view_item(self):
        self.client.get("/items/1")

# Run with: locust -f locustfile.py -u 100 -r 10

# PROFILING with cProfile
def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Your code here
    sum(i*i for i in range(10**7))
    
    profiler.disable()
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(10)
    print(s.getvalue())

# ASYNC PROFILING
# From command line:
# py-spy record -o profile.svg -- python app.py
# py-spy top -- python app.py

# MEMORY PROFILING
from memory_profiler import profile

@profile
def memory_intensive():
    large_list = [i for i in range(10**6)]
    return sum(large_list)

# Run with: python -m memory_profiler script.py
```

#### KEY TAKEAWAY:
- Use Locust for load testing FastAPI apps
- Profile with py-spy for flame graphs
- Monitor p95/p99 response times, not just averages

---

## DAY 5: Testing, Deployment & Interview Mastery

**Core Concepts:** Unit/integration testing, Fixtures, Deployment patterns, Production debugging

### 5.1 Testing Strategy for FastAPI

#### TESTING PYRAMID:
- **Unit tests (70%):** Test functions in isolation
- **Integration tests (20%):** Test components together
- **E2E tests (10%):** Test full workflows

#### FASTAPI TESTING BEST PRACTICES:
- Use `TestClient` for sync endpoints
- Use async client for async endpoints
- Mock external dependencies
- Use fixtures for setup/teardown
- Test error paths, not just happy path

#### KEY INSIGHT:
Always mock external services in tests!

#### EXAMPLE - Testing Strategy:

```python
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch, AsyncMock

app = FastAPI()

async def get_db():
    yield "db_connection"

async def get_external_api():
    return "external_service"

@app.get("/items/{item_id}")
async def get_item(
    item_id: int,
    db = Depends(get_db),
    api = Depends(get_external_api)
):
    return {"item_id": item_id, "source": "db"}

client = TestClient(app)

# UNIT TEST
def test_get_item_success():
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json()["item_id"] == 1

# DEPENDENCY OVERRIDE
def override_get_db():
    return "test_db"

@pytest.fixture
def app_with_overrides():
    app.dependency_overrides[get_db] = override_get_db
    yield app
    app.dependency_overrides.clear()

# ASYNC TEST
@pytest.mark.asyncio
async def test_async_operation():
    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/items/1")
        assert response.status_code == 200

# MOCK EXTERNAL API
@patch('external_service_call')
def test_with_mock(mock_service):
    mock_service.return_value = {"data": "mocked"}
    response = client.get("/items/1")
    mock_service.assert_called_once()
    assert response.status_code == 200

# PARAMETRIZED TESTS
@pytest.mark.parametrize("item_id,expected_status", [
    (1, 200),
    (-1, 422),
    (99999, 404),
])
def test_various_ids(item_id, expected_status):
    response = client.get(f"/items/{item_id}")
    assert response.status_code == expected_status
```

#### KEY TAKEAWAY:
- Override dependencies in tests
- Use parametrized tests for multiple scenarios
- Mock external services (API, email, etc.)

---

### 5.2 Deployment & Production Patterns

#### PRODUCTION DEPLOYMENT CHECKLIST:

- ✓ Use Gunicorn + Uvicorn workers (not uvicorn alone)
- ✓ Set workers = (2 * cores) + 1
- ✓ Configure logging properly (structured logging)
- ✓ Use environment variables for config
- ✓ Enable request timeouts
- ✓ Set up monitoring/alerting
- ✓ Use reverse proxy (nginx)
- ✓ Configure CORS properly
- ✓ Set security headers
- ✓ Use HTTPS only

#### DEPLOYMENT COMMAND:
```bash
gunicorn app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 --timeout 60
```

#### DOCKER BEST PRACTICES:
- ✓ Multi-stage builds
- ✓ Don't run as root
- ✓ Use production base image
- ✓ Copy requirements, install, then copy code

#### EXAMPLE - Production Deployment:

```python
# gunicorn_config.py
workers = 4  # (2 * cores) + 1
worker_class = "uvicorn.workers.UvicornWorker"
bind = "0.0.0.0:8000"
timeout = 60
keepalive = 5
max_requests = 1000  # Restart worker after N requests
max_requests_jitter = 50
preload_app = True  # Load app before workers

# Production FastAPI app structure
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging.config
import os
from dotenv import load_dotenv

load_dotenv()

# Structured logging
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
        }
    },
    "handlers": {
        "default": {
            "formatter": "json",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "INFO"},
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Production API",
    version="1.0.0",
    docs_url="/api/docs" if os.getenv("DEBUG") else None,
)

# Security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["example.com"])
app.add_middleware(GZIPMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    # Return Prometheus metrics
    return {"requests": 1000}
```

```dockerfile
# Dockerfile
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

# Don't run as root
RUN groupadd -r fastapi && useradd -r -g fastapi fastapi

COPY --from=builder /root/.local /home/fastapi/.local
COPY --chown=fastapi:fastapi . .

ENV PATH=/home/fastapi/.local/bin:$PATH

USER fastapi

EXPOSE 8000

CMD ["gunicorn", "app:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

#### KEY TAKEAWAY:
- Always use Gunicorn in production (multi-worker)
- Use structured logging (JSON)
- Disable docs in production
- Use health check endpoint

---

### 5.3 Interview Questions & Answers

#### QUESTION 1: Explain FastAPI's dependency injection system and when you'd use it.

**ANSWER:**
FastAPI's DI is based on callables (functions/classes) that declare dependencies. It's powerful because:
- Reusable across endpoints
- Can depend on other dependencies
- Supports scopes (request, app, etc.)
- Automatically handles async/sync
- Great for testing (override dependencies)

Example: Database sessions, authentication, config values.

---

#### QUESTION 2: What's the difference between async and sync endpoints? When use each?

**ANSWER:**
- **Async:** Returns a coroutine, yields control to event loop
- **Sync:** Blocking, holds the thread

**Async advantages:**
- ✓ Handle more concurrent requests with fewer threads
- ✓ Better for I/O operations (DB, HTTP, file)
- ✗ Can't use blocking libraries directly

**Always use async unless:**
- Library doesn't support async (use run_in_executor)
- CPU-bound work (still use async + executor)

---

#### QUESTION 3: How would you handle 10,000 concurrent connections?

**ANSWER:**

1. Use async endpoints (not sync)
2. Database connection pooling (pool_size ~ 20-50)
3. Caching layer (Redis) for frequently accessed data
4. Load balancing (nginx, HAProxy)
5. Multiple worker processes (Gunicorn + Uvicorn)
6. Monitor resource usage, set limits
7. Implement rate limiting
8. Use streaming for large responses

**Example architecture:**
```
nginx (load balancer)
  ↓
[Gunicorn with 4 workers]
  ↓
[Uvicorn worker] + [FastAPI app]
  ↓
Connection pool (20 connections) → PostgreSQL
Redis cache layer
```

---

#### QUESTION 4: How do you prevent the N+1 query problem?

**ANSWER:**
N+1 occurs when querying relationship data causes 1 initial query + N additional queries.

**Solution with SQLAlchemy:**
1. Eager loading: `selectinload()` or `joinedload()`
2. Select only needed columns
3. Batch queries: `get_list([id1, id2, id3])`
4. Caching at app level

**Code:**
```python
from sqlalchemy.orm import selectinload

query = select(User).options(selectinload(User.posts))
users = await session.execute(query)
```

---

#### QUESTION 5: Describe your approach to error handling in production.

**ANSWER:**

1. Catch specific exceptions first
2. Log with context (request ID, user, etc.)
3. Return generic messages to client
4. Alert on critical errors
5. Monitor error rates

**Implementation:**
```python
@app.exception_handler(Exception)
async def global_handler(request, exc):
    request_id = request.state.correlation_id
    logger.error(f"Error [{request_id}]: {exc}", exc_info=True)
    
    # Don't expose internal details to client
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "request_id": request_id}
    )
```

---

## SUMMARY: 80/20 Concept Map

Focus on these 20% of concepts that yield 80% of interview success:

| Day | Critical Concepts | Interview Focus |
|-----|-------------------|-----------------|
| Day 1 | Async/await, Event loop, Dependency scopes, Callables | How DI works, async vs sync, when to use each |
| Day 2 | Middleware order, Exception hierarchy, Request state | Execution flow, error handling patterns, context vars |
| Day 3 | WebSocket patterns, Streaming, Background tasks | Real-time features, handling disconnects, task queues |
| Day 4 | Connection pooling, Caching, N+1 query prevention | Performance bottlenecks, scaling strategies |
| Day 5 | Testing strategies, Deployment checklist, Debugging | Production patterns, load testing, monitoring |

---

## How to Use This Guide

### Study Strategy
1. **Day 1:** Master async/await and DI (foundation)
2. **Day 2:** Understand request lifecycle (crucial for interviews)
3. **Day 3:** Learn real-time features (differentiate yourself)
4. **Day 4:** Performance optimization (senior-level questions)
5. **Day 5:** Practice questions and production readiness

### Interview Question Categories Covered
- Dependency Injection system architecture
- Async vs Sync decision making
- Handling high concurrency (10,000+ connections)
- N+1 query prevention
- Error handling in production
- Database optimization
- Caching strategies

### Code Examples Include
- ✓ Complete, runnable examples
- ✓ Anti-patterns with explanations
- ✓ Production-ready configurations
- ✓ Common pitfalls and how to avoid them

---

## Next Steps

1. **Review Day 1-2** before your first interview (async + DI are foundational)
2. **Deep dive Day 3-4** 2-3 days before interview (differentiators)
3. **Practice Day 5** questions out loud (interview simulation)
4. **Code along** with the examples in your IDE
5. **Build a mini-project** using patterns from all 5 days

---

## Interview Success Tips

**For 5-year experienced engineers, focus on:**
- Architectural decisions (not basic syntax)
- Trade-offs and when to use each pattern
- Production deployment and monitoring
- Performance optimization under constraints
- Explaining "why" not just "how"

Good luck with your interview! 🎯
