"""
GENERATORS, ITERATORS & FUNCTIONAL PROGRAMMING
Essential for: Memory efficiency, lazy evaluation, functional paradigms

Key Concepts:
- Iterators and Iterables (__iter__ and __next__)
- Generators and yield
- Generator expressions
- Functional tools (map, filter, reduce)
- Lambda functions
- List/Dict/Set comprehensions
- Closures and functional patterns
"""

from typing import Generator, Iterator, List, Dict, Callable, Any, Optional
from functools import reduce
import sys


# ============================================================================
# 1. ITERATORS & ITERABLES
# ============================================================================

class CountUp:
    """Custom iterator - implement __iter__ and __next__"""
    
    def __init__(self, max_value: int):
        self.current = 0
        self.max = max_value
    
    def __iter__(self):
        """Return the iterator object (usually self)"""
        return self
    
    def __next__(self) -> int:
        """Return next value or raise StopIteration when done"""
        if self.current < self.max:
            self.current += 1
            return self.current
        else:
            raise StopIteration


class ReverseString:
    """Implement __getitem__ for sequence protocol"""
    
    def __init__(self, text: str):
        self.text = text
        self.index = len(text)
    
    def __iter__(self):
        return self
    
    def __next__(self) -> str:
        if self.index == 0:
            raise StopIteration
        self.index -= 1
        return self.text[self.index]


# ============================================================================
# 2. GENERATORS (Memory-efficient iterators)
# ============================================================================

def simple_generator() -> Generator[int, None, None]:
    """Generator using yield - pauses execution, returns control"""
    print("Generator started")
    yield 1
    print("Resuming...")
    yield 2
    print("Almost done...")
    yield 3
    print("Generator finished")


def countdown(n: int) -> Generator[int, None, None]:
    """Generator that counts down"""
    while n > 0:
        yield n
        n -= 1


def infinite_sequence() -> Generator[int, None, None]:
    """Generator that produces infinite sequence (lazy evaluation)"""
    num = 0
    while True:
        yield num
        num += 1


def fibonacci(limit: int) -> Generator[int, None, None]:
    """Fibonacci generator - efficient memory usage"""
    a, b = 0, 1
    count = 0
    while count < limit:
        yield a
        a, b = b, a + b
        count += 1


def read_large_file(filepath: str, chunk_size: int = 1024) -> Generator[str, None, None]:
    """Generator for reading large files without loading into memory"""
    with open(filepath, 'r') as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            yield chunk


# ============================================================================
# 3. GENERATOR EXPRESSIONS
# ============================================================================

def generator_expression_demo():
    """Generator expressions are like list comprehensions but lazy"""
    
    # List comprehension - creates entire list in memory
    list_comp = [x*2 for x in range(10)]
    
    # Generator expression - creates generator (memory efficient)
    gen_exp = (x*2 for x in range(10))
    
    return list_comp, gen_exp


# ============================================================================
# 4. COMPREHENSIONS
# ============================================================================

def comprehension_examples():
    """List, dict, and set comprehensions"""
    
    # List comprehension with condition
    squares = [x**2 for x in range(10) if x % 2 == 0]
    
    # Dict comprehension
    person_ages = {name: age for name, age in 
                   [("Alice", 30), ("Bob", 25), ("Charlie", 35)]}
    
    # Set comprehension
    unique_lengths = {len(word) for word in 
                      ["apple", "app", "apricot", "bat", "ball"]}
    
    # Nested comprehension
    matrix = [[j for j in range(3)] for i in range(3)]
    
    return squares, person_ages, unique_lengths, matrix


# ============================================================================
# 5. FUNCTIONAL PROGRAMMING CONCEPTS
# ============================================================================

# --------- MAP ---------
def map_example():
    """Apply function to every item in iterable"""
    numbers = [1, 2, 3, 4, 5]
    
    # Traditional map
    squared = map(lambda x: x**2, numbers)
    
    # Map with custom function
    def double(x):
        return x * 2
    doubled = list(map(double, numbers))
    
    # Map with multiple iterables
    nums1 = [1, 2, 3]
    nums2 = [10, 20, 30]
    summed = list(map(lambda x, y: x + y, nums1, nums2))
    
    return list(squared), doubled, summed


# --------- FILTER ---------
def filter_example():
    """Keep items where function returns True"""
    numbers = range(1, 11)
    
    # Filter even numbers
    evens = list(filter(lambda x: x % 2 == 0, numbers))
    
    # Filter with custom function
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True
    
    primes = list(filter(is_prime, numbers))
    
    return evens, primes


# --------- REDUCE ---------
def reduce_example():
    """Accumulate value from left to right"""
    numbers = [1, 2, 3, 4, 5]
    
    # Sum using reduce
    total = reduce(lambda x, y: x + y, numbers)
    
    # Product
    product = reduce(lambda x, y: x * y, numbers)
    
    # Max value
    maximum = reduce(lambda x, y: x if x > y else y, numbers)
    
    return total, product, maximum


# ============================================================================
# 6. LAMBDA FUNCTIONS
# ============================================================================

def lambda_examples():
    """Anonymous functions for short operations"""
    
    # Simple lambda
    add = lambda x, y: x + y
    
    # Lambda in sorted
    people = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
        {"name": "Charlie", "age": 35}
    ]
    sorted_by_age = sorted(people, key=lambda p: p["age"])
    
    # Lambda with conditions
    is_even = lambda x: x % 2 == 0
    numbers = [1, 2, 3, 4, 5, 6]
    evens = list(filter(is_even, numbers))
    
    return add, sorted_by_age, evens


# ============================================================================
# 7. CLOSURES
# ============================================================================

def make_multiplier(n: int) -> Callable:
    """Closure - function that 'remembers' variables from outer scope"""
    def multiplier(x: int) -> int:
        return x * n
    return multiplier


def make_accumulator(initial: int = 0) -> Callable:
    """Accumulator function using closure"""
    total = initial
    
    def add(amount: int) -> int:
        nonlocal total  # Modify variable in enclosing scope
        total += amount
        return total
    
    return add


def rate_limiter(max_calls: int, time_window: int):
    """Rate limiter using closure - tracks call count"""
    import time
    calls = []
    
    def is_allowed() -> bool:
        nonlocal calls
        now = time.time()
        # Remove old calls outside time window
        calls = [call_time for call_time in calls 
                if now - call_time < time_window]
        
        if len(calls) < max_calls:
            calls.append(now)
            return True
        return False
    
    return is_allowed


# ============================================================================
# 8. GENERATOR WITH SEND & THROW
# ============================================================================

def coroutine_example() -> Generator:
    """Two-way generator communication"""
    print("Coroutine started")
    
    try:
        while True:
            value = yield  # Receive value via send()
            if value is None:
                print("No value received")
            else:
                print(f"Received: {value}, Squaring: {value**2}")
    except GeneratorExit:
        print("Coroutine is closing")


# ============================================================================
# 9. CHAIN OPERATIONS WITH GENERATORS
# ============================================================================

def pipeline_processing(data: List[int]) -> Generator[int, None, None]:
    """Chain multiple generator operations"""
    # Filter -> Map -> Process
    filtered = filter(lambda x: x > 5, data)
    mapped = map(lambda x: x * 2, filtered)
    return (x for x in mapped if x < 100)


# ============================================================================
# INTERVIEW QUESTIONS
# ============================================================================

"""
Q1: What's the difference between an iterable and an iterator?
A: Iterable has __iter__() (returns iterator). Iterator has __next__() and 
   __iter__(). Iterator is more specific - it tracks position.

Q2: How are generators different from regular functions?
A: Generators use yield to pause execution and return values incrementally.
   They're lazy (evaluate on demand) and memory-efficient. Return generator object.

Q3: What's the advantage of generators over lists?
A: Generators are lazy - evaluate on demand, saving memory. Lists load 
   everything upfront. For large/infinite sequences, generators are essential.

Q4: Explain "yield" vs "return".
A: return ends function, yield pauses it. Next call continues from yield point.
   yield allows generating sequence without storing all values.

Q5: How do you pass values into a generator?
A: Use generator.send(value). Generator must have yield expression that 
   assigns: value = yield. Called after first next().

Q6: What's a list comprehension vs generator expression?
A: List comprehension [x for x in ...] creates entire list. Generator 
   expression (x for x in ...) is lazy. Use generator for large data.

Q7: Explain map, filter, and reduce.
A: map applies function to all items. filter keeps items where function 
   is True. reduce accumulates values left-to-right.

Q8: When should you use lambda?
A: For simple, one-time-use functions. Avoid complex logic (bad readability).
   Common in map/filter/sorted with key parameter.

Q9: What's a closure?
A: Function that remembers variables from outer scope even after outer 
   function returns. Use nonlocal to modify outer variables.

Q10: How would you implement a generator that takes input (send)?
A: Use yield as expression: x = yield. Then call send(value). Generator 
   receives value and continues. Common in coroutines.

Q11: What's the memory complexity of using generators?
A: O(1) typically - only stores current state, not entire result. Regular 
   functions/lists store all results in O(n).

Q12: Can you use yield in async functions?
A: No, but use async generators with async def + yield. Use async for to iterate.
"""

if __name__ == "__main__":
    print("=" * 70)
    print("GENERATORS, ITERATORS & FUNCTIONAL PROGRAMMING")
    print("=" * 70)
    
    # Test 1: Custom iterator
    print("\n1. CUSTOM ITERATOR:")
    counter = CountUp(3)
    for num in counter:
        print(f"  {num}")
    
    print("\n  Reverse string:")
    for char in ReverseString("Python"):
        print(f"  {char}", end="")
    print()
    
    # Test 2: Generator
    print("\n2. SIMPLE GENERATOR:")
    for value in simple_generator():
        print(f"  Value: {value}")
    
    # Test 3: Fibonacci generator
    print("\n3. FIBONACCI GENERATOR:")
    fib_gen = fibonacci(7)
    fib_list = list(fib_gen)
    print(f"  First 7 Fibonacci numbers: {fib_list}")
    
    # Test 4: Comprehensions
    print("\n4. COMPREHENSIONS:")
    squares, person_ages, unique_lengths, matrix = comprehension_examples()
    print(f"  Squares (evens only): {squares}")
    print(f"  Person ages: {person_ages}")
    print(f"  Unique word lengths: {unique_lengths}")
    
    # Test 5: Functional programming
    print("\n5. FUNCTIONAL PROGRAMMING:")
    list_comp, gen_exp = generator_expression_demo()
    print(f"  List comprehension: {list_comp}")
    print(f"  Generator expression: {gen_exp} (not evaluated yet)")
    
    squared_map, doubled, summed = map_example()
    print(f"  Mapped (squared): {squared_map}")
    print(f"  Doubled: {doubled}")
    print(f"  Summed pairs: {summed}")
    
    evens, primes = filter_example()
    print(f"  Evens (1-10): {evens}")
    print(f"  Primes (1-10): {primes}")
    
    total, product, maximum = reduce_example()
    print(f"  Sum of [1,2,3,4,5]: {total}")
    print(f"  Product: {product}")
    print(f"  Maximum: {maximum}")
    
    # Test 6: Lambda
    print("\n6. LAMBDA FUNCTIONS:")
    add_func, sorted_people, evens_lambda = lambda_examples()
    print(f"  add(5, 3) = {add_func(5, 3)}")
    print(f"  Sorted by age: {sorted_people}")
    print(f"  Evens via lambda filter: {evens_lambda}")
    
    # Test 7: Closures
    print("\n7. CLOSURES:")
    triple = make_multiplier(3)
    print(f"  triple(5) = {triple(5)}")
    
    accumulator = make_accumulator(10)
    print(f"  Starting with 10")
    print(f"  Add 5: {accumulator(5)}")
    print(f"  Add 3: {accumulator(3)}")
    print(f"  Add 2: {accumulator(2)}")
    
    # Test 8: Generator pipeline
    print("\n8. GENERATOR PIPELINE:")
    data = list(range(1, 15))
    result = list(pipeline_processing(data))
    print(f"  Input: {data}")
    print(f"  Filter >5, Map *2, Filter <100: {result}")
    
    # Test 9: Memory comparison
    print("\n9. MEMORY COMPARISON:")
    list_gen = [x for x in range(1000000)]
    gen_gen = (x for x in range(1000000))
    print(f"  List size: {sys.getsizeof(list_gen)} bytes")
    print(f"  Generator size: {sys.getsizeof(gen_gen)} bytes")
