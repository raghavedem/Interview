"""
OBJECT-ORIENTED PROGRAMMING & DESIGN PATTERNS
Essential for: Building scalable applications, system design, inheritance hierarchies

Key Concepts:
- Classes and Objects
- Inheritance and Polymorphism
- Encapsulation (public, private, protected)
- Composition vs Inheritance
- Design Patterns (Factory, Singleton, Strategy)
- Abstract Base Classes
- Properties and Descriptors
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from enum import Enum


# ============================================================================
# 1. BASIC CLASS STRUCTURE
# ============================================================================

class Person:
    """Basic class with __init__, __str__, __repr__"""
    
    # Class variable (shared across instances)
    species = "Homo sapiens"
    
    def __init__(self, name: str, age: int):
        """Instance variables - data unique to each object"""
        self.name = name
        self.age = age
    
    def __str__(self) -> str:
        """User-friendly string representation"""
        return f"{self.name} ({self.age} years old)"
    
    def __repr__(self) -> str:
        """Developer-friendly representation for debugging"""
        return f"Person(name='{self.name}', age={self.age})"
    
    def __eq__(self, other) -> bool:
        """Compare objects for equality"""
        if not isinstance(other, Person):
            return False
        return self.name == other.name and self.age == other.age
    
    def introduce(self) -> str:
        return f"Hi, I'm {self.name}"


# ============================================================================
# 2. SINGLE INHERITANCE
# ============================================================================

class Employee(Person):
    """Inherits from Person, extends with employee-specific attributes"""
    
    def __init__(self, name: str, age: int, employee_id: str, salary: float):
        super().__init__(name, age)  # Call parent constructor
        self.employee_id = employee_id
        self.salary = salary
    
    def __str__(self) -> str:
        """Override parent method"""
        return f"{super().__str__()} - Employee ID: {self.employee_id}"
    
    def give_raise(self, percentage: float) -> None:
        """New method specific to Employee"""
        self.salary *= (1 + percentage)


# ============================================================================
# 3. MULTIPLE INHERITANCE & METHOD RESOLUTION ORDER (MRO)
# ============================================================================

class CanFly:
    """Mixin: adds flying capability"""
    def fly(self) -> str:
        return "🛫 Flying..."


class CanSwim:
    """Mixin: adds swimming capability"""
    def swim(self) -> str:
        return "🏊 Swimming..."


class Duck(Person, CanFly, CanSwim):
    """Multiple inheritance - inherits from Person and two mixins"""
    
    def __init__(self, name: str):
        super().__init__(name, age=5)
    
    @classmethod
    def mro_demo(cls):
        """Display Method Resolution Order"""
        return [c.__name__ for c in cls.__mro__]


# ============================================================================
# 4. ENCAPSULATION (Data Hiding)
# ============================================================================

class BankAccount:
    """Demonstrates public, protected, and private attributes"""
    
    def __init__(self, account_holder: str, balance: float):
        self.account_holder = account_holder          # Public
        self._pin = "1234"                            # Protected (convention)
        self.__balance = balance                      # Private (name mangling)
    
    @property
    def balance(self) -> float:
        """Read-only property - controlled access to private attribute"""
        return self.__balance
    
    @balance.setter
    def balance(self, amount: float) -> None:
        """Setter with validation"""
        if amount < 0:
            raise ValueError("Balance cannot be negative")
        self.__balance = amount
    
    def withdraw(self, amount: float) -> float:
        """Protected method access to private data"""
        if amount > self.__balance:
            raise ValueError("Insufficient funds")
        self.__balance -= amount
        return self.__balance
    
    def deposit(self, amount: float) -> float:
        """Update private attribute via method"""
        if amount <= 0:
            raise ValueError("Deposit must be positive")
        self.__balance += amount
        return self.__balance


# ============================================================================
# 5. ABSTRACT BASE CLASSES (Interfaces)
# ============================================================================

class Animal(ABC):
    """Abstract base class - cannot be instantiated directly"""
    
    @abstractmethod
    def make_sound(self) -> str:
        """Subclasses must implement this method"""
        pass
    
    @abstractmethod
    def move(self) -> str:
        """Another required method"""
        pass
    
    def describe(self) -> str:
        """Concrete method - implementations can inherit this"""
        return f"I'm a {self.__class__.__name__}"


class Dog(Animal):
    """Must implement abstract methods"""
    
    def make_sound(self) -> str:
        return "🐕 Woof!"
    
    def move(self) -> str:
        return "Running on four legs"


class Bird(Animal):
    """Different implementation of abstract methods"""
    
    def make_sound(self) -> str:
        return "🐦 Tweet!"
    
    def move(self) -> str:
        return "Flying with wings"


# ============================================================================
# 6. COMPOSITION OVER INHERITANCE
# ============================================================================

class Engine:
    """Composable component"""
    def __init__(self, horsepower: int):
        self.horsepower = horsepower
    
    def start(self) -> str:
        return f"🔧 Engine started ({self.horsepower}hp)"


class Wheel:
    """Composable component"""
    def __init__(self, size: int):
        self.size = size


class Car:
    """Uses composition - has-a relationships instead of is-a"""
    
    def __init__(self, make: str, model: str, engine: Engine):
        self.make = make
        self.model = model
        self.engine = engine  # Composition
        self.wheels = [Wheel(18) for _ in range(4)]
    
    def drive(self) -> str:
        return f"{self.make} {self.model} is driving. {self.engine.start()}"


# ============================================================================
# 7. DESIGN PATTERNS
# ============================================================================

# --------- FACTORY PATTERN ---------
class PaymentProcessor:
    """Factory pattern - create objects without specifying exact classes"""
    
    @staticmethod
    def create_payment(payment_type: str, amount: float) -> 'Payment':
        """Factory method"""
        if payment_type == "credit_card":
            return CreditCardPayment(amount)
        elif payment_type == "paypal":
            return PayPalPayment(amount)
        elif payment_type == "crypto":
            return CryptoPayment(amount)
        else:
            raise ValueError(f"Unknown payment type: {payment_type}")


class Payment(ABC):
    def __init__(self, amount: float):
        self.amount = amount
    
    @abstractmethod
    def process(self) -> str:
        pass


class CreditCardPayment(Payment):
    def process(self) -> str:
        return f"💳 Processing ${self.amount} via Credit Card"


class PayPalPayment(Payment):
    def process(self) -> str:
        return f"🅿️  Processing ${self.amount} via PayPal"


class CryptoPayment(Payment):
    def process(self) -> str:
        return f"₿ Processing ${self.amount} via Cryptocurrency"


# --------- SINGLETON PATTERN ---------
class DatabaseConnection:
    """Singleton pattern - only one instance exists"""
    _instance: Optional['DatabaseConnection'] = None
    
    def __new__(cls) -> 'DatabaseConnection':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connected = False
        return cls._instance
    
    def connect(self) -> None:
        if not self.connected:
            print("🔌 Connecting to database...")
            self.connected = True


# --------- STRATEGY PATTERN ---------
class SortingStrategy(ABC):
    """Strategy pattern - different algorithms for same operation"""
    
    @abstractmethod
    def sort(self, data: List[int]) -> List[int]:
        pass


class BubbleSort(SortingStrategy):
    def sort(self, data: List[int]) -> List[int]:
        arr = data.copy()
        n = len(arr)
        for i in range(n):
            for j in range(n - 1 - i):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr


class QuickSort(SortingStrategy):
    def sort(self, data: List[int]) -> List[int]:
        if len(data) <= 1:
            return data
        pivot = data[0]
        less = [x for x in data[1:] if x <= pivot]
        greater = [x for x in data[1:] if x > pivot]
        return self.sort(less) + [pivot] + self.sort(greater)


class Sorter:
    """Context class - uses different strategies"""
    def __init__(self, strategy: SortingStrategy):
        self.strategy = strategy
    
    def execute(self, data: List[int]) -> List[int]:
        return self.strategy.sort(data)


# ============================================================================
# 8. PROPERTIES & DESCRIPTORS
# ============================================================================

class Temperature:
    """Using @property for computed attributes"""
    
    def __init__(self, celsius: float):
        self._celsius = celsius
    
    @property
    def celsius(self) -> float:
        """Getter"""
        return self._celsius
    
    @celsius.setter
    def celsius(self, value: float) -> None:
        """Setter with validation"""
        if value < -273.15:
            raise ValueError("Temperature below absolute zero")
        self._celsius = value
    
    @property
    def fahrenheit(self) -> float:
        """Computed property"""
        return (self._celsius * 9/5) + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value: float) -> None:
        """Computed property setter"""
        self._celsius = (value - 32) * 5/9


# ============================================================================
# INTERVIEW QUESTIONS
# ============================================================================

"""
Q1: What's the difference between __init__ and __new__?
A: __new__ creates the instance (returns object), __init__ initializes it.
   __new__ is rarely overridden unless creating immutable objects or singletons.

Q2: Explain Method Resolution Order (MRO).
A: Python uses C3 linearization. Classes are searched left-to-right, depth-first.
   Use cls.__mro__ or help(cls) to see order. Critical for multiple inheritance.

Q3: What are class variables vs instance variables?
A: Class variables are shared across all instances. Instance variables are 
   unique per object. Modifications to class vars affect all instances.

Q4: How does name mangling work with __ prefix?
A: Python translates __attribute to _ClassName__attribute to discourage access.
   Not true privacy - can still access via _BankAccount__balance if needed.

Q5: When should you use composition over inheritance?
A: Use composition (has-a) for flexibility. Inheritance (is-a) for true 
   hierarchical relationships. Composition is more maintainable and testable.

Q6: What's the difference between abstract methods and concrete methods in ABC?
A: Abstract methods (marked @abstractmethod) must be implemented by subclasses.
   Concrete methods can be inherited. Mixes interface and functionality.

Q7: Explain the Factory Pattern and when to use it.
A: Factory pattern creates objects without specifying exact classes. Use when
   object creation logic is complex or multiple implementations exist.

Q8: What's a Singleton and how do you implement it?
A: Singleton ensures only one instance exists. Implement via __new__ or 
   metaclass. Use for shared resources (DB connections, loggers).

Q9: What's the difference between @property and @classmethod?
A: @property accesses/sets instance data like attributes. @classmethod operates
   on class data (first arg is cls). @staticmethod needs neither (first arg is self/cls).

Q10: How would you implement __eq__ and __hash__?
A: __eq__ defines equality comparison. __hash__ makes objects usable in sets/dicts.
    If you override __eq__, also override __hash__ or set it to None.
"""

if __name__ == "__main__":
    print("=" * 70)
    print("OBJECT-ORIENTED PROGRAMMING & DESIGN PATTERNS")
    print("=" * 70)
    
    # Test 1: Basic class
    print("\n1. BASIC CLASS & INHERITANCE:")
    p = Person("Alice", 30)
    print(f"str():  {str(p)}")
    print(f"repr(): {repr(p)}")
    
    emp = Employee("Bob", 35, "E001", 75000)
    print(f"Employee: {emp}")
    emp.give_raise(0.10)
    print(f"After 10% raise: ${emp.salary:,.2f}\n")
    
    # Test 2: Multiple inheritance & MRO
    print("2. MULTIPLE INHERITANCE & MRO:")
    duck = Duck("Donald")
    print(f"{duck.fly()}")
    print(f"{duck.swim()}")
    print(f"MRO: {Duck.mro_demo()}\n")
    
    # Test 3: Encapsulation
    print("3. ENCAPSULATION:")
    account = BankAccount("John", 1000)
    print(f"Initial balance: ${account.balance}")
    account.deposit(500)
    print(f"After deposit: ${account.balance}")
    account.withdraw(200)
    print(f"After withdrawal: ${account.balance}\n")
    
    # Test 4: Abstract classes
    print("4. ABSTRACT CLASSES:")
    dog = Dog()
    bird = Bird()
    print(f"Dog: {dog.make_sound()} {dog.move()}")
    print(f"Bird: {bird.make_sound()} {bird.move()}\n")
    
    # Test 5: Composition
    print("5. COMPOSITION:")
    engine = Engine(200)
    car = Car("Toyota", "Camry", engine)
    print(car.drive())
    print()
    
    # Test 6: Factory Pattern
    print("6. FACTORY PATTERN:")
    payment1 = PaymentProcessor.create_payment("credit_card", 99.99)
    payment2 = PaymentProcessor.create_payment("paypal", 49.99)
    print(payment1.process())
    print(payment2.process())
    print()
    
    # Test 7: Singleton
    print("7. SINGLETON PATTERN:")
    db1 = DatabaseConnection()
    db2 = DatabaseConnection()
    print(f"Same instance: {db1 is db2}")
    db1.connect()
    db2.connect()
    print()
    
    # Test 8: Strategy Pattern
    print("8. STRATEGY PATTERN:")
    data = [64, 34, 25, 12, 22, 11, 90]
    bubble_sorter = Sorter(BubbleSort())
    quick_sorter = Sorter(QuickSort())
    print(f"Original: {data}")
    print(f"Bubble Sort: {bubble_sorter.execute(data)}")
    print(f"Quick Sort: {quick_sorter.execute(data)}\n")
    
    # Test 9: Properties
    print("9. PROPERTIES:")
    temp = Temperature(25)
    print(f"Celsius: {temp.celsius}°C")
    print(f"Fahrenheit: {temp.fahrenheit}°F")
    temp.fahrenheit = 86
    print(f"After setting to 86°F: {temp.celsius:.2f}°C")
