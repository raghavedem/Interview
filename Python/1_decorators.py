"""
DECORATORS & HIGHER-ORDER FUNCTIONS
Essential for: Logging, timing, caching, authentication, middleware

Key Concepts:
- Functions as first-class objects
- Closures and scope
- Wrapping functions with additional behavior
- Parameterized decorators
- Stacking decorators
"""

import functools
import time
from typing import Callable, Any, TypeVar
from datetime import datetime

# ============================================================================
# 1. BASIC DECORATOR
# ============================================================================

def simple_decorator(func: Callable) -> Callable:
    """Wraps a function to add behavior before/after execution"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[BEFORE] Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"[AFTER] {func.__name__} completed")
        return result
    return wrapper


@simple_decorator
def greet(name: str) -> str:
    """Example function with decorator"""
    return f"Hello, {name}!"


# ============================================================================
# 2. PARAMETERIZED DECORATOR
# ============================================================================

def repeat(times: int) -> Callable:
    """Decorator that repeats function execution"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            results = []
            for i in range(times):
                result = func(*args, **kwargs)
                results.append(result)
            return results
        return wrapper
    return decorator


@repeat(times=3)
def get_current_time() -> str:
    return datetime.now().strftime("%H:%M:%S")


# ============================================================================
# 3. TIMING DECORATOR (Common Interview Question)
# ============================================================================

def timer(func: Callable) -> Callable:
    """Measures function execution time"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        elapsed = end - start
        print(f"⏱️  {func.__name__} took {elapsed:.4f} seconds")
        return result
    return wrapper


@timer
def slow_function(n: int) -> int:
    """Simulates a slow operation"""
    time.sleep(0.5)
    return sum(range(n))


# ============================================================================
# 4. MEMOIZATION DECORATOR (Caching)
# ============================================================================

def memoize(func: Callable) -> Callable:
    """Caches function results based on arguments"""
    cache = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create a hashable key from args and kwargs
        key = (args, tuple(sorted(kwargs.items())))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
            print(f"💾 Cached {func.__name__}{args}")
        else:
            print(f"✓ Using cached result for {func.__name__}{args}")
        
        return cache[key]
    
    wrapper.cache = cache
    return wrapper


@memoize
def fibonacci(n: int) -> int:
    """Classic recursive function (inefficient without caching)"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


# ============================================================================
# 5. STACKING DECORATORS
# ============================================================================

def uppercase(func: Callable) -> Callable:
    """Convert result to uppercase"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result.upper() if isinstance(result, str) else result
    return wrapper


def add_prefix(prefix: str) -> Callable:
    """Add prefix to string result"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return f"{prefix} {result}" if isinstance(result, str) else result
        return wrapper
    return decorator


@add_prefix("[INFO]")
@uppercase
@simple_decorator
def format_message(msg: str) -> str:
    return f"message: {msg}"


# ============================================================================
# 6. CLASS-BASED DECORATOR
# ============================================================================

class CountCalls:
    """Class-based decorator to count function calls"""
    def __init__(self, func: Callable):
        self.func = func
        self.count = 0
        functools.update_wrapper(self, func)
    
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"Call #{self.count} to {self.func.__name__}")
        return self.func(*args, **kwargs)


@CountCalls
def add(a: int, b: int) -> int:
    return a + b


# ============================================================================
# 7. VALIDATION DECORATOR
# ============================================================================

def validate_types(**type_checks):
    """Decorator that validates argument types"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function parameter names
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Check types
            for param_name, expected_type in type_checks.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not isinstance(value, expected_type):
                        raise TypeError(
                            f"{param_name} must be {expected_type.__name__}, "
                            f"got {type(value).__name__}"
                        )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


@validate_types(name=str, age=int)
def create_user(name: str, age: int) -> dict:
    return {"name": name, "age": age}


# ============================================================================
# INTERVIEW QUESTIONS
# ============================================================================

"""
Q1: What is a decorator? How do they work?
A: A decorator is a function that takes another function as input and 
   extends/modifies its behavior without permanently changing it. Uses 
   closures and functools.wraps to preserve metadata.

Q2: What's the difference between @decorator and @decorator()?
A: @decorator applies immediately (simple decorator), while @decorator() 
   returns a decorator factory that takes parameters (parameterized decorator).

Q3: Can you write a decorator that validates function arguments?
A: See validate_types() above - uses inspect module to bind arguments 
   and check types before execution.

Q4: Why use functools.wraps?
A: Preserves original function's __name__, __doc__, and __dict__, making 
   debugging easier and keeping metadata intact.

Q5: What's the time complexity of memoization?
A: First call: O(f(n)), subsequent calls: O(1) dictionary lookup. 
   Space complexity: O(n) for cache storage.

Q6: How would you debug a stacked decorator?
A: Apply decorators one at a time, test innermost first. Use 
   print statements or pdb. Remember execution order: bottom → top.

Q7: Write a thread-safe memoization decorator.
A: Use threading.Lock() to protect cache access in concurrent environments.
"""

if __name__ == "__main__":
    print("=" * 70)
    print("TESTING DECORATORS")
    print("=" * 70)
    
    # Test 1: Simple decorator
    print("\n1. SIMPLE DECORATOR:")
    result = greet("Alice")
    print(f"Result: {result}\n")
    
    # Test 2: Repeat decorator
    print("2. REPEAT DECORATOR:")
    times = get_current_time()
    print(f"Results: {times}\n")
    
    # Test 3: Timer decorator
    print("3. TIMER DECORATOR:")
    slow_function(1000000)
    print()
    
    # Test 4: Memoization
    print("4. MEMOIZATION DECORATOR:")
    print(f"fibonacci(5) = {fibonacci(5)}")
    print(f"Cache: {fibonacci.cache}\n")
    
    # Test 5: Stacked decorators
    print("5. STACKED DECORATORS:")
    print(format_message("test"))
    print()
    
    # Test 6: Class-based decorator
    print("6. CLASS-BASED DECORATOR:")
    print(f"add(2, 3) = {add(2, 3)}")
    print(f"add(5, 7) = {add(5, 7)}")
    print()
    
    # Test 7: Validation decorator
    print("7. VALIDATION DECORATOR:")
    try:
        user = create_user("Bob", 30)
        print(f"Created user: {user}")
        create_user("Charlie", "thirty")  # This will raise TypeError
    except TypeError as e:
        print(f"❌ Error: {e}")
