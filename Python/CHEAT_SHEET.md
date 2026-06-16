# Python Interview Cheat Sheet
## Quick Reference for 3-5 Years Experience Level

---

## 1️⃣ DECORATORS

### Basic Pattern
```python
def decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Before
        result = func(*args, **kwargs)
        # After
        return result
    return wrapper

@decorator
def func(): pass
```

### With Arguments
```python
def decorator(param):
    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Use param
            return func(*args, **kwargs)
        return wrapper
    return actual_decorator

@decorator(param="value")
def func(): pass
```

### Common Decorators
```python
@functools.wraps(func)        # Preserve metadata
@property                      # Create property
@classmethod                   # Class method
@staticmethod                  # Static method
@abstractmethod                # Abstract method
@lru_cache                     # Memoization
```

---

## 2️⃣ OOP FUNDAMENTALS

### Class Structure
```python
class Parent:
    class_var = 0  # Shared
    
    def __init__(self, value):
        self.instance_var = value  # Per instance
    
    def __str__(self): return "user friendly"
    def __repr__(self): return "developer friendly"
    def __eq__(self, other): return ...

class Child(Parent):
    def __init__(self, value, extra):
        super().__init__(value)
        self.extra = extra
```

### Special Methods
```python
__init__(self)           # Constructor
__new__(cls)             # Create instance (rarely used)
__str__(self)            # str() - user friendly
__repr__(self)           # repr() - debug friendly
__eq__(self, other)      # ==
__lt__(self, other)      # <
__len__(self)            # len()
__getitem__(self, key)   # []
__setitem__(self, k, v)  # []
__delitem__(self, key)   # del
```

### Properties
```python
class Temp:
    def __init__(self, c):
        self._celsius = c
    
    @property
    def celsius(self):
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("Too cold")
        self._celsius = value
    
    @property
    def fahrenheit(self):
        return self._celsius * 9/5 + 32
    
    @fahrenheit.setter
    def fahrenheit(self, f):
        self._celsius = (f - 32) * 5/9
```

### Encapsulation
```python
class Account:
    def __init__(self):
        self.public = 1           # Public
        self._protected = 2       # Protected (convention)
        self.__private = 3        # Private (name mangling)
    
    # Access private: obj._Account__private
```

### Inheritance & MRO
```python
class A: pass
class B(A): pass
class C(A): pass
class D(B, C): pass

print(D.__mro__)  # D → B → C → A → object
print(D.mro())    # Same

# Call parent
super().__init__()
super().method()
```

---

## 3️⃣ ABSTRACT CLASSES

```python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def make_sound(self): pass
    
    def describe(self):  # Concrete method
        return f"I'm a {self.__class__.__name__}"

class Dog(Animal):
    def make_sound(self):  # Must implement
        return "Woof"

# Cannot instantiate: Animal()  # TypeError
dog = Dog()  # Works
```

---

## 4️⃣ DESIGN PATTERNS

### Factory Pattern
```python
class PaymentFactory:
    @staticmethod
    def create(type_name):
        if type_name == "card":
            return CardPayment()
        elif type_name == "paypal":
            return PayPalPayment()
        raise ValueError(f"Unknown: {type_name}")

payment = PaymentFactory.create("card")
```

### Singleton Pattern
```python
class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    pass

db1 = Database()
db2 = Database()
assert db1 is db2  # True - same instance
```

### Strategy Pattern
```python
class Strategy(ABC):
    @abstractmethod
    def execute(self): pass

class ConcreteStrategy(Strategy):
    def execute(self):
        return "result"

class Context:
    def __init__(self, strategy):
        self.strategy = strategy
    
    def perform(self):
        return self.strategy.execute()
```

---

## 5️⃣ GENERATORS & ITERATORS

### Iterator
```python
class Counter:
    def __init__(self, max):
        self.current = 0
        self.max = max
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current < self.max:
            self.current += 1
            return self.current
        raise StopIteration

for num in Counter(3):
    print(num)  # 1, 2, 3
```

### Generator
```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1

for num in countdown(3):
    print(num)  # 3, 2, 1

# Generator expression
squares = (x**2 for x in range(10))  # Lazy
list_squares = [x**2 for x in range(10)]  # Eager
```

### Functional Operations
```python
# Map - apply function
result = map(lambda x: x*2, [1,2,3])  # [2,4,6]

# Filter - keep True
result = filter(lambda x: x%2==0, [1,2,3,4])  # [2,4]

# Reduce - accumulate
from functools import reduce
result = reduce(lambda x,y: x+y, [1,2,3,4])  # 10
```

### Comprehensions
```python
# List comprehension
squares = [x**2 for x in range(10) if x % 2 == 0]

# Dict comprehension
mapping = {x: x**2 for x in range(5)}

# Set comprehension
unique = {x % 3 for x in range(10)}

# Nested
matrix = [[j for j in range(3)] for i in range(3)]
```

### Closures & Nonlocal
```python
def make_counter():
    count = 0
    
    def increment():
        nonlocal count  # Modify outer variable
        count += 1
        return count
    
    return increment

counter = make_counter()
print(counter())  # 1
print(counter())  # 2
```

---

## 6️⃣ CONTEXT MANAGERS

### Class-Based
```python
class Manager:
    def __enter__(self):
        print("Setup")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Cleanup")
        return False  # Don't suppress exceptions

with Manager() as m:
    print("Inside")
# Output: Setup, Inside, Cleanup
```

### Decorator-Based
```python
from contextlib import contextmanager

@contextmanager
def managed(name):
    print(f"Enter {name}")
    try:
        yield name
    finally:
        print(f"Exit {name}")

with managed("resource") as r:
    print(f"Using {r}")
```

---

## 7️⃣ EXCEPTION HANDLING

```python
try:
    # Code
    risky_operation()
except ValueError as e:
    # Specific exception
    print(f"Value error: {e}")
except (TypeError, KeyError) as e:
    # Multiple exceptions
    print(f"Type or Key error: {e}")
except Exception as e:
    # Catch all (but avoid!)
    print(f"Unexpected: {e}")
else:
    # Runs if no exception
    print("Success!")
finally:
    # Always runs
    print("Cleanup")
```

### Custom Exceptions
```python
class CustomError(Exception):
    def __init__(self, message, code):
        self.message = message
        self.code = code
        super().__init__(self.message)

raise CustomError("Something failed", 500)

# Chaining exceptions
try:
    risky()
except Error as e:
    raise CustomError("Failed") from e  # Preserve traceback
```

---

## 8️⃣ TYPE HINTS

```python
from typing import List, Dict, Optional, Union, Tuple, Callable

def process(
    items: List[int],
    mapping: Dict[str, int],
    optional: Optional[str] = None,
    either: Union[int, str] = 0,
    func: Callable[[int], str] = str
) -> Tuple[bool, str]:
    """Function with type hints"""
    return (True, "result")

# Variables
count: int = 0
items: List[str] = []
mapping: Dict[str, int] = {}
```

---

## 9️⃣ LAMBDA FUNCTIONS

```python
# Simple
add = lambda x, y: x + y
add(2, 3)  # 5

# With sorted
people = [{"age": 30}, {"age": 25}]
sorted(people, key=lambda p: p["age"])

# With map/filter
nums = [1, 2, 3, 4, 5]
doubled = list(map(lambda x: x*2, nums))
evens = list(filter(lambda x: x%2==0, nums))
```

---

## 🔟 METACLASSES

```python
class Meta(type):
    def __new__(mcs, name, bases, namespace):
        # Modify class creation
        return super().__new__(mcs, name, bases, namespace)

class MyClass(metaclass=Meta):
    pass

# Use cases:
# - Singleton
# - Register subclasses
# - Auto-generate methods
# - Enforce structure
```

---

## 1️⃣1️⃣ DESCRIPTORS

```python
class Descriptor:
    def __get__(self, obj, objtype=None):
        print("Getting")
        return "value"
    
    def __set__(self, obj, value):
        print(f"Setting to {value}")
    
    def __delete__(self, obj):
        print("Deleting")

class MyClass:
    attr = Descriptor()

obj = MyClass()
obj.attr          # Calls __get__
obj.attr = 5      # Calls __set__
del obj.attr      # Calls __delete__
```

---

## 🎯 KEY TAKEAWAYS

### Decorators
- ✅ Use `functools.wraps` to preserve metadata
- ✅ Can stack multiple decorators
- ✅ Understand execution order (bottom-to-top)

### OOP
- ✅ Use `super()` for inheritance
- ✅ Know MRO for multiple inheritance
- ✅ Composition > Inheritance when possible
- ✅ Use `@property` for controlled access

### Generators
- ✅ Memory efficient: O(1) vs O(n)
- ✅ Lazy evaluation (compute on demand)
- ✅ Chain for data processing pipelines

### Context Managers
- ✅ Ensure cleanup via `__exit__`
- ✅ Use `@contextmanager` for simplicity
- ✅ Perfect for resource management

### Exception Handling
- ✅ Catch specific exceptions first
- ✅ Use `raise from` to chain exceptions
- ✅ Don't catch bare `Exception` (too broad)

### Design Patterns
- ✅ Factory: Create objects polymorphically
- ✅ Singleton: Ensure one instance
- ✅ Strategy: Swap algorithms
- ✅ Observer: Publish-subscribe

---

## 📊 COMPLEXITY CHEAT SHEET

| Operation | Time | Space | Notes |
|-----------|------|-------|-------|
| List lookup | O(1) | O(n) | By index |
| List insert | O(n) | O(n) | May require resize |
| List search | O(n) | O(1) | Linear search |
| Dict lookup | O(1) | O(n) | Average case |
| Set search | O(1) | O(n) | Average case |
| Generator | O(1)* | O(1) | Per item |
| Decorator | O(1) | O(1) | Per call |
| Recursion | O(n) | O(n) | Call stack |
| Memoization | O(1)** | O(n) | Cache hit |

*: Per item generated
**: After first call

---

## 🚀 INTERVIEW TIPS

### What to Emphasize
1. **Why** not just how
2. Trade-offs (time vs space, simplicity vs power)
3. Real-world use cases
4. Edge cases and error handling
5. Testing strategy

### What to Avoid
- ❌ Vague explanations
- ❌ Jargon without explanation
- ❌ Ignoring edge cases
- ❌ Overthinking simple problems
- ❌ Not asking clarifying questions

### Example Answer Structure
1. **Clarify** - "Do you mean...?"
2. **Explain** - Simple language
3. **Example** - Show code
4. **Trade-offs** - When/why to use
5. **Alternatives** - Other approaches

---

## 📚 QUICK STUDY ROADMAP

**Day 1**: Decorators + OOP (files 1-2)
**Day 2**: Generators + Functional (file 3)
**Day 3**: Context Managers + Advanced (file 4)
**Day 4**: Review Q&A (file 5)
**Day 5**: Coding Challenges (file 6)
**Day 6**: Practice problems + weak areas
**Day 7**: Mock interviews

---

## ✨ REMEMBER

> "It's not about memorizing answers, it's about understanding concepts 
> and being able to apply them in new situations."

Good luck with your interviews! 🎯

---

*Last Updated: 2024*
*For Python 3.8+*
*Created for 3-5 Years Experience Level*
