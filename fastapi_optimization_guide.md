# FastAPI Performance Optimization Guide

## 1. FASTAPI SERVER OPTIMIZATION

### 1.1 Async/Await for I/O Operations

```python
from fastapi import FastAPI
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# Use async database driver
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/db"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# ❌ BAD - Blocking operation
@app.get("/users/bad")
def get_users_bad():
    import time
    time.sleep(2)  # Blocks the entire worker
    return {"users": []}

# ✅ GOOD - Non-blocking async operation
@app.get("/users/good")
async def get_users_good():
    await asyncio.sleep(2)  # Yields control, other requests can be processed
    return {"users": []}
```

### 1.2 Database Connection Pooling

```python
from sqlalchemy.ext.asyncio import create_async_engine

# Configure connection pool parameters
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,  # Number of connections to keep in pool
    max_overflow=10,  # Extra connections beyond pool_size
    pool_pre_ping=True,  # Test connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# For sync SQLAlchemy
from sqlalchemy import create_engine
sync_engine = create_engine(
    "postgresql://user:password@localhost/db",
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)
```

### 1.3 Uvicorn Worker Configuration

```bash
# Run with multiple workers for better concurrency
# Multiply workers by 2 x CPU cores
uvicorn main:app --workers 8 --host 0.0.0.0 --port 8000

# Or in Python
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        workers=8,
        host="0.0.0.0",
        port=8000,
        loop="uvloop",  # Faster event loop implementation
        log_level="info",
    )
```

### 1.4 Response Compression

```python
from fastapi import FastAPI
from fastapi.middleware.gzip import GZIPMiddleware

app = FastAPI()

# Compress responses larger than 1000 bytes
app.add_middleware(GZIPMiddleware, minimum_size=1000)
```

### 1.5 HTTP Caching Headers

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta

app = FastAPI()

@app.get("/cache/public")
async def public_data():
    return JSONResponse(
        {"data": "public"},
        headers={
            "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
            "ETag": "123456",  # Unique identifier for resource version
        }
    )

@app.get("/cache/private")
async def private_data():
    return JSONResponse(
        {"data": "private"},
        headers={
            "Cache-Control": "private, max-age=1800",  # Cache for 30 mins
        }
    )

@app.get("/cache/no-cache")
async def no_cache_data():
    return JSONResponse(
        {"data": "frequently changing"},
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
        }
    )
```

---

## 2. QUERY OPTIMIZATION

### 2.1 Eager Loading vs Lazy Loading

```python
from sqlalchemy import Column, Integer, String, ForeignKey, select
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession

class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    books = relationship("Book", back_populates="author")

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author_id = Column(Integer, ForeignKey("authors.id"))
    author = relationship("Author", back_populates="books")

# ❌ BAD - N+1 Query Problem: 1 query for books + 100 queries for each author
@app.get("/books/bad")
async def get_books_bad(session: AsyncSession):
    stmt = select(Book)
    books = (await session.execute(stmt)).scalars().all()
    return [{"title": b.title, "author": b.author.name} for b in books]

# ✅ GOOD - Eager loading with joinedload (1-2 queries total)
from sqlalchemy.orm import joinedload

@app.get("/books/good")
async def get_books_good(session: AsyncSession):
    stmt = select(Book).options(joinedload(Book.author))
    result = await session.execute(stmt)
    books = result.unique().scalars().all()
    return [{"title": b.title, "author": b.author.name} for b in books]

# ✅ GOOD - Using selectinload for relationships
from sqlalchemy.orm import selectinload

@app.get("/books/selectin")
async def get_books_selectin(session: AsyncSession):
    stmt = select(Book).options(selectinload(Book.author))
    result = await session.execute(stmt)
    books = result.scalars().all()
    return [{"title": b.title, "author": b.author.name} for b in books]
```

### 2.2 Select Only Required Columns

```python
from sqlalchemy import select, Column, Integer, String, Text

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(Text)  # Large field
    author = Column(String)

# ❌ BAD - Fetching all columns including large content field
@app.get("/articles/bad")
async def get_articles_bad(session: AsyncSession):
    stmt = select(Article)
    articles = (await session.execute(stmt)).scalars().all()
    return articles

# ✅ GOOD - Select only required columns
@app.get("/articles/good")
async def get_articles_good(session: AsyncSession):
    stmt = select(Article.id, Article.title, Article.author)
    results = await session.execute(stmt)
    articles = [
        {"id": id, "title": title, "author": author}
        for id, title, author in results
    ]
    return articles
```

### 2.3 Pagination

```python
from fastapi import Query
from sqlalchemy import select, func

# ✅ GOOD - Efficient pagination
@app.get("/items")
async def get_items(
    session: AsyncSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    # Get total count
    count_stmt = select(func.count(Item.id))
    total = await session.scalar(count_stmt)
    
    # Get paginated results
    stmt = select(Item).offset(skip).limit(limit)
    items = (await session.execute(stmt)).scalars().all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": items,
    }
```

### 2.4 Database Indexing

```python
from sqlalchemy import Column, Integer, String, Index, DateTime
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)  # Single column index
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String)
    
    # Composite index for common filter combinations
    __table_args__ = (
        Index('idx_user_status_created', 'status', 'created_at'),
    )

# Query that benefits from indexes
@app.get("/users/search")
async def search_users(
    session: AsyncSession,
    email: str = Query(None),
    status: str = Query(None),
):
    stmt = select(User)
    if email:
        stmt = stmt.where(User.email == email)  # Uses index
    if status:
        stmt = stmt.where(User.status == status)  # Uses composite index
    
    users = (await session.execute(stmt)).scalars().all()
    return users
```

### 2.5 Query Execution Plans

```python
@app.get("/explain")
async def explain_query(session: AsyncSession):
    # Use EXPLAIN ANALYZE to understand query performance
    query = "EXPLAIN ANALYZE SELECT * FROM books WHERE author_id = 1"
    result = await session.execute(query)
    explanation = result.fetchall()
    return {"explanation": explanation}
```

---

## 3. CACHING STRATEGIES

### 3.1 In-Memory Cache with Python `cachetools`

```python
from fastapi import FastAPI
from cachetools import TTLCache
from datetime import datetime
import time

app = FastAPI()

# Cache with 100 items, 5-minute TTL
cache = TTLCache(maxsize=100, ttl=300)

@app.get("/data/simple-cache")
async def get_data_cached(key: str):
    if key in cache:
        print(f"Cache hit for {key}")
        return cache[key]
    
    print(f"Cache miss for {key}, fetching data...")
    # Simulate expensive operation
    data = {"key": key, "value": "expensive computation", "timestamp": datetime.now()}
    cache[key] = data
    return data
```

### 3.2 Functools LRU Cache

```python
from functools import lru_cache
import asyncio

# ✅ For CPU-intensive operations (pure functions)
@lru_cache(maxsize=128)
def expensive_computation(n: int) -> int:
    """Fibonacci with caching"""
    if n < 2:
        return n
    return expensive_computation(n - 1) + expensive_computation(n - 2)

@app.get("/fibonacci/{n}")
async def get_fibonacci(n: int):
    result = expensive_computation(n)
    return {"n": n, "result": result}

# Clear cache when needed
@app.post("/cache/clear")
async def clear_cache():
    expensive_computation.cache_clear()
    return {"message": "Cache cleared"}
```

### 3.3 Redis Caching

```python
import aioredis
from fastapi import FastAPI
import json
from datetime import timedelta

app = FastAPI()

# Initialize Redis
redis = None

@app.on_event("startup")
async def startup():
    global redis
    redis = await aioredis.create_redis_pool('redis://localhost')

@app.on_event("shutdown")
async def shutdown():
    redis.close()
    await redis.wait_closed()

@app.get("/user/{user_id}")
async def get_user(user_id: int):
    cache_key = f"user:{user_id}"
    
    # Try to get from cache
    cached = await redis.get(cache_key)
    if cached:
        print(f"Cache hit for user {user_id}")
        return json.loads(cached)
    
    print(f"Cache miss for user {user_id}")
    # Simulate database query
    user_data = {"id": user_id, "name": f"User {user_id}"}
    
    # Store in Redis with 1-hour expiration
    await redis.setex(cache_key, 3600, json.dumps(user_data))
    
    return user_data

# Invalidate cache on update
@app.put("/user/{user_id}")
async def update_user(user_id: int, name: str):
    user_data = {"id": user_id, "name": name}
    
    # Invalidate cache
    await redis.delete(f"user:{user_id}")
    
    # Update database (not shown)
    return user_data
```

### 3.4 Cached Dependency Injection

```python
from fastapi import Depends, FastAPI
from functools import lru_cache

app = FastAPI()

class Settings:
    database_url: str = "postgresql://localhost/db"
    cache_ttl: int = 300
    
    def __init__(self):
        # Expensive initialization
        pass

@lru_cache()
def get_settings():
    return Settings()

@app.get("/config")
async def get_config(settings: Settings = Depends(get_settings)):
    return {"database_url": settings.database_url, "cache_ttl": settings.cache_ttl}
```

### 3.5 Custom Cache Decorator

```python
from functools import wraps
from datetime import datetime, timedelta
import inspect

class CacheDecorator:
    def __init__(self, ttl: int = 300, max_size: int = 128):
        self.ttl = ttl
        self.max_size = max_size
        self.cache = {}
        self.timestamps = {}
    
    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key = f"{func.__name__}:{args}:{kwargs}"
            
            # Check if cached and not expired
            if key in self.cache:
                if datetime.now() < self.timestamps[key]:
                    return self.cache[key]
            
            # Execute function and cache result
            result = await func(*args, **kwargs) if inspect.iscoroutinefunction(func) else func(*args, **kwargs)
            
            # Maintain max cache size
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.timestamps.keys(), key=self.timestamps.get)
                del self.cache[oldest_key]
                del self.timestamps[oldest_key]
            
            self.cache[key] = result
            self.timestamps[key] = datetime.now() + timedelta(seconds=self.ttl)
            
            return result
        
        return wrapper

cache_decorator = CacheDecorator(ttl=300, max_size=100)

@app.get("/expensive-operation/{param}")
@cache_decorator
async def expensive_operation(param: str):
    await asyncio.sleep(2)  # Simulate expensive operation
    return {"param": param, "result": "computed"}
```

### 3.6 Cache Warming (Pre-loading)

```python
from fastapi import FastAPI
import asyncio

app = FastAPI()

# Cache storage
cache_store = {}

async def warm_cache():
    """Pre-load frequently accessed data"""
    print("Warming cache...")
    
    # Pre-load top products
    popular_products = [
        {"id": 1, "name": "Product 1"},
        {"id": 2, "name": "Product 2"},
        {"id": 3, "name": "Product 3"},
    ]
    
    for product in popular_products:
        cache_store[f"product:{product['id']}"] = product
    
    print(f"Cache warmed with {len(popular_products)} items")

@app.on_event("startup")
async def startup():
    await warm_cache()

@app.get("/product/{product_id}")
async def get_product(product_id: int):
    key = f"product:{product_id}"
    if key in cache_store:
        return cache_store[key]
    
    # Fallback to database query
    return {"id": product_id, "name": "Unknown"}
```

---

## 4. PERFORMANCE MONITORING

### 4.1 Middleware for Request Timing

```python
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
import time

app = FastAPI()

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        print(f"{request.url.path} took {process_time:.3f}s")
        return response

app.add_middleware(TimingMiddleware)
```

### 4.2 Query Performance Logging

```python
from sqlalchemy import event
from sqlalchemy.engine import Engine
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())
    print(f"START Query: {statement}\nPARAMS: {params}")

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, params, context, executemany):
    total_time = time.time() - conn.info['query_start_time'].pop(-1)
    print(f"TOTAL Query Time: {total_time:.3f}s")
```

---

## SUMMARY CHECKLIST

- ✅ Use async/await for I/O operations
- ✅ Configure connection pooling (pool_size=20, max_overflow=10)
- ✅ Run multiple Uvicorn workers (2x CPU cores)
- ✅ Enable gzip compression
- ✅ Set appropriate cache headers
- ✅ Use eager loading (joinedload/selectinload)
- ✅ Select only required columns
- ✅ Implement pagination for large datasets
- ✅ Create indexes on frequently queried columns
- ✅ Use Redis for distributed caching
- ✅ Implement cache invalidation strategies
- ✅ Monitor query performance
- ✅ Warm cache on startup for frequently accessed data
