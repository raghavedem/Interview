"""
BONUS: PRACTICAL CODING CHALLENGES
Real-world scenarios combining multiple concepts

These challenges require you to synthesize knowledge from multiple files
to solve practical problems. Solutions are provided below.
"""

from typing import List, Dict, Any, Optional, Callable
from abc import ABC, abstractmethod
from functools import wraps
import time
from collections import defaultdict


# ============================================================================
# CHALLENGE 1: Rate Limiter
# ============================================================================

class RateLimiter:
    """
    CHALLENGE: Implement a rate limiter that allows N requests per time window.
    
    Requirements:
    - Track request timestamps
    - Allow specified number of requests
    - Reset after time window
    - Thread-safe
    
    Concepts Used: Closures, decorators, context managers, time management
    """
    
    def __init__(self, max_calls: int, time_window_seconds: int):
        self.max_calls = max_calls
        self.time_window = time_window_seconds
        self.calls = []
    
    def is_allowed(self) -> bool:
        """Check if request is allowed"""
        now = time.time()
        
        # Remove old calls outside time window
        self.calls = [call_time for call_time in self.calls 
                      if now - call_time < self.time_window]
        
        # Check if within limit
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False
    
    def __call__(self, func: Callable) -> Callable:
        """Use as decorator"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.is_allowed():
                raise Exception(f"Rate limit exceeded: max {self.max_calls} "
                              f"per {self.time_window} seconds")
            return func(*args, **kwargs)
        return wrapper


# Usage:
rate_limiter = RateLimiter(max_calls=3, time_window_seconds=1)

@rate_limiter
def api_call(endpoint: str) -> str:
    return f"Response from {endpoint}"


# ============================================================================
# CHALLENGE 2: Object Validation Pipeline
# ============================================================================

class Validator(ABC):
    """
    CHALLENGE: Implement validation chain for objects with multiple rules.
    
    Requirements:
    - Define validation rules for object fields
    - Chain validators together
    - Collect all errors
    - Support custom rules
    
    Concepts Used: Abstract classes, composition, generator patterns
    """
    
    @abstractmethod
    def validate(self, value: Any) -> Optional[str]:
        """Return error message if invalid, None if valid"""
        pass


class TypeValidator(Validator):
    def __init__(self, expected_type: type):
        self.expected_type = expected_type
    
    def validate(self, value: Any) -> Optional[str]:
        if not isinstance(value, self.expected_type):
            return f"Expected {self.expected_type.__name__}, got {type(value).__name__}"
        return None


class RangeValidator(Validator):
    def __init__(self, min_val: float, max_val: float):
        self.min = min_val
        self.max = max_val
    
    def validate(self, value: Any) -> Optional[str]:
        try:
            if value < self.min or value > self.max:
                return f"Value must be between {self.min} and {self.max}"
        except TypeError:
            return "Value must be comparable"
        return None


class StringLengthValidator(Validator):
    def __init__(self, min_len: int, max_len: int):
        self.min = min_len
        self.max = max_len
    
    def validate(self, value: Any) -> Optional[str]:
        if not isinstance(value, str):
            return "Value must be string"
        if len(value) < self.min or len(value) > self.max:
            return f"String length must be {self.min}-{self.max}"
        return None


class ValidatedObject:
    """Base class with validation support"""
    
    _validators: Dict[str, List[Validator]] = {}
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._validators = {}
    
    @classmethod
    def add_validator(cls, field: str, validator: Validator):
        if field not in cls._validators:
            cls._validators[field] = []
        cls._validators[field].append(validator)
    
    def validate(self) -> Dict[str, List[str]]:
        """Return dict of field -> list of errors"""
        errors = defaultdict(list)
        
        for field, validators in self._validators.items():
            if hasattr(self, field):
                value = getattr(self, field)
                for validator in validators:
                    error = validator.validate(value)
                    if error:
                        errors[field].append(error)
        
        return dict(errors)
    
    def is_valid(self) -> bool:
        return len(self.validate()) == 0


class User(ValidatedObject):
    def __init__(self, username: str, age: int, email: str):
        self.username = username
        self.age = age
        self.email = email


# Setup validators
User.add_validator('username', TypeValidator(str))
User.add_validator('username', StringLengthValidator(3, 20))
User.add_validator('age', TypeValidator(int))
User.add_validator('age', RangeValidator(18, 120))
User.add_validator('email', TypeValidator(str))


# ============================================================================
# CHALLENGE 3: Lazy Data Pipeline
# ============================================================================

def data_pipeline_challenge():
    """
    CHALLENGE: Process large dataset efficiently without loading all into memory.
    
    Requirements:
    - Load data incrementally
    - Apply multiple transformations
    - Filter records
    - Aggregate results
    - Memory efficient
    
    Concepts Used: Generators, yield, map, filter, functional programming
    """
    
    def read_data_stream(num_records: int):
        """Simulate data stream - generator"""
        for i in range(num_records):
            yield {
                'id': i,
                'value': i * 2,
                'category': 'A' if i % 2 == 0 else 'B'
            }
    
    def filter_by_category(records, category: str):
        """Filter records - generator"""
        for record in records:
            if record['category'] == category:
                yield record
    
    def transform_values(records):
        """Transform data - generator"""
        for record in records:
            yield {
                **record,
                'doubled_value': record['value'] * 2,
                'squared_value': record['value'] ** 2
            }
    
    # Pipeline
    data = read_data_stream(1000)
    filtered = filter_by_category(data, 'A')
    transformed = transform_values(filtered)
    
    # Consume pipeline (lazy evaluation)
    results = []
    for i, record in enumerate(transformed):
        results.append(record)
        if i >= 4:  # Just get first 5
            break
    
    return results


# ============================================================================
# CHALLENGE 4: Cache with TTL
# ============================================================================

class CacheWithTTL:
    """
    CHALLENGE: Implement caching with time-to-live (TTL) for entries.
    
    Requirements:
    - Cache function results
    - Entries expire after TTL
    - Automatic cleanup of expired entries
    - Can be used as decorator
    
    Concepts Used: Decorators, closures, time management, memoization
    """
    
    def __init__(self, ttl_seconds: float):
        self.ttl = ttl_seconds
        self.cache = {}
        self.timestamps = {}
    
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = time.time()
            
            # Check if cached and not expired
            if key in self.cache:
                if now - self.timestamps[key] < self.ttl:
                    return self.cache[key]
            
            # Compute and cache
            result = func(*args, **kwargs)
            self.cache[key] = result
            self.timestamps[key] = now
            return result
        
        return wrapper


# Usage:
@CacheWithTTL(ttl_seconds=2)
def expensive_operation(x: int) -> int:
    """Cached for 2 seconds"""
    print(f"Computing for {x}...")
    return x ** 2


# ============================================================================
# CHALLENGE 5: Event System with Observer Pattern
# ============================================================================

class Event:
    """
    CHALLENGE: Implement publish-subscribe event system.
    
    Requirements:
    - Register event handlers
    - Publish events with data
    - Handlers can be unregistered
    - Support multiple subscribers
    - Thread-safe (bonus)
    
    Concepts Used: Design patterns, composition, type hints, callbacks
    """
    
    def __init__(self, name: str):
        self.name = name
        self._handlers: List[Callable] = []
    
    def subscribe(self, handler: Callable) -> Callable:
        """Register handler - can be used as decorator"""
        self._handlers.append(handler)
        return handler
    
    def unsubscribe(self, handler: Callable):
        """Unregister handler"""
        if handler in self._handlers:
            self._handlers.remove(handler)
    
    def publish(self, **data):
        """Trigger all handlers"""
        for handler in self._handlers:
            handler(self.name, **data)


class EventEmitter:
    """Manager for multiple events"""
    
    def __init__(self):
        self.events: Dict[str, Event] = {}
    
    def get_event(self, name: str) -> Event:
        if name not in self.events:
            self.events[name] = Event(name)
        return self.events[name]


# Usage:
emitter = EventEmitter()
user_created = emitter.get_event('user_created')

@user_created.subscribe
def log_user_created(event_name: str, user_id: int, username: str):
    print(f"[LOG] {event_name}: user_id={user_id}, username={username}")

@user_created.subscribe
def send_email(event_name: str, user_id: int, username: str):
    print(f"[EMAIL] Sending welcome email to {username}")


# ============================================================================
# CHALLENGE 6: Configuration Manager with Context
# ============================================================================

class ConfigurationManager:
    """
    CHALLENGE: Manage application configuration with temporary overrides.
    
    Requirements:
    - Load configuration
    - Allow temporary overrides in context
    - Restore original after context
    - Thread-safe (bonus)
    
    Concepts Used: Context managers, __enter__/__exit__, state management
    """
    
    def __init__(self, **defaults):
        self._config = defaults.copy()
        self._overrides_stack = []
    
    def __enter__(self):
        self._overrides_stack.append(self._config.copy())
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._config = self._overrides_stack.pop()
    
    def set(self, key: str, value: Any):
        self._config[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)
    
    def override(self, **overrides):
        """Context manager for temporary overrides"""
        original = self._config.copy()
        self._config.update(overrides)
        
        class OverrideContext:
            def __enter__(self):
                return self
            
            def __exit__(self, *args):
                # Restore original
                self._config.clear()
                self._config.update(original)
        
        ctx = OverrideContext()
        ctx._config = self._config
        return ctx


# Usage:
config = ConfigurationManager(debug=False, timeout=30, retries=3)

# Normal usage
print(f"Debug: {config.get('debug')}")

# Temporary override
with config.override(debug=True, timeout=60):
    print(f"Debug: {config.get('debug')}")
    print(f"Timeout: {config.get('timeout')}")

# Back to normal
print(f"Debug: {config.get('debug')}")
print(f"Timeout: {config.get('timeout')}")


# ============================================================================
# CHALLENGE 7: Dependency Injector
# ============================================================================

class DependencyInjector:
    """
    CHALLENGE: Implement simple dependency injection container.
    
    Requirements:
    - Register dependencies (singletons, factories)
    - Resolve dependencies
    - Automatic instantiation
    - Support parameters
    
    Concepts Used: Closures, factories, composition, registry pattern
    """
    
    def __init__(self):
        self._singletons = {}
        self._factories = {}
    
    def register_singleton(self, name: str, instance: Any):
        """Register already created instance"""
        self._singletons[name] = instance
    
    def register_factory(self, name: str, factory: Callable):
        """Register factory function"""
        self._factories[name] = factory
    
    def get(self, name: str) -> Any:
        """Resolve dependency"""
        if name in self._singletons:
            return self._singletons[name]
        
        if name in self._factories:
            return self._factories[name]()
        
        raise ValueError(f"Dependency '{name}' not registered")


# Usage:
class Database:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
    
    def query(self, sql: str) -> List[Dict]:
        return [{"result": "mock data"}]


class UserRepository:
    def __init__(self, db: Database):
        self.db = db
    
    def get_user(self, user_id: int) -> Dict:
        return {"id": user_id, "name": "John"}


# Setup DI
injector = DependencyInjector()
injector.register_singleton('db', Database("postgresql://localhost"))
injector.register_factory('user_repo', 
                         lambda: UserRepository(injector.get('db')))

# Usage
repo = injector.get('user_repo')
user = repo.get_user(1)


# ============================================================================
# TEST ALL CHALLENGES
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("PRACTICAL CODING CHALLENGES")
    print("=" * 70)
    
    # Challenge 1: Rate Limiter
    print("\n1. RATE LIMITER:")
    try:
        for i in range(5):
            result = api_call(f"/users/{i}")
            print(f"  Request {i+1}: {result}")
    except Exception as e:
        print(f"  Rate limit hit: {e}")
    
    # Challenge 2: Object Validation
    print("\n2. OBJECT VALIDATION:")
    user1 = User("john_doe", 25, "john@example.com")
    print(f"  User 1 valid: {user1.is_valid()}")
    
    user2 = User("ab", 150, "invalid")
    errors = user2.validate()
    if errors:
        print(f"  User 2 errors:")
        for field, error_list in errors.items():
            for error in error_list:
                print(f"    - {field}: {error}")
    
    # Challenge 3: Lazy Pipeline
    print("\n3. LAZY DATA PIPELINE:")
    pipeline_results = data_pipeline_challenge()
    print(f"  Processed {len(pipeline_results)} records")
    if pipeline_results:
        print(f"  First record: {pipeline_results[0]}")
    
    # Challenge 4: Cache with TTL
    print("\n4. CACHE WITH TTL:")
    print("  First call (computes):")
    result1 = expensive_operation(5)
    print(f"  Result: {result1}")
    
    print("  Second call (cached):")
    result2 = expensive_operation(5)
    print(f"  Result: {result2}")
    
    print("  Waiting 3 seconds for cache expiry...")
    time.sleep(3)
    print("  Third call (recomputes after TTL):")
    result3 = expensive_operation(5)
    print(f"  Result: {result3}")
    
    # Challenge 5: Event System
    print("\n5. EVENT SYSTEM:")
    user_created.publish(user_id=123, username="alice")
    
    # Challenge 6: Configuration Manager
    print("\n6. CONFIGURATION MANAGER:")
    config = ConfigurationManager(debug=False, timeout=30)
    print(f"  Original - Debug: {config.get('debug')}, "
          f"Timeout: {config.get('timeout')}")
    
    try:
        with config.override(debug=True, timeout=60):
            print(f"  Overridden - Debug: {config.get('debug')}, "
                  f"Timeout: {config.get('timeout')}")
    except:
        pass
    
    print(f"  Restored - Debug: {config.get('debug')}, "
          f"Timeout: {config.get('timeout')}")
    
    # Challenge 7: Dependency Injector
    print("\n7. DEPENDENCY INJECTOR:")
    repo = injector.get('user_repo')
    user = repo.get_user(1)
    print(f"  Retrieved user: {user}")
    
    print("\n" + "=" * 70)
    print("All challenges completed! Combine these patterns for production code.")
    print("=" * 70)
