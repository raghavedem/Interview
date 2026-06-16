# Python Interview Preparation Project
## For 3-5 Years Experience Level

Complete project covering essential Python concepts with practical examples and interview questions.

---

## 📋 Project Structure

### 1. **1_decorators.py** - Decorators & Higher-Order Functions
**Topics Covered:**
- Basic decorators with `functools.wraps`
- Parameterized decorators (decorator factories)
- Timing decorators (performance measurement)
- Memoization/caching (optimize repeated calls)
- Stacked decorators (combining multiple decorators)
- Class-based decorators
- Validation decorators (argument checking)

**Key Interview Questions:**
- What is a decorator and how do they work?
- Difference between `@decorator` and `@decorator()`
- How to write a type-validating decorator?
- Why use `functools.wraps`?
- How would you debug stacked decorators?

**Run:**
```bash
python 1_decorators.py
```

---

### 2. **2_oop_design_patterns.py** - OOP & Design Patterns
**Topics Covered:**
- Basic class structure (`__init__`, `__str__`, `__repr__`, `__eq__`)
- Single and multiple inheritance
- Method Resolution Order (MRO)
- Encapsulation (public, protected, private attributes)
- Abstract Base Classes (ABC)
- Composition vs Inheritance
- Design Patterns:
  - Factory Pattern
  - Singleton Pattern
  - Strategy Pattern
- Properties with getters/setters

**Key Interview Questions:**
- `__init__` vs `__new__` - what's the difference?
- Explain Method Resolution Order (MRO)
- Class variables vs instance variables
- Name mangling with `__` prefix
- When to use composition over inheritance
- Implement Singleton pattern
- When to use Strategy pattern
- How do @property decorators work?

**Run:**
```bash
python 2_oop_design_patterns.py
```

---

### 3. **3_generators_functional.py** - Generators & Functional Programming
**Topics Covered:**
- Iterators and Iterables
- Custom iterator implementation
- Generators and `yield`
- Generator expressions vs list comprehensions
- List/dict/set comprehensions
- Functional programming: `map()`, `filter()`, `reduce()`
- Lambda functions
- Closures and `nonlocal`
- Generator pipelines (chaining)
- Memory complexity comparison

**Key Interview Questions:**
- Difference between iterable and iterator
- How are generators different from regular functions?
- `yield` vs `return` - what's the difference?
- How do you pass values into a generator (`.send()`)?
- List comprehension vs generator expression
- When to use lambda functions
- What is a closure?
- How to implement a generator pipeline?
- Memory complexity of generators

**Run:**
```bash
python 3_generators_functional.py
```

---

### 4. **4_context_managers_advanced.py** - Context Managers & Advanced Concepts
**Topics Covered:**
- Context managers with `__enter__` and `__exit__`
- `@contextmanager` decorator
- Exception handling (try/except/else/finally)
- Custom exceptions
- Exception chaining (`raise from`)
- Metaclasses (advanced OOP)
- Descriptors (`__get__`, `__set__`, `__delete__`)
- Type hints and annotations
- ExitStack for multiple context managers

**Key Interview Questions:**
- What is a context manager and why use them?
- How does the `with` statement work?
- Difference between contextmanager decorator and custom class
- How to handle multiple exceptions
- When to create custom exceptions
- What are metaclasses used for?
- What are descriptors?
- Why use type hints?
- How to manage multiple context managers with ExitStack?

**Run:**
```bash
python 4_context_managers_advanced.py
```

---

### 5. **5_interview_questions_answers.py** - Comprehensive Q&A Reference
**Contains:**
- 40+ interview questions with detailed answers
- Follow-up questions and alternative approaches
- Code examples for each concept
- Tips for interview success
- Common pitfalls to avoid

**Run:**
```bash
python 5_interview_questions_answers.py
```

This will print comprehensive Q&A for all major topics.

---

## 🎯 Key Concepts Quick Reference

### Decorators
```python
# Simple decorator
@decorator
def func(): pass

# With parameters
@decorator(param=value)
def func(): pass

# Timing decorator
@timer
def expensive_operation(): pass

# Memoization
@memoize
def fibonacci(n): pass
```

### OOP
```python
# Inheritance
class Child(Parent): pass

# Abstract class
class Abstract(ABC):
    @abstractmethod
    def method(self): pass

# Properties
class Person:
    @property
    def age(self): return self._age
    
    @age.setter
    def age(self, value): self._age = value

# Singleton
class Database(metaclass=SingletonMeta): pass
```

### Generators
```python
# Generator function
def gen():
    yield 1
    yield 2

# Generator expression
gen_exp = (x for x in range(10))

# Iterator
class MyIterator:
    def __iter__(self): return self
    def __next__(self): ...

# Functional operations
map(func, iterable)
filter(condition, iterable)
reduce(accumulator, iterable)
```

### Context Managers
```python
# Class-based
class Manager:
    def __enter__(self): ...
    def __exit__(self, exc_type, exc_val, exc_tb): ...

# Decorator-based
@contextmanager
def managed():
    # Setup
    yield resource
    # Cleanup

# With statement
with Manager() as m:
    pass  # Auto cleanup
```

---

## 📚 How to Use This Project

### For Learning
1. **Read the code files sequentially** from 1 to 5
2. **Run each file** to see examples in action
3. **Modify the code** - experiment with changes
4. **Study the docstrings** for detailed explanations

### For Interview Prep
1. **Review file 5** (interview Q&A) for comprehensive coverage
2. **Focus on concepts** you're weak in
3. **Practice explaining** the code out loud
4. **Run the code** to verify your understanding
5. **Modify examples** to create variations

### For Reference
- Each file is self-contained
- Docstrings explain concepts
- Interview questions included in each file
- Run individual files to test specific concepts

---

## 🔥 Most Important Interview Topics

### Top 10 Must-Know
1. **Decorators** - Extremely common interview topic
2. **OOP Fundamentals** - Expected knowledge for 3+ years
3. **Generators** - Shows understanding of memory/performance
4. **Inheritance & MRO** - Design fundamental
5. **Context Managers** - Production code requirement
6. **Exception Handling** - Real-world essential
7. **Functional Programming** - Shows modern Python knowledge
8. **Design Patterns** - Architecture maturity
9. **Type Hints** - Modern Python best practices
10. **Metaclasses** - Advanced OOP (may not be asked, but impressive to know)

---

## 💡 Interview Tips

### What Interviewers Look For
- **Understanding the why**, not just the how
- **Trade-offs awareness** (time vs space, simplicity vs flexibility)
- **Real-world application** of concepts
- **Code quality** (readability, maintainability)
- **Edge case handling** (None, empty, large inputs)
- **Performance considerations** (complexity analysis)

### How to Answer
1. **Clarify the question** - "Do you mean ...?"
2. **Explain the concept** - Use simple language
3. **Provide examples** - Show code samples
4. **Discuss trade-offs** - When to use/not use
5. **Mention alternatives** - Other approaches
6. **Ask follow-ups** - "Does this scale?"

### Common Pitfalls
- ❌ Memorizing answers without understanding
- ❌ Using complex jargon without explanation
- ❌ Not mentioning edge cases
- ❌ Forgetting to explain why, just how
- ❌ Not asking clarifying questions
- ✅ Instead: Explain concepts, provide examples, discuss trade-offs

---

## 🧪 Testing Your Knowledge

### Quick Checks
After each file, ask yourself:
- Can I explain this concept in plain English?
- Can I write code example from memory?
- Do I understand the trade-offs?
- Can I name real-world use cases?
- Would I recognize this in a code review?

### Practice Exercises
1. **Modify decorators** - Create your own timing/validation decorator
2. **Extend OOP examples** - Add methods, create subclasses
3. **Refactor to generators** - Convert lists to generators
4. **Build context manager** - Create one for your use case
5. **Combine concepts** - Use decorator + generator + context manager

---

## 📖 Supplementary Resources

### To Learn More
- **Official Python Docs**: https://docs.python.org/3/
- **PEP 20 (The Zen of Python)**: `python -c "import this"`
- **Real Python**: Real-world tutorials and examples
- **GeeksforGeeks Python**: Comprehensive reference

### Related Topics to Study
- Async/Await (asynchronous programming)
- Testing (unittest, pytest)
- Logging (logging module)
- Collections (defaultdict, Counter, deque)
- Itertools (combinations, permutations)

---

## 🎓 Experience Level Notes

### 3-5 Years Developer Should Know
- ✅ All topics in this project
- ✅ Why to use each concept
- ✅ When NOT to use (trade-offs)
- ✅ How to explain to junior developers
- ✅ Real-world applications
- ✅ Performance implications
- ✅ How to test code using these concepts

### Not Expected to Know (Advanced)
- ❌ Every exotic decorator use case
- ❌ Metaclass internals (just know what they are)
- ❌ Descriptor protocol edge cases
- ❌ CPython implementation details
- Note: But knowing these is impressive!

---

## 📊 Self-Assessment Checklist

- [ ] Understand decorators and can write custom ones
- [ ] Know OOP hierarchy and MRO without looking it up
- [ ] Can explain generators vs lists from memory
- [ ] Understand context managers and use them properly
- [ ] Know 5+ design patterns and when to use them
- [ ] Can write lambda functions appropriately
- [ ] Understand closures and nonlocal
- [ ] Know exception handling best practices
- [ ] Can explain comprehensions vs generators
- [ ] Understand map/filter/reduce operations
- [ ] Know when to use abstract classes
- [ ] Can implement Singleton and Factory patterns
- [ ] Understand type hints and their benefits
- [ ] Know difference between @property and @classmethod
- [ ] Can explain MRO with multiple inheritance

**Score >= 13/15**: Ready for interviews!
**Score < 13/15**: Keep studying, focus on gaps

---

## 🚀 Next Steps After This Project

1. **Build Something**: Create a small project using these concepts
2. **Code Review**: Review others' code, spot patterns
3. **Practice Problems**: LeetCode, HackerRank medium problems
4. **System Design**: Learn to apply concepts at scale
5. **Advanced Topics**: Async, concurrency, performance optimization

---

## 📝 File Summary

| File | Topics | Lines | Complexity |
|------|--------|-------|-----------|
| 1_decorators.py | Decorators, higher-order functions | ~400 | ⭐⭐ |
| 2_oop_design_patterns.py | OOP, design patterns, inheritance | ~600 | ⭐⭐⭐ |
| 3_generators_functional.py | Generators, iterators, functional | ~500 | ⭐⭐⭐ |
| 4_context_managers_advanced.py | Context managers, metaclasses | ~500 | ⭐⭐⭐⭐ |
| 5_interview_questions_answers.py | Q&A reference guide | ~800 | ⭐ |

**Total**: 2,800+ lines of code and documentation

---

## ✨ Special Features

- ✅ Production-quality code examples
- ✅ Type hints throughout
- ✅ Comprehensive docstrings
- ✅ Real-world scenarios
- ✅ Interview questions embedded in code
- ✅ Executable demonstrations
- ✅ Edge case handling
- ✅ Best practices shown

---

## 📞 Questions or Improvements?

This project is designed to be comprehensive yet practical. If you find areas that need clarification, create more examples or modify existing ones.

**Happy coding and good luck with interviews! 🎯**

---

*Last Updated: 2024*
*Python Version: 3.8+*
*Created for: 3-5 Years Experience Level*
