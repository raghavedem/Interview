# Interview Q&A: React, Python, FastAPI & PostgreSQL
## For 7+ Years Experienced Developer

---

## REACT QUESTIONS

### 1. **Explain the difference between controlled and uncontrolled components. When would you use each?**

**A:** 
- **Controlled Components**: Form input values are managed by React state. Every input change updates state, giving React full control.
  ```jsx
  const [email, setEmail] = useState('');
  return <input value={email} onChange={(e) => setEmail(e.target.value)} />
  ```
  **Use when**: You need real-time validation, conditional rendering, or multiple field dependencies.

- **Uncontrolled Components**: DOM manages the input state, React accesses it via refs.
  ```jsx
  const inputRef = useRef(null);
  return <input ref={inputRef} />
  // Access via inputRef.current.value
  ```
  **Use when**: Integrating with non-React code, simple forms, file inputs.

---

### 2. **How do you optimize performance in a large React application?**

**A:**
- **Code Splitting**: Use React.lazy() and Suspense for route-based splitting
- **Memoization**: React.memo(), useMemo(), useCallback()
- **Virtual Scrolling**: Render only visible items in large lists
- **Image Optimization**: Lazy load images, use WebP, responsive sizes
- **Bundle Analysis**: Use webpack-bundle-analyzer
- **State Management**: Avoid prop drilling, use context/Redux selectively
- **Key Prop**: Always use stable keys in lists
- **Profiler**: Use React DevTools Profiler to identify bottlenecks

---

### 3. **Explain useCallback vs useMemo. When would you use each?**

**A:**
- **useCallback**: Memoizes a function reference, preventing child re-renders
  ```jsx
  const handleClick = useCallback(() => { doSomething(id); }, [id]);
  ```
  **Use**: When passing functions as dependencies or props to memoized children.

- **useMemo**: Memoizes an expensive computation result
  ```jsx
  const expensiveValue = useMemo(() => computeValue(data), [data]);
  ```
  **Use**: Heavy computations, expensive object/array creation.

---

### 4. **How do you handle state management at scale? Compare Redux, Zustand, and Context API.**

**A:**
| Aspect | Redux | Zustand | Context API |
|--------|-------|---------|-------------|
| Learning Curve | Steep | Gentle | Easy |
| Bundle Size | 9KB | 2KB | 0KB |
| DevTools | Excellent | Good | None |
| Scalability | Best | Very Good | Limited |
| Async Logic | Redux Thunk/Saga | Built-in | Needs custom |
| Performance | Good | Excellent | Can cause re-renders |

**7yr recommendation**: Use Redux for enterprise apps, Zustand for startups, Context for small/medium apps.

---

### 5. **What are React hooks pitfalls, and how do you avoid them?**

**A:**
- **Not respecting dependency arrays**: Missing deps in useEffect causes stale closures
  ```jsx
  // Wrong
  useEffect(() => { doSomething(id); }, []) // id changes ignored
  // Right
  useEffect(() => { doSomething(id); }, [id])
  ```

- **Creating objects/arrays in deps**: Causes infinite loops
  ```jsx
  // Wrong
  useEffect(() => {}, [{ id: 1 }]) // New object each render
  // Right
  useEffect(() => {}, [id]) // Use primitive value
  ```

- **Calling hooks conditionally**: Breaks hook order
- **Not cleaning up subscriptions**: Memory leaks
- **Closure over old state**: Use setState callback or ref if needed

---

### 6. **How do you handle error boundaries in React?**

**A:**
Error Boundaries catch errors in render/lifecycle. Class components only (React 19 approaching support in hooks).

```jsx
class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };
  
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  
  componentDidCatch(error, errorInfo) {
    logErrorToService(error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) return <ErrorFallback error={this.state.error} />;
    return this.props.children;
  }
}
```

**Doesn't catch**: Event handler errors (use try/catch), async code, server-side rendering.

---

### 7. **Explain the Virtual DOM and React's reconciliation algorithm (Fiber).**

**A:**
- **Virtual DOM**: In-memory representation of actual DOM. React renders to vDOM first, diffs against previous, updates only changed elements.

- **Fiber Architecture** (introduced React 16):
  - Breaks rendering into small units of work
  - Can pause/resume rendering (enables Concurrent Features)
  - Better for animation/responsiveness
  - Uses requestIdleCallback for scheduling

**Key insight**: Fiber enables interruptible rendering, crucial for keeping UI responsive during large updates.

---

### 8. **How do you test React components effectively?**

**A:**
```jsx
// Using React Testing Library (recommended)
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

test('submits form', async () => {
  render(<LoginForm />);
  fireEvent.change(screen.getByRole('textbox'), { target: { value: 'user' } });
  fireEvent.click(screen.getByRole('button', { name: /submit/i }));
  
  await waitFor(() => {
    expect(screen.getByText('Welcome')).toBeInTheDocument();
  });
});
```

**Best practices**:
- Test behavior, not implementation
- Use data-testid sparingly
- Test user interactions, not state
- Avoid snapshot testing (fragile)
- Mock external dependencies (APIs, modules)

---

## PYTHON / FASTAPI QUESTIONS

### 9. **Compare Flask, Django, and FastAPI. When would you choose FastAPI?**

**A:**
| Aspect | Flask | Django | FastAPI |
|--------|-------|--------|---------|
| Learning Curve | Easy | Moderate | Easy |
| Built-in ORM | No | Yes (Django ORM) | No |
| Type Hints | Optional | No | Required |
| Async Support | Limited | New (3.1+) | Native |
| Performance | Good | Good | Excellent |
| Speed Dev | Fast | Slow (batteries included) | Fast |
| Built-in Admin | No | Yes | No |
| API Documentation | No | No | Auto (OpenAPI) |

**Choose FastAPI when**: Building APIs, need async, type safety, auto-documentation, high performance.

---

### 10. **Explain dependency injection in FastAPI. How does it work?**

**A:**
FastAPI's dependency injection system allows reusing logic across routes.

```python
def get_query_token(token: str = Header(...)):
    return token

def get_current_user(token: str = Depends(get_query_token)):
    if token != "secret":
        raise HTTPException(status_code=401)
    return {"user": "john"}

@app.get("/items/")
async def read_items(current_user: dict = Depends(get_current_user)):
    return current_user
```

**Key features**:
- Dependencies can depend on other dependencies
- Works with class constructors
- Supports async dependencies
- Great for authentication, database sessions, validation
- Tested in isolation easily

---

### 11. **How do you handle background tasks in FastAPI? Compare Celery, RQ, and BackgroundTasks.**

**A:**
- **BackgroundTasks** (simple, in-process):
  ```python
  @app.post("/send-notification/")
  async def send_notification(email: str, background_tasks: BackgroundTasks):
      background_tasks.add_task(send_email, email, message="Hello")
      return {"message": "Notification sent in background"}
  ```
  **Use**: Simple tasks, short-lived operations.

- **Celery** (distributed, heavy):
  ```python
  @app.post("/process/")
  async def process(data: dict):
      task = process_task.delay(data)
      return {"task_id": task.id}
  ```
  **Use**: Heavy workloads, distributed systems, scaling.

- **RQ** (Redis Queue, lighter than Celery):
  ```python
  job = q.enqueue(process_data, data)
  ```
  **Use**: Middle ground, simpler than Celery.

**7yr recommendation**: Use BackgroundTasks for prototypes, Celery for production, RQ if Celery feels heavy.

---

### 12. **How do you implement pagination in FastAPI with SQLAlchemy?**

**A:**
```python
from sqlalchemy.orm import Session
from fastapi import Query

@app.get("/items/")
async def read_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    items = db.query(Item).offset(skip).limit(limit).all()
    total = db.query(Item).count()
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": items
    }
```

**Better approach with cursor-based pagination**:
```python
@app.get("/items/")
async def read_items(
    cursor: Optional[int] = Query(None),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Item)
    if cursor:
        query = query.filter(Item.id > cursor)
    items = query.limit(limit + 1).all()
    
    has_more = len(items) > limit
    return {
        "items": items[:limit],
        "next_cursor": items[limit].id if has_more else None
    }
```

---

### 13. **How do you handle async/await in FastAPI? What are common pitfalls?**

**A:**
```python
# Correct async handler
@app.get("/async-io/")
async def async_io():
    result = await asyncio.sleep(1)  # Async operation
    return {"message": "done"}

# Blocking code still works but blocks event loop
@app.get("/cpu-bound/")
async def cpu_bound():
    # DON'T: This blocks the entire event loop
    time.sleep(5)  # BAD
    
    # DO: Use run_in_executor for CPU-bound work
    result = await asyncio.get_event_loop().run_in_executor(None, expensive_function)
    return result
```

**Pitfalls**:
- Using blocking libraries in async handlers (requests → httpx)
- Not awaiting async calls
- Mixing async/sync incorrectly
- Database drivers: psycopg2 is blocking → use asyncpg or tortoise-orm

---

### 14. **Explain async context managers and their use in FastAPI.**

**A:**
```python
# Database session dependency with lifespan
@asynccontextmanager
async def get_db():
    async with AsyncSession() as session:
        yield session

# Or in FastAPI lifespan (newer approach)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    print("Starting up")
    yield
    # Shutdown code
    print("Shutting down")

app = FastAPI(lifespan=lifespan)
```

**Use for**: Resource management, database connections, external service initialization.

---

### 15. **How do you validate request data in FastAPI beyond basic types?**

**A:**
```python
from pydantic import BaseModel, Field, validator, field_validator

class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    description: Optional[str] = None
    
    @field_validator('name')
    @classmethod
    def name_alphanumeric(cls, v):
        assert v.isalnum(), 'Name must be alphanumeric'
        return v

# Custom root validator
class Order(BaseModel):
    item_count: int
    total_price: float
    
    @field_validator('total_price')
    @classmethod
    def validate_price(cls, v, info):
        if info.data['item_count'] == 0 and v > 0:
            raise ValueError('Empty order cannot have price')
        return v
```

---

### 16. **How do you handle errors and exceptions in FastAPI?**

**A:**
```python
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

# Custom exception
class ItemNotFound(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id

# Exception handler
@app.exception_handler(ItemNotFound)
async def item_not_found_handler(request: Request, exc: ItemNotFound):
    return JSONResponse(
        status_code=404,
        content={"detail": f"Item {exc.item_id} not found"}
    )

# Use in route
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if not item_exists(item_id):
        raise ItemNotFound(item_id)
    return get_item(item_id)

# Or use HTTPException directly
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if not item_exists(item_id):
        raise HTTPException(status_code=404, detail="Item not found")
    return get_item(item_id)
```

---

## POSTGRESQL QUESTIONS

### 17. **Explain ACID properties and their importance in databases.**

**A:**
- **Atomicity**: Transaction all-or-nothing. Either all operations succeed or all rollback.
- **Consistency**: Data moves from valid state to valid state. Constraints maintained.
- **Isolation**: Concurrent transactions don't interfere (SERIALIZABLE level).
- **Durability**: Committed data survives system failures.

**Example**:
```sql
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;  -- Either both succeed or both rollback
```

---

### 18. **Explain different isolation levels in PostgreSQL.**

**A:**
| Level | Dirty Reads | Non-repeatable Reads | Phantom Reads |
|-------|-------------|----------------------|---------------|
| Read Uncommitted | Possible | Possible | Possible |
| Read Committed | No | Possible | Possible |
| Repeatable Read | No | No | Possible |
| Serializable | No | No | No |

```sql
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
BEGIN;
SELECT COUNT(*) FROM orders WHERE user_id = 1;
-- If another transaction inserts, SERIALIZABLE will conflict
COMMIT;
```

**Default in PostgreSQL**: READ COMMITTED (good balance)

---

### 19. **How do you optimize slow queries? Explain EXPLAIN ANALYZE.**

**A:**
```sql
EXPLAIN ANALYZE
SELECT u.id, u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at > '2023-01-01'
GROUP BY u.id
ORDER BY order_count DESC;
```

**Output shows**:
- Seq Scan vs Index Scan
- Actual vs planned rows (shows if estimates are off)
- Execution time

**Optimization steps**:
1. Add indexes on frequently filtered columns
2. Analyze query plan (EXPLAIN ANALYZE)
3. Update statistics (ANALYZE table_name)
4. Check for sequential scans on large tables
5. Consider denormalization for complex joins

---

### 20. **How do you design database indexes effectively?**

**A:**
```sql
-- Single column index
CREATE INDEX idx_users_email ON users(email);

-- Composite index (order matters!)
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at DESC);

-- Partial index (only indexed rows matching condition)
CREATE INDEX idx_active_users ON users(email) WHERE is_active = true;

-- JSONB index for fast JSON searches
CREATE INDEX idx_metadata ON products USING gin(metadata);

-- Full-text search index
CREATE INDEX idx_posts_search ON posts USING gin(to_tsvector('english', title || ' ' || content));
```

**Best practices**:
- Index columns in WHERE, JOIN, ORDER BY
- Avoid over-indexing (slows writes)
- Use EXPLAIN to verify index usage
- Drop unused indexes
- Consider index size for large tables

---

### 21. **Explain normalization vs denormalization. When would you denormalize?**

**A:**
- **Normalization** (3NF standard): Eliminates redundancy, ensures data integrity. Requires joins.
  ```sql
  -- Normalized
  CREATE TABLE users (id, name);
  CREATE TABLE orders (id, user_id, date);  -- user_id is FK
  ```

- **Denormalization**: Store redundant data for query performance. Breaks normal forms.
  ```sql
  -- Denormalized
  CREATE TABLE orders (id, user_id, user_name, user_email, date);
  -- Avoids JOIN but risks inconsistency
  ```

**Denormalize when**:
- Read-heavy workload with complex joins
- User count field on posts (materialized via trigger)
- Cache frequently accessed data
- OLAP systems

**Stay normalized when**: Write-heavy, data consistency critical, small datasets.

---

### 22. **How do you handle migrations in production?**

**A:**
```python
# Using Alembic (SQLAlchemy migration tool)
# Create migration
alembic revision --autogenerate -m "add user email"

# Migration file: alembic/versions/xxx_add_user_email.py
def upgrade():
    op.add_column('users', sa.Column('email', sa.String(), nullable=True))
    op.create_index('idx_users_email', 'users', ['email'])

def downgrade():
    op.drop_index('idx_users_email')
    op.drop_column('users', 'email')
```

**Best practices**:
- Small, reversible migrations
- Test on production-like database first
- Plan for zero-downtime deployments
- Add columns as nullable first, backfill, then add constraints
- Don't drop columns immediately; deprecate first
- Lock strategies for large table modifications

---

### 23. **Explain transactions and deadlocks. How do you prevent them?**

**A:**
```sql
-- Deadlock scenario (two transactions, opposite lock order)
-- Transaction 1:
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

-- Transaction 2 (runs simultaneously):
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 2;
UPDATE accounts SET balance = balance + 100 WHERE id = 1;
COMMIT;
-- DEADLOCK! T1 waits for T2 to release id=2, T2 waits for T1 to release id=1
```

**Prevention**:
- Always lock resources in same order
- Use lower isolation levels when possible
- Keep transactions short
- Use advisory locks for application-level coordination
- Set statement_timeout

```sql
-- Advisory lock (application-level)
SELECT pg_advisory_lock(1);
-- Do work
SELECT pg_advisory_unlock(1);
```

---

### 24. **How do you implement full-text search in PostgreSQL?**

**A:**
```sql
-- Setup tsvector column
ALTER TABLE articles ADD COLUMN search_vector tsvector;

-- Populate with English dictionary
UPDATE articles SET search_vector = 
  to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''));

-- Create index for speed
CREATE INDEX idx_articles_search ON articles USING gin(search_vector);

-- Query
SELECT title, ts_rank(search_vector, query) as rank
FROM articles,
     plainto_tsquery('english', 'machine learning') as query
WHERE search_vector @@ query
ORDER BY rank DESC;
```

**Advanced**: Use PostgreSQL extensions like pg_trgm for fuzzy matching.

---

## INTEGRATION & ARCHITECTURE

### 25. **How do you structure a large FastAPI + React application?**

**A:**
```
project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   ├── routers/
│   │   │   ├── users.py
│   │   │   ├── orders.py
│   │   │   └── products.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   └── order.py
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   └── order.py
│   │   ├── services/
│   │   │   └── email.py
│   │   └── utils/
│   ├── tests/
│   ├── requirements.txt
│   └── alembic/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UserForm.tsx
│   │   │   └── OrderList.tsx
│   │   ├── pages/
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── hooks/
│   │   ├── store/
│   │   └── App.tsx
│   └── package.json
└── docker-compose.yml
```

---

### 26. **How do you secure a FastAPI + React application?**

**A:**
- **CORS**: 
  ```python
  from fastapi.middleware.cors import CORSMiddleware
  
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["https://yourdomain.com"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```

- **Authentication** (JWT):
  ```python
  from jose import JWTError, jwt
  from passlib.context import CryptContext
  
  pwd_context = CryptContext(schemes=["bcrypt"])
  
  @app.post("/token")
  async def login(email: str, password: str):
      user = db.query(User).filter(User.email == email).first()
      if not pwd_context.verify(password, user.hashed_password):
          raise HTTPException(status_code=401)
      token = jwt.encode({"sub": user.id}, SECRET_KEY)
      return {"access_token": token}
  
  async def get_current_user(token: str = Depends(oauth2_scheme)):
      try:
          payload = jwt.decode(token, SECRET_KEY)
          user_id = payload.get("sub")
      except JWTError:
          raise HTTPException(status_code=401)
      return db.query(User).filter(User.id == user_id).first()
  ```

- **Input validation**: Pydantic models validate all input
- **Rate limiting**: SlowAPI middleware
- **HTTPS only**: Set secure cookie flags
- **SQL injection**: Use parameterized queries (SQLAlchemy handles this)
- **CSRF**: Token-based protection
- **React security**:
  - DOMPurify for user content
  - Secure localStorage (avoid sensitive data)
  - CSP headers

---

### 27. **How would you deploy this stack? Describe your deployment strategy.**

**A:**
```yaml
# docker-compose.yml for production
version: '3.9'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: myapp
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://user:password@db:5432/myapp
      SECRET_KEY: ${SECRET_KEY}
    ports:
      - "8000:8000"
    command: uvicorn app.main:app --host 0.0.0.0 --reload

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      REACT_APP_API_URL: http://backend:8000

  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

**Deployment approach**:
1. **Local**: Docker Compose
2. **Staging**: Kubernetes or managed service (Railway, Render)
3. **Production**: 
   - Database: AWS RDS (managed PostgreSQL)
   - Backend: ECS/EKS, Heroku, Railway
   - Frontend: Vercel, Netlify, S3 + CloudFront
   - CI/CD: GitHub Actions

---

### 28. **How do you handle API versioning?**

**A:**
```python
# Version in URL path
@app.get("/v1/items/")
async def get_items_v1():
    return {"items": []}

@app.get("/v2/items/")
async def get_items_v2():
    return {"items": [], "metadata": {}}

# Or using APIRouter with prefix
v1_router = APIRouter(prefix="/v1")
v2_router = APIRouter(prefix="/v2")

@v1_router.get("/items/")
async def get_items():
    pass

app.include_router(v1_router)
app.include_router(v2_router)

# Deprecation headers
from fastapi.responses import JSONResponse

@app.get("/v1/items/", deprecated=True)
async def get_items_v1():
    return JSONResponse(
        {"items": []},
        headers={"Deprecation": "true", "Sunset": "Sun, 01 Jan 2025 00:00:00 GMT"}
    )
```

---

### 29. **How do you monitor and log a production FastAPI application?**

**A:**
```python
import logging
from pythonjsonlogger import jsonlogger

# JSON logging for better parsing
logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

# Structured logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    logger.info(
        "HTTP Request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration * 1000,
        }
    )
    return response

# Error tracking (Sentry)
import sentry_sdk

sentry_sdk.init(
    dsn="https://examplePublicKey@o0.ingest.sentry.io/0",
    traces_sample_rate=0.1,
    environment="production"
)

# Metrics (Prometheus)
from prometheus_client import Counter, Histogram

request_count = Counter('requests_total', 'Total Requests')
request_duration = Histogram('request_duration_seconds', 'Request Duration')

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    request_count.inc()
    start = time.time()
    response = await call_next(request)
    request_duration.observe(time.time() - start)
    return response
```

---

### 30. **How would you optimize a slow FastAPI + PostgreSQL application with thousands of concurrent users?**

**A:**
1. **Database**:
   - Connection pooling (pgbouncer, SQLAlchemy pool)
   - Read replicas for heavy queries
   - Horizontal partitioning for large tables
   - Caching hot data (Redis)

2. **Backend**:
   - Async/await everywhere
   - Pagination for large result sets
   - Response compression (gzip)
   - Query optimization (indexes, EXPLAIN ANALYZE)
   - Batch operations

3. **Frontend**:
   - Infinite scroll instead of pagination UI
   - Response caching (React Query, SWR)
   - Service Worker for offline support
   - Code splitting, lazy loading

4. **Infrastructure**:
   - Load balancer (Nginx)
   - CDN for static assets
   - Database connection pooling
   - Message queue (Celery) for heavy tasks
   - Horizontal scaling of backend servers

```python
# Example with caching and pooling
from sqlalchemy.pool import QueuePool
from redis import Redis

DATABASE_URL = "postgresql+asyncpg://..."
engine = create_async_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
)

redis = Redis(host='localhost', port=6379, decode_responses=True)

@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    cache_key = f"items:{skip}:{limit}"
    cached = redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    items = await get_items_from_db(skip, limit)
    redis.setex(cache_key, 3600, json.dumps(items))
    return items
```

---

## BONUS: COMMON BEHAVIORAL QUESTIONS

### 31. **Tell us about a time you debugged a complex issue across the stack.**

**Best approach**: 
- Situation: Describe the stack involved
- Task: What went wrong
- Action: How you systematically debugged (logs, profiling, isolation)
- Result: What you learned

Example: *"An API endpoint became slow during peak hours. I used database query logs to find an N+1 problem, added proper eager loading in SQLAlchemy, and implemented caching. Response time dropped from 2s to 200ms."*

---

### 32. **How do you stay current with React, Python, and database technologies?**

**Strong answer**: 
- Read release notes for each library
- Contribute to open source
- Follow key figures (Dan Abramov, Guido van Rossum, etc.)
- Participate in communities
- Build side projects exploring new patterns

---

### 33. **Describe your testing strategy.**

**Expected answer**:
- Unit tests for utilities and business logic (Pytest)
- Component tests (React Testing Library)
- Integration tests (FastAPI TestClient)
- E2E tests (Cypress, Playwright)
- Coverage target: 70-80%
- CI/CD runs all tests before merge

---

## QUICK REFERENCE

### Must-Know FastAPI Patterns
- Dependency injection
- Async handlers with proper database access
- Pydantic validation
- Background tasks
- Error handling
- Middleware

### Must-Know React Patterns
- State management strategy
- Performance optimization (memoization, code splitting)
- Error boundaries
- Testing approaches
- Hook best practices

### Must-Know PostgreSQL Concepts
- Indexing strategy
- Transaction isolation
- Query optimization
- Migrations
- Connection pooling
- Full-text search

---

**Good luck with your interview!** Focus on practical experience, trade-offs, and how you solved real problems.
