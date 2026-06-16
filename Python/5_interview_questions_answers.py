"""
COMPREHENSIVE PYTHON INTERVIEW QUESTIONS & ANSWERS
For 3-5 Years Experience Level

This document contains questions extracted from the project code
organized by topic with detailed explanations and follow-up questions.
"""

# ============================================================================
# SECTION 1: DECORATORS & HIGHER-ORDER FUNCTIONS
# ============================================================================

DECORATORS_QA = """
┌─────────────────────────────────────────────────────────────────────────┐
│ DECORATORS & HIGHER-ORDER FUNCTIONS                                     │
└─────────────────────────────────────────────────────────────────────────┘

Q1: What is a decorator and how do they work?
────────────────────────────────────────────────────────────────────────────
A: A decorator is a function that takes another function as input and 
   extends/modifies its behavior without permanently changing it.
   
   How it works:
   - Takes a function as argument
   - Returns a wrapper function
   - Wrapper function can execute code before/after original function
   - Uses closures to maintain access to original function
   
   Example:
   ```python
   def my_decorator(func):
       def wrapper(*args, **kwargs):
           print("Before")
           result = func(*args, **kwargs)
           print("After")
           return result
       return wrapper
   
   @my_decorator
   def greet(name):
       return f"Hello, {name}"
   ```

F1: Why use functools.wraps?
A1: functools.wraps preserves original function's metadata:
    - __name__: Function name
    - __doc__: Docstring
    - __dict__: Attributes
    
    Without it, decorated function loses identity, breaking introspection.

F2: Can you apply multiple decorators?
A2: Yes! Stacked decorators execute bottom-to-top (closest to function first).
    
    ```python
    @decorator1
    @decorator2
    @decorator3
    def func():
        pass
    
    # Execution order: decorator3 → decorator2 → decorator1 → func
    ```

────────────────────────────────────────────────────────────────────────────

Q2: What's the difference between @decorator and @decorator()?
────────────────────────────────────────────────────────────────────────────
A: @decorator is a simple decorator (no arguments).
   @decorator() is a decorator factory (with arguments).
   
   Simple decorator:
   ```python
   @my_decorator
   def func(): pass
   # Direct wrapping
   ```
   
   Decorator with arguments:
   ```python
   @my_decorator(param1, param2)
   def func(): pass
   
   # my_decorator(param1, param2) returns decorator function
   # That decorator is then applied to func
   ```

F1: Can you modify both patterns in the same decorator?
A1: Yes, make it flexible:
    ```python
    def decorator(_func=None, *, param=None):
        def actual_decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Use param if provided
                return func(*args, **kwargs)
            return wrapper
        
        if _func is None:
            # Called with arguments
            return actual_decorator
        else:
            # Called without arguments
            return actual_decorator(_func)
    ```

────────────────────────────────────────────────────────────────────────────

Q3: Write a decorator that validates function arguments
────────────────────────────────────────────────────────────────────────────
A: Use inspect module to get function signature:
   
   ```python
   import inspect
   from functools import wraps
   
   def validate_types(**type_checks):
       def decorator(func):
           @wraps(func)
           def wrapper(*args, **kwargs):
               sig = inspect.signature(func)
               bound = sig.bind(*args, **kwargs)
               bound.apply_defaults()
               
               for param_name, expected_type in type_checks.items():
                   value = bound.arguments.get(param_name)
                   if value and not isinstance(value, expected_type):
                       raise TypeError(f"{param_name} must be {expected_type}")
               
               return func(*args, **kwargs)
           return wrapper
       return decorator
   
   @validate_types(name=str, age=int)
   def create_user(name, age):
       return {"name": name, "age": age}
   ```

────────────────────────────────────────────────────────────────────────────

Q4: How would you implement a thread-safe memoization decorator?
────────────────────────────────────────────────────────────────────────────
A: Use threading.Lock to protect cache access:
   
   ```python
   import threading
   from functools import wraps
   
   def thread_safe_memoize(func):
       cache = {}
       lock = threading.Lock()
       
       @wraps(func)
       def wrapper(*args, **kwargs):
           key = (args, tuple(sorted(kwargs.items())))
           
           with lock:  # Acquire lock for thread-safe access
               if key not in cache:
                   cache[key] = func(*args, **kwargs)
               return cache[key]
       
       return wrapper
   ```
   
   Critical: Lock prevents race conditions when multiple threads access cache.

────────────────────────────────────────────────────────────────────────────

Q5: What's the time complexity of a memoization decorator?
────────────────────────────────────────────────────────────────────────────
A: First call to function with args: O(f(n)) where f is original function
   Subsequent calls with same args: O(1) dictionary lookup
   Space complexity: O(n) for cache storage (n = number of unique arg combinations)

F1: What's a limitation of memoization?
A1: If function depends on external state or time, cached results may be stale.
    Not suitable for functions with side effects.

────────────────────────────────────────────────────────────────────────────

Q6: Write a decorator that measures function execution time
────────────────────────────────────────────────────────────────────────────
A: ```python
   import time
   from functools import wraps
   
   def timer(func):
       @wraps(func)
       def wrapper(*args, **kwargs):
           start = time.perf_counter()  # Use perf_counter for precision
           result = func(*args, **kwargs)
           elapsed = time.perf_counter() - start
           print(f"{func.__name__} took {elapsed:.4f} seconds")
           return result
       return wrapper
   ```
   
   Note: Use time.perf_counter() for better precision than time.time()

"""

# ============================================================================
# SECTION 2: OBJECT-ORIENTED PROGRAMMING
# ============================================================================

OOP_QA = """
┌─────────────────────────────────────────────────────────────────────────┐
│ OBJECT-ORIENTED PROGRAMMING & DESIGN PATTERNS                           │
└─────────────────────────────────────────────────────────────────────────┘

Q1: What's the difference between __init__ and __new__?
────────────────────────────────────────────────────────────────────────────
A: __new__: Creates instance (called first)
   __init__: Initializes instance (called second)
   
   ```python
   class Example:
       def __new__(cls, *args, **kwargs):
           print("Creating instance")
           return super().__new__(cls)
       
       def __init__(self, value):
           print("Initializing instance")
           self.value = value
   ```
   
   __new__ is rarely overridden. Common use case: Singleton pattern, 
   immutable objects (str, int), returning different type.

────────────────────────────────────────────────────────────────────────────

Q2: Explain Method Resolution Order (MRO) in Python
────────────────────────────────────────────────────────────────────────────
A: MRO is the order in which Python looks for methods/attributes in multiple
   inheritance. Uses C3 linearization algorithm.
   
   Rules:
   - Left-to-right: Base classes listed left come before right
   - Depth-first: Parent before grandparent
   - Preserve order from parents
   
   Example:
   ```python
   class A: pass
   class B(A): pass
   class C(A): pass
   class D(B, C): pass
   
   # MRO: D → B → C → A → object
   print(D.__mro__)
   # or use help(D) to see MRO
   ```
   
   Critical for multiple inheritance: always respect MRO for correct behavior.

────────────────────────────────────────────────────────────────────────────

Q3: What's the difference between class variables and instance variables?
────────────────────────────────────────────────────────────────────────────
A: Class variables: Shared across all instances
   Instance variables: Unique to each object
   
   ```python
   class Counter:
       count = 0  # Class variable
       
       def __init__(self, name):
           self.name = name  # Instance variable
           Counter.count += 1
   
   c1 = Counter("A")
   c2 = Counter("B")
   print(Counter.count)  # 2 (shared)
   print(c1.name)  # "A" (unique)
   print(c2.name)  # "B" (unique)
   ```
   
   Gotcha: Modifying mutable class variable affects all instances!
   ```python
   class Team:
       members = []  # Shared list (dangerous!)
   
   t1, t2 = Team(), Team()
   t1.members.append("Alice")
   print(t2.members)  # ["Alice"] - shared!
   ```

────────────────────────────────────────────────────────────────────────────

Q4: How does name mangling work with __ prefix?
────────────────────────────────────────────────────────────────────────────
A: Python translates __attribute to _ClassName__attribute to discourage 
   external access, but it's not true privacy.
   
   ```python
   class Account:
       def __init__(self):
           self.__balance = 0  # Private (by convention)
   
   acc = Account()
   # acc.__balance  # AttributeError
   # acc._Account__balance  # Works! (name mangling)
   ```
   
   Name mangling:
   - Only applies to double underscore (__)
   - Applied to attributes AND methods
   - Not a security feature, just discouragement
   - Use _single_underscore for protected members

────────────────────────────────────────────────────────────────────────────

Q5: When should you use composition over inheritance?
────────────────────────────────────────────────────────────────────────────
A: Use composition (has-a) for flexibility and reusability.
   Use inheritance (is-a) for true hierarchical relationships.
   
   Inheritance example (appropriate):
   ```python
   class Animal:
       def move(self): pass
   
   class Dog(Animal):  # IS-A relationship
       def move(self):
           return "Running on four legs"
   ```
   
   Composition example (more flexible):
   ```python
   class Engine:
       def start(self): pass
   
   class Car:
       def __init__(self):
           self.engine = Engine()  # HAS-A relationship
   ```
   
   Advantages of composition:
   - More flexible (swap components)
   - Easier testing (inject dependencies)
   - Avoids fragile base class problem
   - Follows "favor composition over inheritance"

────────────────────────────────────────────────────────────────────────────

Q6: Explain the Factory Pattern
────────────────────────────────────────────────────────────────────────────
A: Factory pattern creates objects without specifying exact classes.
   
   Benefits:
   - Decouples object creation from usage
   - Centralizes creation logic
   - Easy to add new types
   
   ```python
   class PaymentFactory:
       @staticmethod
       def create(payment_type, amount):
           if payment_type == "card":
               return CardPayment(amount)
           elif payment_type == "paypal":
               return PayPalPayment(amount)
           else:
               raise ValueError(f"Unknown type: {payment_type}")
   
   # Usage
   payment = PaymentFactory.create("card", 99.99)
   payment.process()
   ```
   
   When to use: Different implementations, plugin systems, configuration-driven creation

────────────────────────────────────────────────────────────────────────────

Q7: How would you implement a Singleton in Python?
────────────────────────────────────────────────────────────────────────────
A: Use metaclass (most reliable):
   
   ```python
   class SingletonMeta(type):
       _instances = {}
       
       def __call__(cls, *args, **kwargs):
           if cls not in cls._instances:
               cls._instances[cls] = super().__call__(*args, **kwargs)
           return cls._instances[cls]
   
   class Database(metaclass=SingletonMeta):
       def __init__(self):
           self.connection = None
   
   db1 = Database()
   db2 = Database()
   assert db1 is db2  # Same instance
   ```
   
   Alternative: Module-level singleton (Pythonic)
   ```python
   # database.py
   class _Database:
       def __init__(self):
           self.connection = None
   
   database = _Database()  # Single instance
   
   # usage.py
   from database import database
   ```

────────────────────────────────────────────────────────────────────────────

Q8: What's the Strategy Pattern and when to use it?
────────────────────────────────────────────────────────────────────────────
A: Strategy pattern encapsulates interchangeable algorithms.
   
   ```python
   from abc import ABC, abstractmethod
   
   class PaymentStrategy(ABC):
       @abstractmethod
       def pay(self, amount): pass
   
   class CreditCard(PaymentStrategy):
       def pay(self, amount):
           return f"Paid ${amount} with credit card"
   
   class PaymentProcessor:
       def __init__(self, strategy: PaymentStrategy):
           self.strategy = strategy
       
       def process_payment(self, amount):
           return self.strategy.pay(amount)
   
   # Usage
   processor = PaymentProcessor(CreditCard())
   processor.process_payment(100)
   
   # Easy to switch strategy
   processor.strategy = PayPal()
   processor.process_payment(100)
   ```
   
   Use when: Multiple algorithms for same task, algorithm selection at runtime

────────────────────────────────────────────────────────────────────────────

Q9: What are abstract base classes and how do you use them?
────────────────────────────────────────────────────────────────────────────
A: Abstract base classes define interface that subclasses must implement.
   Cannot instantiate abstract class directly.
   
   ```python
   from abc import ABC, abstractmethod
   
   class Shape(ABC):
       @abstractmethod
       def area(self): pass
       
       @abstractmethod
       def perimeter(self): pass
       
       def describe(self):  # Concrete method
           return f"I'm a {self.__class__.__name__}"
   
   class Circle(Shape):
       def __init__(self, radius):
           self.radius = radius
       
       def area(self):  # Must implement
           return 3.14 * self.radius ** 2
       
       def perimeter(self):  # Must implement
           return 2 * 3.14 * self.radius
   
   # Shape()  # TypeError: Can't instantiate abstract class
   circle = Circle(5)  # Works
   ```
   
   Benefits:
   - Define contracts/interfaces
   - Enforce implementation in subclasses
   - Enable polymorphism

────────────────────────────────────────────────────────────────────────────

Q10: How do @property decorators work?
────────────────────────────────────────────────────────────────────────────
A: @property allows accessing methods like attributes, with validation.
   
   ```python
   class Temperature:
       def __init__(self, celsius):
           self._celsius = celsius
       
       @property
       def celsius(self):  # Getter
           return self._celsius
       
       @celsius.setter
       def celsius(self, value):  # Setter
           if value < -273.15:
               raise ValueError("Below absolute zero")
           self._celsius = value
       
       @property
       def fahrenheit(self):  # Computed property
           return self._celsius * 9/5 + 32
   
   temp = Temperature(25)
   print(temp.celsius)  # 25 (calls getter)
   temp.celsius = 30    # Calls setter with validation
   ```
   
   Benefits:
   - Encapsulation with attribute-like syntax
   - Add validation without changing API
   - Computed values (fahrenheit from celsius)

"""

# ============================================================================
# SECTION 3: GENERATORS & FUNCTIONAL PROGRAMMING
# ============================================================================

GENERATORS_QA = """
┌─────────────────────────────────────────────────────────────────────────┐
│ GENERATORS, ITERATORS & FUNCTIONAL PROGRAMMING                          │
└─────────────────────────────────────────────────────────────────────────┘

Q1: What's the difference between an iterable and an iterator?
────────────────────────────────────────────────────────────────────────────
A: Iterable: Object with __iter__() method that returns an iterator
   Iterator: Object with __next__() method that returns next value
   
   ```python
   # Iterable
   my_list = [1, 2, 3]  # Has __iter__
   iterator = iter(my_list)  # Returns iterator
   
   # Iterator
   print(next(iterator))  # Calls __next__, returns 1
   print(next(iterator))  # Returns 2
   print(next(iterator))  # Returns 3
   # next(iterator)  # Raises StopIteration
   ```
   
   All iterators are iterable (have __iter__), but not all iterables are iterators.

F1: Can you write a custom iterator?
A1: ```python
    class CountUp:
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
    
    for num in CountUp(3):
        print(num)  # 1, 2, 3
    ```

────────────────────────────────────────────────────────────────────────────

Q2: What are generators and how are they different from regular functions?
────────────────────────────────────────────────────────────────────────────
A: Generators use 'yield' to produce sequence without storing all values.
   
   Regular function vs Generator:
   ```python
   # Regular function - returns all at once
   def get_numbers(n):
       result = []
       for i in range(n):
           result.append(i)
       return result  # 1 return, entire list
   
   # Generator - yields one at a time
   def gen_numbers(n):
       for i in range(n):
           yield i  # Multiple yields
   
   # Usage difference
   nums = get_numbers(5)  # Returns [0,1,2,3,4] immediately
   gen = gen_numbers(5)   # Returns generator object (nothing computed yet)
   next(gen)  # 0 (computed on demand)
   ```
   
   Benefits:
   - Lazy evaluation (compute on demand)
   - Memory efficient (only current value in memory)
   - Can represent infinite sequences

F1: What's the advantage of generators over lists?
A1: ```python
    # List: loads entire sequence in memory
    squares = [x**2 for x in range(1000000)]  # Uses lots of RAM
    
    # Generator: computes values as needed
    squares_gen = (x**2 for x in range(1000000))  # Minimal RAM
    
    # With generator, memory usage is constant regardless of range
    ```

────────────────────────────────────────────────────────────────────────────

Q3: Explain "yield" vs "return"
────────────────────────────────────────────────────────────────────────────
A: return: Ends function, returns value
   yield: Pauses function, returns value, resumes on next call
   
   ```python
   def demo_return():
       return 1
       return 2  # Never reached
   
   def demo_yield():
       yield 1
       yield 2  # Reached on next call
   
   r = demo_return()
   print(r)  # 1
   
   g = demo_yield()
   print(next(g))  # 1
   print(next(g))  # 2
   ```
   
   Yield allows stateful generators:
   ```python
   def fibonacci():
       a, b = 0, 1
       while True:
           yield a
           a, b = b, a + b
   
   fib = fibonacci()
   for _ in range(5):
       print(next(fib))  # 0, 1, 1, 2, 3
   ```

────────────────────────────────────────────────────────────────────────────

Q4: How do you pass values into a generator?
────────────────────────────────────────────────────────────────────────────
A: Use generator.send(value). Generator receives value from yield expression.
   
   ```python
   def echo_generator():
       print("Started")
       while True:
           received = yield  # Receives value via send()
           if received is None:
               print("No value")
           else:
               print(f"Received: {received}, squared: {received**2}")
   
   gen = echo_generator()
   next(gen)  # Start generator, reaches first yield
   gen.send("test")  # Send value
   gen.send(5)  # Send number
   ```
   
   Critical: Must call next() or send(None) first to start generator!

────────────────────────────────────────────────────────────────────────────

Q5: What's a list comprehension vs generator expression?
────────────────────────────────────────────────────────────────────────────
A: List comprehension: Creates entire list in memory
   Generator expression: Creates generator (lazy evaluation)
   
   Syntax:
   ```python
   list_comp = [x*2 for x in range(1000)]      # List (all in memory)
   gen_exp = (x*2 for x in range(1000))        # Generator (lazy)
   
   # Memory usage
   import sys
   print(sys.getsizeof(list_comp))  # Much larger
   print(sys.getsizeof(gen_exp))    # Tiny
   ```
   
   When to use:
   - List comprehension: Small/medium data, need multiple iterations
   - Generator expression: Large data, single pass, memory limited

────────────────────────────────────────────────────────────────────────────

Q6: Explain map(), filter(), and reduce()
────────────────────────────────────────────────────────────────────────────
A: map(): Apply function to all items
   filter(): Keep items where function is True
   reduce(): Accumulate values left-to-right
   
   ```python
   numbers = [1, 2, 3, 4, 5]
   
   # map: apply function
   squared = map(lambda x: x**2, numbers)  # [1, 4, 9, 16, 25]
   
   # filter: keep if True
   evens = filter(lambda x: x % 2 == 0, numbers)  # [2, 4]
   
   # reduce: accumulate
   from functools import reduce
   total = reduce(lambda x, y: x + y, numbers)  # 15
   product = reduce(lambda x, y: x * y, numbers)  # 120
   ```
   
   Note: All return iterators (lazy), convert to list if needed.

────────────────────────────────────────────────────────────────────────────

Q7: When should you use lambda functions?
────────────────────────────────────────────────────────────────────────────
A: Use lambda for simple, one-time-use functions.
   Avoid lambda for complex logic (bad readability).
   
   Good use cases:
   ```python
   # Sorting by custom key
   people = [{"name": "Bob", "age": 30}, {"name": "Alice", "age": 25}]
   sorted_by_age = sorted(people, key=lambda p: p["age"])
   
   # With map/filter
   nums = [1, 2, 3, 4, 5]
   doubled = list(map(lambda x: x*2, nums))
   evens = list(filter(lambda x: x%2==0, nums))
   ```
   
   Bad use cases (use named function instead):
   ```python
   # Complex logic - should be named function
   process = lambda x: (x*2 + 5) / 3 if x > 0 else -(x*2 + 5) / 3
   
   # Multiple statements - lambda can't handle
   # calculate = lambda x: (x += 5; return x)  # Syntax error
   ```

────────────────────────────────────────────────────────────────────────────

Q8: What is a closure?
────────────────────────────────────────────────────────────────────────────
A: Closure is a function that "remembers" variables from outer scope.
   
   ```python
   def make_multiplier(n):
       def multiplier(x):
           return x * n  # Remembers 'n' from outer scope
       return multiplier
   
   triple = make_multiplier(3)
   print(triple(5))  # 15 - uses remembered n=3
   print(triple(10))  # 30
   
   # Another example: Counter
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
   print(counter())  # 3
   ```
   
   Critical: Use 'nonlocal' to modify outer variables!

────────────────────────────────────────────────────────────────────────────

Q9: How do you implement a generator pipeline?
────────────────────────────────────────────────────────────────────────────
A: Chain generators for efficient data processing:
   
   ```python
   # Pipeline: Filter → Map → Process
   def numbers():
       for i in range(1, 11):
           yield i
   
   def filter_even(nums):
       for n in nums:
           if n % 2 == 0:
               yield n
   
   def double(nums):
       for n in nums:
           yield n * 2
   
   # Chain them
   pipeline = double(filter_even(numbers()))
   for result in pipeline:
       print(result)  # 4, 8, 12, 16, 20
   
   # Or using generator expressions
   result = (n*2 for n in range(1,11) if n%2==0)
   ```
   
   Benefits: Memory efficient, each value flows through pipeline

────────────────────────────────────────────────────────────────────────────

Q10: What's the memory complexity of generators?
────────────────────────────────────────────────────────────────────────────
A: Generator: O(1) - constant memory regardless of sequence size
   List: O(n) - proportional to data size
   
   Example impact:
   ```python
   # List - must store entire sequence
   all_squares = [x**2 for x in range(1000000)]  # Uses ~40MB
   
   # Generator - stores only current state
   square_gen = (x**2 for x in range(1000000))  # Uses few bytes
   
   # You can iterate infinitely with generators
   def infinite():
       n = 0
       while True:
           yield n
           n += 1
   
   inf = infinite()
   for _ in range(1000000):
       next(inf)  # Constant memory, not growing
   ```

"""

# ============================================================================
# SECTION 4: CONTEXT MANAGERS & ERROR HANDLING
# ============================================================================

CONTEXT_QA = """
┌─────────────────────────────────────────────────────────────────────────┐
│ CONTEXT MANAGERS & ERROR HANDLING                                       │
└─────────────────────────────────────────────────────────────────────────┘

Q1: What is a context manager and why use them?
────────────────────────────────────────────────────────────────────────────
A: Context manager ensures resources are properly acquired and released.
   Implement __enter__() for setup and __exit__() for cleanup.
   
   Common use cases:
   - File I/O (open/close)
   - Database connections
   - Thread locks
   - Temporary state changes
   
   ```python
   class FileManager:
       def __init__(self, filename):
           self.filename = filename
       
       def __enter__(self):
           self.file = open(self.filename, 'r')
           return self.file
       
       def __exit__(self, exc_type, exc_val, exc_tb):
           if self.file:
               self.file.close()
           return False  # Don't suppress exceptions
   
   # Usage
   with FileManager('data.txt') as f:
       content = f.read()
   # File automatically closed, even if exception occurs
   ```

────────────────────────────────────────────────────────────────────────────

Q2: How does the 'with' statement work?
────────────────────────────────────────────────────────────────────────────
A: 'with' statement:
   1. Calls __enter__() on entering block
   2. Assigns return value to 'as' variable
   3. Executes block code
   4. Calls __exit__() on exiting (even on exception!)
   
   ```python
   with expression as var:
       # Equivalent to:
       # var = expression.__enter__()
       # try:
       #     <block code>
       # finally:
       #     expression.__exit__(...)
   ```
   
   __exit__ parameters:
   - exc_type: Exception class (or None if no exception)
   - exc_val: Exception value
   - exc_tb: Traceback object
   
   Return True to suppress exception, False to propagate.

────────────────────────────────────────────────────────────────────────────

Q3: What's @contextmanager decorator?
────────────────────────────────────────────────────────────────────────────
A: Simplifies context manager creation using generators:
   
   ```python
   from contextlib import contextmanager
   
   @contextmanager
   def database_connection(db_name):
       print(f"Connecting to {db_name}")
       conn = f"Connection to {db_name}"
       try:
           yield conn  # Code before yield is __enter__
       except Exception as e:
           print(f"Error: {e}")
           raise
       finally:
           print(f"Closing connection to {db_name}")
       # Code after yield is __exit__
   
   # Usage
   with database_connection("mydb") as conn:
       print(f"Using {conn}")
   ```
   
   Advantages:
   - Less boilerplate
   - Exception handling built-in
   - Easier to understand

────────────────────────────────────────────────────────────────────────────

Q4: How would you handle multiple exceptions?
────────────────────────────────────────────────────────────────────────────
A: Use multiple except clauses, ordered most specific to most general:
   
   ```python
   try:
       # Code that might raise exceptions
       value = int(input("Enter number: "))
       result = 10 / value
   except ValueError:
       print("Invalid input - must be a number")
   except ZeroDivisionError:
       print("Cannot divide by zero")
   except Exception as e:
       print(f"Unexpected error: {e}")
   else:
       print("Success! Result: {result}")
   finally:
       print("Cleanup code always runs")
   ```
   
   Clauses:
   - except: Specific exceptions first
   - else: Runs if no exception
   - finally: Always runs (cleanup)
   
   Order matters! Python checks top-to-bottom, uses first match.

────────────────────────────────────────────────────────────────────────────

Q5: How do you create custom exceptions?
────────────────────────────────────────────────────────────────────────────
A: Inherit from Exception and add domain-specific data:
   
   ```python
   class InsufficientFundsError(Exception):
       def __init__(self, available, requested):
           self.available = available
           self.requested = requested
           super().__init__(
               f"Need ${requested}, only have ${available}"
           )
   
   class ValidationError(Exception):
       def __init__(self, field, message):
           self.field = field
           super().__init__(f"Field '{field}': {message}")
   
   # Usage
   try:
       if balance < amount:
           raise InsufficientFundsError(balance, amount)
   except InsufficientFundsError as e:
       print(f"Error: {e}")
       print(f"Available: ${e.available}")
   ```
   
   Best practices:
   - Inherit from specific exception class
   - Add relevant context data
   - Use meaningful exception names

────────────────────────────────────────────────────────────────────────────

Q6: What's "raise from" and when use it?
────────────────────────────────────────────────────────────────────────────
A: 'raise from' chains exceptions, preserving original traceback:
   
   ```python
   # Without chaining - original exception lost
   try:
       result = 1 / 0
   except ZeroDivisionError:
       raise ValueError("Calculation failed")  # Original lost
   
   # With chaining - preserves original
   try:
       result = 1 / 0
   except ZeroDivisionError as e:
       raise ValueError("Calculation failed") from e  # Original preserved
   ```
   
   Benefits:
   - Full exception history visible in traceback
   - Better debugging
   - Shows root cause
   
   Use 'raise from None' to suppress context:
   ```python
   try:
       result = 1 / 0
   except ZeroDivisionError:
       raise ValueError("Bad calculation") from None  # Hide ZeroDivisionError
   ```

────────────────────────────────────────────────────────────────────────────

Q7: What are metaclasses?
────────────────────────────────────────────────────────────────────────────
A: Metaclass is a "class of a class" - controls how class is created.
   
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
   assert db1 is db2  # Same instance
   ```
   
   Common use cases:
   - Singleton pattern
   - Registering subclasses
   - Auto-generating methods
   - Enforcing structure

────────────────────────────────────────────────────────────────────────────

Q8: What are descriptors?
────────────────────────────────────────────────────────────────────────────
A: Descriptors control attribute access via __get__, __set__, __delete__:
   
   ```python
   class Validator:
       def __init__(self, expected_type):
           self.expected_type = expected_type
           self.data = {}
       
       def __get__(self, obj, objtype=None):
           if obj is None:
               return self
           return self.data.get(id(obj))
       
       def __set__(self, obj, value):
           if not isinstance(value, self.expected_type):
               raise TypeError(f"Expected {self.expected_type}")
           self.data[id(obj)] = value
   
   class Person:
       name = Validator(str)
       age = Validator(int)
   
   p = Person()
   p.name = "Alice"  # Calls __set__ with validation
   print(p.name)     # Calls __get__
   ```
   
   Use cases:
   - Validation
   - Lazy loading
   - Computed properties
   - Type checking

────────────────────────────────────────────────────────────────────────────

Q9: What are type hints used for?
────────────────────────────────────────────────────────────────────────────
A: Type hints improve code documentation and enable static analysis:
   
   ```python
   from typing import List, Dict, Optional, Union
   
   def calculate_average(numbers: List[int]) -> float:
       return sum(numbers) / len(numbers) if numbers else 0.0
   
   def process_data(
       data: Dict[str, int],
       filters: Optional[List[str]] = None
   ) -> Union[int, None]:
       if filters:
           return sum(v for k, v in data.items() if k in filters)
       return sum(data.values())
   ```
   
   Benefits:
   - IDE autocomplete
   - Catch errors early (mypy, type checkers)
   - Self-documenting code
   - Easier refactoring
   
   Note: Type hints are optional, don't enforce at runtime!

────────────────────────────────────────────────────────────────────────────

Q10: What's ExitStack?
────────────────────────────────────────────────────────────────────────────
A: ExitStack manages variable number of context managers dynamically:
   
   ```python
   from contextlib import ExitStack
   
   def process_files(file_paths):
       with ExitStack() as stack:
           files = []
           for path in file_paths:
               # Dynamically add context managers
               f = stack.enter_context(open(path, 'r'))
               files.append(f)
           
           # All files will auto-close
           for f in files:
               print(f.read())
   
   # Without ExitStack, you'd need nested with statements
   ```
   
   Use cases:
   - Unknown number of resources
   - Dynamic resource allocation
   - Cleanup callbacks

"""

# Print all sections
if __name__ == "__main__":
    print("=" * 80)
    print("PYTHON INTERVIEW PREPARATION - COMPREHENSIVE Q&A")
    print("For 3-5 Years Experience Level")
    print("=" * 80)
    
    print(DECORATORS_QA)
    print("\n")
    print(OOP_QA)
    print("\n")
    print(GENERATORS_QA)
    print("\n")
    print(CONTEXT_QA)
    
    print("\n" + "=" * 80)
    print("TIPS FOR INTERVIEW SUCCESS")
    print("=" * 80)
    print("""
1. UNDERSTAND THE FUNDAMENTALS
   - Know why concepts exist, not just how to use them
   - Explain trade-offs (time vs space, flexibility vs simplicity)

2. PROVIDE PRACTICAL EXAMPLES
   - Show code examples for technical concepts
   - Explain the output and why it happens that way

3. DISCUSS TRADE-OFFS
   - When to use inheritance vs composition
   - List comprehension vs generator expression
   - Monolithic vs microservices

4. ASK CLARIFYING QUESTIONS
   - "Are we optimizing for readability or performance?"
   - "What's the size of data we're dealing with?"
   - "Are there concurrency concerns?"

5. MENTION EDGE CASES
   - Empty inputs
   - None values
   - Large data sets
   - Concurrent access

6. FOLLOW-UP PREPARATION
   - Practice coding on whiteboard
   - Explain your code as you write
   - Be ready for "How would you test this?"
   - Know libraries: collections, itertools, functools

7. SOFT SKILLS
   - Communicate clearly
   - Show enthusiasm for learning
   - Discuss real-world applications
   - Mention projects where you used concepts

8. COMMON FOLLOW-UP QUESTIONS TO EXPECT
   - "How would you test this?"
   - "What about edge cases?"
   - "How would this scale?"
   - "Any performance concerns?"
   - "How would you refactor this?"
""")
