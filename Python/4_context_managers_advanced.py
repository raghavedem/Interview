"""
CONTEXT MANAGERS, ERROR HANDLING & ADVANCED CONCEPTS
Essential for: Resource management, exception handling, metaprogramming

Key Concepts:
- Context managers (with statement)
- __enter__ and __exit__
- Exception handling and custom exceptions
- Traceback inspection
- Metaclasses
- Descriptors
- Type hints and typing module
"""

from typing import Any, Type, Optional, List
from contextlib import contextmanager, ExitStack
import sys
import traceback
from pathlib import Path


# ============================================================================
# 1. CONTEXT MANAGERS (Resource Management)
# ============================================================================

class FileManager:
    """Basic context manager using __enter__ and __exit__"""
    
    def __init__(self, filename: str, mode: str = 'r'):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        """Called when entering 'with' block"""
        print(f"[ENTER] Opening {self.filename}")
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called when exiting 'with' block (even on exception)"""
        print(f"[EXIT] Closing {self.filename}")
        if self.file:
            self.file.close()
        
        # Return True to suppress exception, False/None to propagate
        if exc_type is not None:
            print(f"Exception occurred: {exc_type.__name__}: {exc_val}")
        return False


# ============================================================================
# 2. CONTEXT MANAGER WITH DECORATOR
# ============================================================================

@contextmanager
def managed_resource(name: str):
    """Use @contextmanager decorator for simpler context managers"""
    print(f"[ACQUIRE] {name}")
    try:
        yield name  # Value after 'as' in with statement
    finally:
        print(f"[RELEASE] {name}")


@contextmanager
def database_transaction(db_name: str = "mydb"):
    """Simulated database transaction context"""
    print(f"BEGIN TRANSACTION on {db_name}")
    try:
        yield f"Connection to {db_name}"
    except Exception as e:
        print(f"ROLLBACK due to {type(e).__name__}")
        raise
    else:
        print(f"COMMIT")


# ============================================================================
# 3. EXCEPTION HANDLING
# ============================================================================

class CustomException(Exception):
    """Custom exception with additional data"""
    def __init__(self, message: str, error_code: int):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
    
    def __str__(self):
        return f"[Error {self.error_code}] {self.message}"


class ValidationError(Exception):
    """Custom validation exception"""
    pass


class InsufficientFundsError(Exception):
    """Custom exception for banking domain"""
    def __init__(self, account_balance: float, requested: float):
        self.balance = account_balance
        self.requested = requested
        super().__init__(
            f"Insufficient funds. Balance: ${account_balance}, "
            f"Requested: ${requested}"
        )


def demonstrate_exception_hierarchy():
    """Show exception handling with multiple except clauses"""
    try:
        # Simulate different errors
        value = int("not_a_number")
    except ValueError as e:
        print(f"ValueError: {e}")
    except TypeError as e:
        print(f"TypeError: {e}")
    except Exception as e:
        print(f"Generic Exception: {e}")
    else:
        print("No exception occurred")
    finally:
        print("Cleanup code always runs")


def exception_with_context():
    """Chaining exceptions with 'raise from'"""
    try:
        result = 1 / 0
    except ZeroDivisionError as e:
        # Preserve original exception context
        raise CustomException("Failed calculation", 500) from e


def exception_information():
    """Access exception information during handling"""
    try:
        items = [1, 2, 3]
        items[10]  # IndexError
    except Exception as e:
        # Exception details
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(f"Type: {exc_type}")
        print(f"Value: {exc_value}")
        print(f"Traceback: {exc_traceback}")
        
        # Print full traceback
        traceback.print_exc()


# ============================================================================
# 4. EXCEPTION HANDLING WITH CONTEXT MANAGERS
# ============================================================================

@contextmanager
def error_handler(error_name: str):
    """Context manager for error handling"""
    try:
        yield
    except Exception as e:
        print(f"[{error_name}] Caught exception: {type(e).__name__}: {e}")
        # Optionally suppress or re-raise


class TransactionManager:
    """Context manager with rollback capability"""
    
    def __init__(self):
        self.committed = False
        self.data = {}
    
    def __enter__(self):
        print("Transaction started")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(f"Transaction failed: {exc_type.__name__}")
            self.rollback()
            return False  # Don't suppress exception
        else:
            self.commit()
            return True
    
    def set(self, key: str, value: Any):
        self.data[key] = value
    
    def commit(self):
        print(f"Committed changes: {self.data}")
        self.committed = True
    
    def rollback(self):
        print("Rolled back transaction")
        self.data = {}


# ============================================================================
# 5. METACLASSES (Advanced OOP)
# ============================================================================

class SingletonMeta(type):
    """Metaclass that creates singleton pattern"""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Logger(metaclass=SingletonMeta):
    """Uses SingletonMeta to ensure only one instance"""
    def __init__(self):
        self.logs = []
    
    def log(self, message: str):
        self.logs.append(message)
        print(f"LOG: {message}")


class ValidatingMeta(type):
    """Metaclass that validates class attributes on creation"""
    
    def __new__(mcs, name, bases, namespace):
        # Check that all methods have docstrings
        for key, value in namespace.items():
            if callable(value) and not key.startswith('_'):
                if not value.__doc__:
                    print(f"⚠️  {name}.{key} missing docstring")
        
        return super().__new__(mcs, name, bases, namespace)


class WellDocumentedClass(metaclass=ValidatingMeta):
    """Class checked by ValidatingMeta"""
    
    def method1(self):
        """This has a docstring"""
        pass
    
    def method2(self):
        # This is missing a docstring
        pass


# ============================================================================
# 6. DESCRIPTORS (Custom Attribute Access)
# ============================================================================

class Descriptor:
    """Base descriptor - intercepts attribute access"""
    
    def __get__(self, obj, objtype=None):
        """Called when attribute is accessed"""
        print(f"__get__ called: {obj}, {objtype}")
        return "descriptor value"
    
    def __set__(self, obj, value):
        """Called when attribute is assigned"""
        print(f"__set__ called: setting to {value}")
    
    def __delete__(self, obj):
        """Called when attribute is deleted"""
        print(f"__delete__ called")


class Validator:
    """Descriptor that validates values"""
    
    def __init__(self, name: str, expected_type: Type):
        self.name = name
        self.expected_type = expected_type
        self.data = {}
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return self.data.get(id(obj), None)
    
    def __set__(self, obj, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name} must be {self.expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
        self.data[id(obj)] = value
    
    def __delete__(self, obj):
        del self.data[id(obj)]


class Person:
    """Class using descriptors"""
    name = Validator("name", str)
    age = Validator("age", int)
    
    def __init__(self, name: str, age: int):
        self.name = name  # Triggers Validator.__set__
        self.age = age


# ============================================================================
# 7. TYPE HINTS (Type Annotations)
# ============================================================================

def calculate_average(numbers: List[int]) -> float:
    """Function with type hints"""
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)


class TypedClass:
    """Class with type annotations"""
    
    count: int = 0
    name: str
    items: List[str]
    config: dict[str, Any]  # Python 3.9+
    
    def __init__(self, name: str) -> None:
        self.name = name
        self.items = []
        TypedClass.count += 1
    
    def add_item(self, item: str) -> None:
        """Add item to list"""
        self.items.append(item)
    
    def get_info(self) -> dict[str, Any]:
        """Return information about instance"""
        return {"name": self.name, "item_count": len(self.items)}


# ============================================================================
# 8. EXIT STACK (Multiple Context Managers)
# ============================================================================

def process_multiple_files(file_paths: List[str]):
    """Use ExitStack to manage multiple context managers"""
    with ExitStack() as stack:
        files = []
        for filepath in file_paths:
            # Each file will be closed automatically
            f = stack.enter_context(open(filepath, 'r'))
            files.append(f)
        
        # Process all files
        for f in files:
            print(f"Processing: {f.name}")


# ============================================================================
# INTERVIEW QUESTIONS
# ============================================================================

"""
Q1: What is a context manager and why would you use it?
A: Context managers (with statement) ensure resources are properly acquired
   and released. Implement __enter__ (setup) and __exit__ (cleanup). Use for
   file I/O, database connections, locks, etc.

Q2: How does the 'with' statement work?
A: Calls __enter__() on entering block, __exit__() on exiting (even on 
   exception). __exit__ receives exception info. Return True to suppress.

Q3: What's the difference between contextmanager and custom class?
A: @contextmanager decorator simplifies creating context managers. Decorator
   wraps generator, yield is __enter__, code after is __exit__.

Q4: How would you handle multiple exceptions differently?
A: Use multiple except clauses in order (most specific first). Check 
   exception type with isinstance(). Use 'raise from' to chain exceptions.

Q5: What's the purpose of __exit__ returning True/False?
A: Return True to suppress exception. Return False/None to propagate it.
   Useful when context manager handles known exceptions.

Q6: What are custom exceptions useful for?
A: Domain-specific exceptions make code clearer and enable precise error
   handling. Include relevant data (__init__ parameters). Good for API design.

Q7: What's a metaclass and when would you use it?
A: Metaclass is a "class of a class" (controls class creation). Use for:
   - Singletons, Borg pattern
   - Enforcing class structure
   - Auto-registering subclasses
   - Advanced metaprogramming

Q8: How do you create a class with a metaclass?
A: Use 'class ClassName(metaclass=MetaclassName):'. Metaclass.__new__ is
   called to create class. Can validate/modify namespace.

Q9: What are descriptors and what problem do they solve?
A: Descriptors control attribute access via __get__, __set__, __delete__.
   Used for: validation, computed properties, lazy loading, caching.

Q10: What's the difference between @property and a descriptor?
A: @property is a descriptor for simple cases. Descriptors are more powerful,
    can be shared across classes, better for complex access patterns.

Q11: Why use type hints?
A: Improve code documentation, enable IDE autocomplete, catch errors early
    with mypy/static analysis, make refactoring safer.

Q12: What's ExitStack used for?
A: Manages variable number of context managers. Push/pop contexts dynamically.
    Useful for unknown number of resources to manage.
"""

if __name__ == "__main__":
    print("=" * 70)
    print("CONTEXT MANAGERS, ERROR HANDLING & ADVANCED CONCEPTS")
    print("=" * 70)
    
    # Test 1: Context manager
    print("\n1. CONTEXT MANAGER:")
    test_file = Path("/tmp/test_context.txt")
    test_file.write_text("Hello, World!")
    with FileManager(str(test_file), 'r') as f:
        content = f.read()
        print(f"  File content: {content}")
    
    # Test 2: Decorator-based context manager
    print("\n2. @contextmanager DECORATOR:")
    with managed_resource("Database Connection") as res:
        print(f"  Using: {res}")
    
    # Test 3: Database transaction
    print("\n3. DATABASE TRANSACTION:")
    try:
        with database_transaction("orders"):
            print("  Executing SQL queries...")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test 4: Exception hierarchy
    print("\n4. EXCEPTION HANDLING:")
    demonstrate_exception_hierarchy()
    
    # Test 5: Custom exception
    print("\n5. CUSTOM EXCEPTION:")
    try:
        raise CustomException("Payment failed", 402)
    except CustomException as e:
        print(f"  Caught: {e}")
    
    # Test 6: Transaction manager
    print("\n6. TRANSACTION MANAGER:")
    tm = TransactionManager()
    try:
        with tm as trans:
            trans.set("user_id", 123)
            trans.set("amount", 99.99)
            print(f"  Data in transaction: {trans.data}")
    except Exception as e:
        print(f"  Exception: {e}")
    
    # Test 7: Singleton metaclass
    print("\n7. SINGLETON METACLASS:")
    logger1 = Logger()
    logger1.log("First message")
    logger2 = Logger()
    logger2.log("Second message")
    print(f"  Same instance: {logger1 is logger2}")
    print(f"  All logs: {logger1.logs}")
    
    # Test 8: Descriptors
    print("\n8. DESCRIPTORS:")
    try:
        person = Person("Alice", 30)
        print(f"  Created: {person.name}, age {person.age}")
        person.age = "thirty"  # This will raise TypeError
    except TypeError as e:
        print(f"  Descriptor validation: {e}")
    
    # Test 9: Type hints
    print("\n9. TYPE HINTS:")
    avg = calculate_average([10, 20, 30, 40])
    print(f"  Average: {avg}")
    
    obj = TypedClass("Python Developer")
    obj.add_item("Decorators")
    obj.add_item("Context Managers")
    print(f"  Info: {obj.get_info()}")
    
    # Cleanup
    test_file.unlink()
