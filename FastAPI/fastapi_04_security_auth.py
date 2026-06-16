"""
FASTAPI SECURITY & AUTHENTICATION
Topics:
- JWT authentication
- Password hashing
- OAuth2 implementation
- CORS and HTTPS
- SQL injection prevention
- Input validation
- Rate limiting and DDoS protection
"""

from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthCredentials, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import sqlite3
import secrets
import hashlib


# ============================================================================
# 1. PASSWORD HASHING
# ============================================================================

# Setup password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


class PasswordManager:
    """Manage password hashing and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def generate_password_hash(password: str) -> str:
        """Alternative: manual hash with SHA256 (not recommended for production)"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${pwd_hash.hex()}"


# ============================================================================
# 2. JWT TOKEN MANAGEMENT
# ============================================================================

class TokenConfig:
    """JWT configuration"""
    SECRET_KEY = "your-secret-key-change-in-production"  # Change in production!
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7


class TokenManager:
    """Manage JWT tokens"""
    
    @staticmethod
    def create_token(
        data: dict,
        expires_delta: Optional[timedelta] = None,
        token_type: str = "access"
    ) -> str:
        """Create JWT token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            # Default expiration
            if token_type == "access":
                expire = datetime.utcnow() + timedelta(
                    minutes=TokenConfig.ACCESS_TOKEN_EXPIRE_MINUTES
                )
            else:  # refresh
                expire = datetime.utcnow() + timedelta(
                    days=TokenConfig.REFRESH_TOKEN_EXPIRE_DAYS
                )
        
        to_encode.update({"exp": expire, "type": token_type})
        
        encoded_jwt = jwt.encode(
            to_encode,
            TokenConfig.SECRET_KEY,
            algorithm=TokenConfig.ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> dict:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                TokenConfig.SECRET_KEY,
                algorithms=[TokenConfig.ALGORITHM]
            )
            
            # Verify token type
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            user_id: Optional[int] = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            return payload
        
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )


# ============================================================================
# 3. OAUTH2 AUTHENTICATION
# ============================================================================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRequest(BaseModel):
    """Token request model"""
    username: str
    password: str


class User(BaseModel):
    """User model"""
    id: int
    username: str
    email: str
    is_active: bool = True


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Dependency to get current authenticated user
    
    Usage:
    @app.get("/me")
    async def get_me(current_user: User = Depends(get_current_user)):
        return current_user
    """
    payload = TokenManager.verify_token(token)
    user_id: int = payload.get("sub")
    
    # Fetch user from database
    user = UserRepository.get_by_id(user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return User(**user)


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verify user is active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


# ============================================================================
# 4. HTTP BEARER TOKEN (API KEYS)
# ============================================================================

security = HTTPBearer()


async def verify_api_key(credentials: HTTPAuthCredentials = Depends(security)) -> str:
    """
    Verify API key authentication
    
    Usage:
    @app.get("/protected")
    async def protected(api_key: str = Depends(verify_api_key)):
        return {"message": "Success"}
    """
    # Validate API key (check against database)
    valid_keys = ["sk-12345", "sk-67890"]  # Should be in database
    
    if credentials.credentials not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    
    return credentials.credentials


# ============================================================================
# 5. ROLE-BASED ACCESS CONTROL (RBAC)
# ============================================================================

class Role(str):
    """User roles"""
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


def check_admin_role(current_user: User = Depends(get_current_active_user)):
    """
    Verify user has admin role
    
    Usage:
    @app.delete("/users/{user_id}")
    async def delete_user(
        user_id: int,
        admin: User = Depends(check_admin_role)
    ):
        return {"message": "User deleted"}
    """
    # Check user role in database
    user_role = UserRepository.get_user_role(current_user.id)
    
    if user_role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user


# ============================================================================
# 6. SQL INJECTION PREVENTION
# ============================================================================

class SafeDatabase:
    """Safe database operations to prevent SQL injection"""
    
    @staticmethod
    def safe_query(conn: sqlite3.Connection, query: str, params: tuple) -> list:
        """
        Execute query with parameterized statements (prevents SQL injection)
        
        ✅ SAFE:
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        
        ❌ UNSAFE:
        cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
        """
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def validate_column_name(column: str, allowed_columns: list) -> str:
        """Validate column names for ORDER BY clauses"""
        if column not in allowed_columns:
            raise ValueError(f"Invalid column: {column}")
        return column


# Example of vulnerable code:
"""
❌ VULNERABLE TO SQL INJECTION:
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    # If user_id = "1 OR 1=1", returns all users!
    cursor.execute(query)

✅ SAFE:
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))
    # Parameterized query prevents injection
"""


# ============================================================================
# 7. DATA VALIDATION & SANITIZATION
# ============================================================================

from pydantic import BaseModel, Field, validator


class SecureUserInput(BaseModel):
    """Validated user input"""
    username: str = Field(..., min_length=3, max_length=50, regex="^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @validator('username')
    def username_not_reserved(cls, v):
        """Prevent using reserved usernames"""
        reserved = ["admin", "root", "system"]
        if v.lower() in reserved:
            raise ValueError("Username is reserved")
        return v
    
    @validator('password')
    def password_strength(cls, v):
        """Ensure strong password"""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain digit")
        return v


# ============================================================================
# 8. CSRF PROTECTION
# ============================================================================

from fastapi import Form
import secrets


class CSRFTokenManager:
    """Manage CSRF tokens"""
    
    def __init__(self):
        self.tokens = {}  # In production, use Redis
    
    def generate_token(self, user_id: int) -> str:
        """Generate CSRF token"""
        token = secrets.token_urlsafe(32)
        self.tokens[user_id] = token
        return token
    
    def verify_token(self, user_id: int, token: str) -> bool:
        """Verify CSRF token"""
        stored_token = self.tokens.get(user_id)
        
        # Token should match and be single-use
        if stored_token and secrets.compare_digest(stored_token, token):
            del self.tokens[user_id]  # Invalidate after use
            return True
        
        return False


# ============================================================================
# 9. RATE LIMITING SECURITY
# ============================================================================

import time


class RateLimiter:
    """Rate limiting to prevent brute force attacks"""
    
    def __init__(self, max_attempts: int = 5, window_seconds: int = 300):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.attempts = {}  # IP/user -> list of timestamps
    
    def is_rate_limited(self, identifier: str) -> bool:
        """Check if identifier exceeded rate limit"""
        now = time.time()
        
        # Clean old attempts
        if identifier in self.attempts:
            self.attempts[identifier] = [
                t for t in self.attempts[identifier]
                if now - t < self.window_seconds
            ]
        else:
            self.attempts[identifier] = []
        
        # Check limit
        if len(self.attempts[identifier]) >= self.max_attempts:
            return True
        
        # Record attempt
        self.attempts[identifier].append(now)
        return False


login_limiter = RateLimiter(max_attempts=5, window_seconds=900)  # 5 attempts per 15 min


# ============================================================================
# 10. FASTAPI APPLICATION WITH SECURITY
# ============================================================================

app = FastAPI(title="Secure API")


class UserRepository:
    """User repository with password hashing"""
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional[dict]:
        """Get user by ID"""
        # Fetch from database
        return {"id": user_id, "username": "user1", "email": "user@example.com"}
    
    @staticmethod
    def get_by_username(username: str) -> Optional[dict]:
        """Get user by username"""
        # Fetch from database
        return {"id": 1, "username": username, "email": "user@example.com", "hashed_password": "..."}
    
    @staticmethod
    def create(username: str, email: str, password: str):
        """Create user with hashed password"""
        hashed_password = PasswordManager.hash_password(password)
        # Save to database with hashed password
        return {"id": 1, "username": username, "email": email}
    
    @staticmethod
    def get_user_role(user_id: int) -> str:
        """Get user role"""
        return Role.USER


@app.post("/register", response_model=dict)
async def register(user_data: SecureUserInput):
    """
    Register new user
    
    Includes:
    - Input validation
    - Password strength checking
    - Password hashing
    """
    try:
        user = UserRepository.create(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password
        )
        return {"message": "User created", "user_id": user["id"]}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Login and get tokens
    
    Includes:
    - Rate limiting
    - Password verification
    - JWT token generation
    """
    # Check rate limit
    if login_limiter.is_rate_limited(form_data.username):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts"
        )
    
    # Get user
    user = UserRepository.get_by_username(form_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not PasswordManager.verify_password(
        form_data.password,
        user["hashed_password"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create tokens
    access_token = TokenManager.create_token(
        data={"sub": user["id"], "username": user["username"]},
        token_type="access"
    )
    
    refresh_token = TokenManager.create_token(
        data={"sub": user["id"]},
        token_type="refresh"
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@app.post("/refresh", response_model=TokenResponse)
async def refresh_token(token: str):
    """
    Refresh access token using refresh token
    """
    payload = TokenManager.verify_token(token, token_type="refresh")
    user_id = payload.get("sub")
    
    # Generate new access token
    access_token = TokenManager.create_token(
        data={"sub": user_id},
        token_type="access"
    )
    
    return {
        "access_token": access_token,
        "refresh_token": token,  # Refresh token can be reused
        "token_type": "bearer"
    }


@app.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user


@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(check_admin_role)
):
    """Delete user (admin only)"""
    return {"message": f"User {user_id} deleted"}


@app.get("/api-key-test")
async def test_api_key(api_key: str = Depends(verify_api_key)):
    """Test endpoint with API key"""
    return {"message": "API key valid"}


# ============================================================================
# INTERVIEW QUESTIONS - SECURITY
# ============================================================================

"""
Q1: What's the difference between authentication and authorization?
A: Authentication: Verify who you are (login with credentials)
   Authorization: Verify what you can do (admin vs user permissions)

Q2: Why hash passwords instead of storing plaintext?
A: If database is breached, attackers can't use passwords directly.
   Hashing is one-way: can't reverse it to get plaintext.
   Use bcrypt, not MD5 or SHA (vulnerable).

Q3: How do JWT tokens work?
A: JWT has 3 parts: header.payload.signature
   - Header: algorithm (HS256)
   - Payload: user data (user_id, exp, etc)
   - Signature: HMAC of header+payload with secret key
   
   When user sends token, verify signature with secret key.
   If signature valid, token wasn't tampered with.

Q4: What's the difference between access and refresh tokens?
A: Access token: Short-lived (30 min), used for API requests
   Refresh token: Long-lived (7 days), used to get new access token
   
   If access token is compromised, it expires soon.
   Refresh token stored more securely (e.g., HttpOnly cookie).

Q5: How to prevent SQL injection?
A: Use parameterized queries (? placeholders):
   ✅ cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
   ❌ cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

Q6: What's CORS and when needed?
A: CORS allows cross-origin requests:
   - Same origin: http://localhost:3000 → http://localhost:3000 ✓
   - Different origin: http://localhost:3000 → http://localhost:8000 ✗
   
   Configure CORS middleware to allow specific origins.

Q7: How to protect against brute force attacks?
A: Rate limiting: Allow N login attempts per time window
   - Lock account after 5 failed attempts for 15 minutes
   - Log failed attempts
   - Alert on suspicious activity

Q8: What are the security headers to add?
A: - X-Content-Type-Options: nosniff
   - X-Frame-Options: DENY
   - Content-Security-Policy: Restrict content sources
   - Strict-Transport-Security: HTTPS only

Q9: How to securely handle secrets?
A: - Store in environment variables, not code
   - Use .env files (never commit)
   - Use secret management (Vault, AWS Secrets Manager)
   - Rotate secrets regularly
   - Limit access to secrets

Q10: What's OAuth2 and when use it?
A: OAuth2 is authorization protocol for delegating access.
   - User logs in via third-party (Google, GitHub)
   - Third-party returns tokens
   - App uses tokens to access user data
   - Good for "Sign in with Google" features
"""

if __name__ == "__main__":
    import uvicorn
    print("Starting secure FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
