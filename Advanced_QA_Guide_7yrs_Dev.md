# Advanced Q&A Guide: HTML, CSS, JavaScript, Python
## For 7+ Years Experienced Developers

---

## TABLE OF CONTENTS
1. [HTML Advanced Concepts](#html-advanced-concepts)
2. [CSS Advanced Concepts](#css-advanced-concepts)
3. [JavaScript Advanced Concepts](#javascript-advanced-concepts)
4. [Python Advanced Concepts](#python-advanced-concepts)

---

## HTML ADVANCED CONCEPTS

### Q1: Explain Web Components and Shadow DOM. How do you use them in modern applications?

**A:** Web Components are a set of APIs (Custom Elements, Shadow DOM, HTML Templates, and ES Modules) that allow you to create reusable, encapsulated components.

**Shadow DOM** provides style and DOM encapsulation:
```html
<template id="my-template">
  <style>
    :host { display: block; }
    p { color: blue; }
  </style>
  <p>Shadow DOM Content</p>
</template>

<script>
class MyComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }
  
  connectedCallback() {
    const template = document.getElementById('my-template');
    this.shadowRoot.appendChild(template.content.cloneNode(true));
  }
}

customElements.define('my-component', MyComponent);
</script>

<my-component></my-component>
```

**Key Benefits:**
- Style encapsulation (internal styles don't leak)
- DOM encapsulation (internal DOM hidden from outside queries)
- Reusability across projects
- Framework-independent components

### Q2: What is the difference between semantic HTML and non-semantic HTML? Why does it matter?

**A:** Semantic HTML uses meaningful elements that describe content purpose.

**Semantic Elements:**
- `<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<aside>`, `<footer>`
- `<figure>`, `<figcaption>`, `<time>`, `<mark>`, `<progress>`

**Non-semantic:**
- `<div>`, `<span>` (no meaning)

**Why It Matters:**
1. **Accessibility:** Screen readers understand document structure
2. **SEO:** Search engines better understand content hierarchy
3. **Maintainability:** Code is self-documenting
4. **Browser features:** Native elements get built-in functionality
5. **Responsive design:** Easier to style with CSS

```html
<!-- Non-semantic -->
<div class="container">
  <div class="header">
    <div class="nav">Home | About | Contact</div>
  </div>
  <div class="content">Article here</div>
  <div class="footer">Copyright 2024</div>
</div>

<!-- Semantic -->
<body>
  <header>
    <nav>Home | About | Contact</nav>
  </header>
  <main>
    <article>Article here</article>
  </main>
  <footer>Copyright 2024</footer>
</body>
```

### Q3: Explain ARIA roles, properties, and states with practical examples.

**A:** ARIA (Accessible Rich Internet Applications) enhances accessibility for complex interfaces.

**Three Categories:**
1. **Roles:** Define what element is (toolbar, menu, alert)
2. **Properties:** Describe element characteristics (aria-label, aria-describedby)
3. **States:** Describe element status (aria-expanded, aria-checked, aria-hidden)

```html
<!-- Custom Tab Component -->
<div class="tabs">
  <div role="tablist">
    <button role="tab" aria-selected="true" aria-controls="panel1" id="tab1">
      Tab 1
    </button>
    <button role="tab" aria-selected="false" aria-controls="panel2" id="tab2">
      Tab 2
    </button>
  </div>
  
  <div role="tabpanel" id="panel1" aria-labelledby="tab1">
    Content 1
  </div>
  <div role="tabpanel" id="panel2" aria-labelledby="tab2" hidden>
    Content 2
  </div>
</div>

<!-- Alert Dialog -->
<div role="alertdialog" aria-labelledby="alert-title" aria-describedby="alert-desc">
  <h2 id="alert-title">Warning</h2>
  <p id="alert-desc">Are you sure you want to proceed?</p>
</div>

<!-- Live Region for dynamic updates -->
<div aria-live="polite" aria-atomic="true">
  <!-- Content updates here without page reload -->
</div>
```

### Q4: What are HTML data attributes and how do you use them effectively?

**A:** Data attributes (`data-*`) store custom data private to HTML and CSS.

```html
<article id="article-1"
  data-author="John Doe"
  data-date="2024-01-15"
  data-read-time="5"
  data-tags='["javascript", "html"]'>
  <h2>Article Title</h2>
</article>

<script>
// Access via dataset
const article = document.getElementById('article-1');
console.log(article.dataset.author);        // "John Doe"
console.log(article.dataset.readTime);      // "5"
console.log(JSON.parse(article.dataset.tags)); // Array

// Access via getAttribute
console.log(article.getAttribute('data-date')); // "2024-01-15"
</script>

<style>
/* Use in CSS selectors */
article[data-author="John Doe"] { color: green; }

/* Use with content property */
article::after { content: " - " attr(data-author); }
</style>
```

**Best Practices:**
- Store application state, not styling data
- Use camelCase: `data-readTime` (converts to `dataset.readTime`)
- Keep values small for performance
- Use JSON for complex data

---

## CSS ADVANCED CONCEPTS

### Q1: Explain CSS Grid vs Flexbox. When do you use each?

**A:** Both are layout systems with different purposes.

**Flexbox:**
- One-dimensional layout (row OR column)
- Content-driven (size items, then allocate space)
- Better for components and small layouts
- Simpler for alignment

**Grid:**
- Two-dimensional layout (rows AND columns)
- Layout-driven (define layout, then place content)
- Better for page layouts and complex structures
- Precise control over positioning

```css
/* Flexbox: Navigation Bar */
.navbar {
  display: flex;
  justify-content: space-between;  /* horizontal spacing */
  align-items: center;              /* vertical alignment */
  gap: 1rem;
}

/* Grid: Page Layout */
.page {
  display: grid;
  grid-template-columns: 200px 1fr 300px;  /* sidebar, main, aside */
  grid-template-rows: 60px 1fr 60px;       /* header, content, footer */
  gap: 1rem;
  height: 100vh;
}

.page header { grid-column: 1 / -1; }  /* span all columns */
.page footer { grid-column: 1 / -1; }

/* Grid: Responsive without media queries */
.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}
```

### Q2: What are CSS custom properties and how do they differ from preprocessor variables?

**A:** CSS custom properties (variables) are dynamic and inherit through the DOM.

```css
/* Define custom properties */
:root {
  --primary-color: #3498db;
  --spacing-unit: 1rem;
  --border-radius: 4px;
  --transition-speed: 0.3s;
}

/* Inherit through DOM */
.card {
  background: var(--primary-color);
  padding: var(--spacing-unit);
  border-radius: var(--border-radius);
  transition: all var(--transition-speed);
}

/* Override per component */
.card.urgent {
  --primary-color: #e74c3c;
}

/* Fallback values */
.element {
  color: var(--custom-color, #333);
}

/* JavaScript manipulation */
document.documentElement.style.setProperty('--primary-color', '#2ecc71');

/* Computed values */
const primary = getComputedStyle(document.documentElement)
  .getPropertyValue('--primary-color');

/* Dynamic theming */
.dark-mode {
  --primary-color: #2c3e50;
  --text-color: #ecf0f1;
  --bg-color: #1a1a1a;
}
```

**Advantages over Preprocessor Variables:**
- Dynamic (can change at runtime)
- Inherit through DOM
- Can use in media queries
- Accessible via JavaScript
- Real CSS (no compilation needed)

### Q3: Explain CSS Stacking Context and z-index behavior.

**A:** Stacking Context determines how elements layer in 3D space perpendicular to the screen.

**Properties Creating Stacking Context:**
- `position: absolute/relative/fixed` with `z-index` ≠ auto
- `opacity` < 1
- `transform`, `filter`, `backdrop-filter` (not none)
- `will-change` (certain properties)
- `isolation: isolate`

```css
/* Parent creates stacking context, child z-index isolated */
.parent {
  position: relative;
  z-index: 1;  /* Creates stacking context */
}

.parent .child {
  z-index: 9999;  /* Can't exceed parent's context */
}

.sibling {
  position: relative;
  z-index: 2;   /* Will appear above .parent and its children */
}

/* Prevent z-index wars with isolation */
.container {
  isolation: isolate;  /* New stacking context without z-index */
}

.modal {
  position: fixed;
  z-index: 1000;
  opacity: 0.95;  /* Creates stacking context, z-index becomes relevant */
}
```

### Q4: What is the CSS contain property and why is it important for performance?

**A:** `contain` property optimizes browser rendering by limiting scope of style calculations.

```css
/* Contain: size */
.widget {
  contain: size;
  width: 300px;
  height: 300px;
  /* Browser knows this element won't exceed these bounds */
}

/* Contain: layout */
.component {
  contain: layout;
  /* Layout changes inside don't affect outside elements */
}

/* Contain: paint */
.card {
  contain: paint;
  /* Paint operations contained to this element */
  overflow: hidden;
}

/* Contain: style */
.widget {
  contain: style;
  /* Style changes don't leak to siblings */
}

/* Shorthand: all */
.isolated {
  contain: size layout paint style;
  /* or: contain: strict; */
}

/* Content-visibility for off-screen optimization */
.item {
  content-visibility: auto;
  contain: layout paint style;
  /* Skips rendering off-screen items */
}
```

### Q5: Explain CSS-in-JS approaches and their trade-offs.

**A:** CSS-in-JS (CSS in JavaScript) provides dynamic styling and scoping.

```javascript
// Emotion/Styled-components approach
import styled from 'styled-components';

const Button = styled.button`
  background-color: ${props => props.primary ? '#3498db' : '#95a5a6'};
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  
  &:hover {
    opacity: 0.9;
  }
  
  &:disabled {
    cursor: not-allowed;
    opacity: 0.6;
  }
`;

// BEM with JavaScript
const buttonClasses = `btn btn--${size} btn--${variant}`;

// Utility-first (Tailwind)
<button className="px-4 py-2 bg-blue-500 text-white rounded hover:opacity-90">
  Click me
</button>
```

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **CSS-in-JS** | Dynamic styles, component scope, runtime control | Bundle size, JS execution, no static extraction |
| **BEM/SMACSS** | Predictable, fast, caching | Verbose naming, manual scoping |
| **Utility-First** | Small bundle, composable, fast | Large HTML, learning curve, customization |

---

## JAVASCRIPT ADVANCED CONCEPTS

### Q1: Explain JavaScript closures, scope chain, and lexical scoping with practical examples.

**A:** Closures allow functions to access variables from outer scopes even after execution.

```javascript
// Basic Closure
function createCounter() {
  let count = 0;  // Private variable
  
  return {
    increment() { return ++count; },
    decrement() { return --count; },
    getCount() { return count; }
  };
}

const counter = createCounter();
console.log(counter.increment()); // 1
console.log(counter.increment()); // 2
console.log(counter.getCount());  // 2

// Scope Chain Example
const global = 'global';

function outer() {
  const outerVar = 'outer';
  
  function middle() {
    const middleVar = 'middle';
    
    function inner() {
      const innerVar = 'inner';
      console.log(innerVar, middleVar, outerVar, global);
      // Looks up scope chain: inner → middle → outer → global
    }
    inner();
  }
  middle();
}

outer();

// Practical: Event Handler with Closure
function setupButtons() {
  for (let i = 1; i <= 3; i++) {  // Use let, not var
    const btn = document.getElementById(`btn${i}`);
    btn.addEventListener('click', () => {
      console.log(`Button ${i} clicked`);  // Closure captures i
    });
  }
}

// Closure in Module Pattern
const userModule = (() => {
  const users = []; // Private
  
  return {
    addUser(name) {
      users.push(name);
    },
    getUsers() {
      return [...users]; // Return copy
    }
  };
})();
```

### Q2: Explain the Event Loop, Microtask Queue, and Macrotask Queue.

**A:** The Event Loop manages JavaScript execution, callbacks, and browser tasks.

```javascript
// Execution Order:
// 1. Synchronous code
// 2. Microtasks (Promises, queueMicrotask)
// 3. Macrotasks (setTimeout, setInterval)

console.log('1. Start');

setTimeout(() => {
  console.log('2. setTimeout (macrotask)');
}, 0);

Promise.resolve()
  .then(() => {
    console.log('3. Promise (microtask)');
  });

queueMicrotask(() => {
  console.log('4. queueMicrotask (microtask)');
});

console.log('5. End');

/* Output:
1. Start
5. End
3. Promise (microtask)
4. queueMicrotask (microtask)
2. setTimeout (macrotask)
*/

// Practical: Understanding async/await
async function example() {
  console.log('A');  // Synchronous
  
  await Promise.resolve();
  console.log('B');  // Microtask
}

example();
console.log('C');   // Synchronous

/* Output:
A
C
B
*/

// Complex Example
console.log('Start');

setTimeout(() => console.log('Timeout 1'), 0);
setTimeout(() => console.log('Timeout 2'), 0);

Promise.resolve()
  .then(() => {
    console.log('Promise 1');
    setTimeout(() => console.log('Timeout 3'), 0);
  })
  .then(() => console.log('Promise 2'));

queueMicrotask(() => {
  console.log('Microtask');
});

console.log('End');

/* Output:
Start
End
Promise 1
Microtask
Promise 2
Timeout 1
Timeout 2
Timeout 3
*/
```

### Q3: Explain Promises vs async/await and error handling strategies.

**A:** Both manage asynchronous operations; async/await is syntactic sugar over Promises.

```javascript
// Promise-based
function fetchUser(id) {
  return fetch(`/api/user/${id}`)
    .then(res => res.json())
    .then(user => ({ user, success: true }))
    .catch(err => ({ error: err.message, success: false }));
}

// Async/await equivalent
async function fetchUserAsync(id) {
  try {
    const res = await fetch(`/api/user/${id}`);
    const user = await res.json();
    return { user, success: true };
  } catch (err) {
    return { error: err.message, success: false };
  }
}

// Promise.all with error handling
Promise.all([
  fetchUser(1),
  fetchUser(2),
  fetchUser(3)
])
  .then(users => console.log(users))
  .catch(err => console.log('One failed:', err));

// Promise.allSettled (handles failures gracefully)
Promise.allSettled([
  fetchUser(1),
  fetchUser(2),
  fetchUser(3)
])
  .then(results => {
    results.forEach((result, index) => {
      if (result.status === 'fulfilled') {
        console.log(`User ${index}:`, result.value);
      } else {
        console.log(`User ${index} failed:`, result.reason);
      }
    });
  });

// Async/await with Promise.all
async function fetchMultipleUsers() {
  try {
    const users = await Promise.all([
      fetchUserAsync(1),
      fetchUserAsync(2)
    ]);
    return users;
  } catch (err) {
    console.error('Error:', err);
    throw err;
  }
}

// Parallel vs Sequential
// Parallel: faster
const results = await Promise.all([
  fetch(url1).then(r => r.json()),
  fetch(url2).then(r => r.json())
]);

// Sequential: one depends on other
const user = await fetchUserAsync(1);
const posts = await fetchUserPosts(user.id);
```

### Q4: Explain Prototypal Inheritance and the Prototype Chain.

**A:** JavaScript uses prototype-based inheritance; every object has a prototype.

```javascript
// Constructor Function Pattern
function Person(name, age) {
  this.name = name;
  this.age = age;
}

Person.prototype.greet = function() {
  return `Hello, I'm ${this.name}`;
};

const john = new Person('John', 30);
console.log(john.greet()); // "Hello, I'm John"

// Prototype Chain
console.log(john.__proto__ === Person.prototype);        // true
console.log(Person.prototype.__proto__ === Object.prototype); // true
console.log(Object.prototype.__proto__);                 // null (end of chain)

// Class syntax (syntactic sugar over prototypes)
class PersonClass {
  constructor(name, age) {
    this.name = name;
    this.age = age;
  }
  
  greet() {
    return `Hello, I'm ${this.name}`;
  }
}

// Inheritance
class Employee extends PersonClass {
  constructor(name, age, department) {
    super(name, age);
    this.department = department;
  }
  
  work() {
    return `${this.name} works in ${this.department}`;
  }
}

const jane = new Employee('Jane', 28, 'Engineering');
console.log(jane.greet());  // Inherits from PersonClass
console.log(jane.work());   // Own method

// Object.create pattern
const personProto = {
  greet() { return `Hello, I'm ${this.name}`; }
};

const bob = Object.create(personProto);
bob.name = 'Bob';

// Check inheritance
console.log(Object.getPrototypeOf(bob) === personProto); // true
```

### Q5: Explain Proxy and Reflect APIs.

**A:** Proxy intercepts operations on objects; Reflect mirrors object operations.

```javascript
// Basic Proxy
const user = { name: 'John', age: 30 };

const handler = {
  get(target, property) {
    console.log(`Accessing ${property}`);
    return target[property];
  },
  
  set(target, property, value) {
    console.log(`Setting ${property} to ${value}`);
    if (property === 'age' && value < 0) {
      throw new Error('Age cannot be negative');
    }
    target[property] = value;
    return true;
  }
};

const userProxy = new Proxy(user, handler);
console.log(userProxy.name);  // Logs "Accessing name"
userProxy.age = 31;           // Logs "Setting age to 31"

// Validation Handler
function createValidated(target, validator) {
  return new Proxy(target, {
    set(obj, prop, value) {
      if (validator[prop]) {
        validator[prop](value);
      }
      obj[prop] = value;
      return true;
    }
  });
}

const product = createValidated(
  { name: '', price: 0 },
  {
    name(value) {
      if (typeof value !== 'string') throw new Error('Name must be string');
    },
    price(value) {
      if (value < 0) throw new Error('Price cannot be negative');
    }
  }
);

// Reflect - mirrors object operations
const obj = { name: 'John', age: 30 };

Reflect.get(obj, 'name');        // 'John'
Reflect.set(obj, 'name', 'Jane'); // true
Reflect.has(obj, 'age');         // true
Reflect.deleteProperty(obj, 'age'); // true
Reflect.ownKeys(obj);            // ['name']

// Proxy with Reflect
const handler2 = {
  get(target, prop, receiver) {
    console.log(`Getting ${prop}`);
    return Reflect.get(target, prop, receiver);
  },
  
  set(target, prop, value, receiver) {
    console.log(`Setting ${prop}`);
    return Reflect.set(target, prop, value, receiver);
  }
};

const proxy = new Proxy(obj, handler2);
```

### Q6: Explain Generators, Iterators, and async/await implementation details.

**A:** Generators provide pausable functions; Iterators define iteration protocol.

```javascript
// Generator Function
function* counterGenerator() {
  yield 1;
  yield 2;
  yield 3;
}

const gen = counterGenerator();
console.log(gen.next()); // { value: 1, done: false }
console.log(gen.next()); // { value: 2, done: false }
console.log(gen.next()); // { value: 3, done: false }
console.log(gen.next()); // { value: undefined, done: true }

// Generator with loops
function* infiniteCounter() {
  let count = 0;
  while (true) {
    yield count++;
  }
}

const counter = infiniteCounter();
console.log(counter.next().value); // 0
console.log(counter.next().value); // 1

// Custom Iterator
const obj = {
  [Symbol.iterator]: function* () {
    yield 1;
    yield 2;
    yield 3;
  }
};

for (const value of obj) {
  console.log(value); // 1, 2, 3
}

// Generator with two-way communication
function* echo() {
  const value = yield 'Enter value';
  console.log(value);
}

const e = echo();
e.next();        // { value: 'Enter value', done: false }
e.next('Hello'); // logs 'Hello'

// Async/await is built on Promises and Generators
async function fetchData() {
  try {
    const response = await fetch('/api/data');
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(error);
  }
}

// Equivalent to Promise pattern:
function fetchDataPromise() {
  return fetch('/api/data')
    .then(response => response.json())
    .catch(error => console.error(error));
}
```

### Q7: Explain Memory Management, Garbage Collection, and WeakMap/WeakSet.

**A:** JavaScript manages memory; understanding GC prevents leaks.

```javascript
// Memory Leak: Circular Reference
class Node {
  constructor() {
    this.data = new Array(1000000); // Large data
    this.next = null;
  }
}

const node1 = new Node();
const node2 = new Node();
node1.next = node2;
node2.next = node1; // Circular reference - may cause memory leak

// Solution: WeakMap/WeakSet
const cache = new WeakMap();
const processed = new WeakSet();

function processData(obj) {
  if (processed.has(obj)) {
    return cache.get(obj);
  }
  
  const result = /* expensive computation */ {};
  cache.set(obj, result);
  processed.add(obj);
  return result;
}

const myObj = { name: 'test' };
processData(myObj);

// When myObj is garbage collected, WeakMap/WeakSet entries are freed

// Identifying Memory Leaks
let largeArray = [];

function leaky() {
  const hugeData = new Array(1000000);
  largeArray.push(hugeData); // Data never freed
}

// Better approach
function notLeaky() {
  const hugeData = new Array(1000000);
  return hugeData; // Freed after function ends
}

// Event Listener Memory Leak
const btn = document.getElementById('btn');

btn.addEventListener('click', function handler() {
  console.log('clicked');
});

// Memory leak: listener not removed when btn removed from DOM
// Solution:
btn.removeEventListener('click', handler);

// AbortController for cleanup
const controller = new AbortController();

fetch('/api/data', { signal: controller.signal })
  .then(r => r.json());

// Later: cleanup
controller.abort();
```

### Q8: Explain JavaScript Design Patterns.

**A:** Design patterns solve common programming problems.

```javascript
// 1. Singleton Pattern
class Database {
  static instance = null;
  
  constructor() {
    if (Database.instance) {
      return Database.instance;
    }
    Database.instance = this;
  }
  
  connect() { /* ... */ }
}

const db1 = new Database();
const db2 = new Database();
console.log(db1 === db2); // true

// 2. Factory Pattern
class AnimalFactory {
  static createAnimal(type) {
    switch(type) {
      case 'dog': return new Dog();
      case 'cat': return new Cat();
    }
  }
}

class Dog {
  speak() { return 'Woof'; }
}

class Cat {
  speak() { return 'Meow'; }
}

// 3. Observer Pattern
class EventEmitter {
  constructor() {
    this.listeners = {};
  }
  
  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }
  
  off(event, callback) {
    this.listeners[event] = this.listeners[event]
      .filter(cb => cb !== callback);
  }
  
  emit(event, data) {
    this.listeners[event]?.forEach(cb => cb(data));
  }
}

const emitter = new EventEmitter();
emitter.on('update', (data) => console.log(data));
emitter.emit('update', { message: 'Hello' });

// 4. Strategy Pattern
class PaymentProcessor {
  constructor(strategy) {
    this.strategy = strategy;
  }
  
  process(amount) {
    return this.strategy.pay(amount);
  }
}

class CreditCardStrategy {
  pay(amount) { /* ... */ }
}

class PayPalStrategy {
  pay(amount) { /* ... */ }
}

// 5. Decorator Pattern
function logDecorator(fn) {
  return function(...args) {
    console.log(`Calling ${fn.name}`, args);
    return fn(...args);
  };
}

const add = (a, b) => a + b;
const loggedAdd = logDecorator(add);
```

---

## PYTHON ADVANCED CONCEPTS

### Q1: Explain Python Decorators and their use cases.

**A:** Decorators modify function/class behavior without changing source code.

```python
# Basic Decorator
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Finished {func.__name__}")
        return result
    return wrapper

@my_decorator
def greet(name):
    print(f"Hello, {name}")

greet("John")
# Output:
# Calling greet
# Hello, John
# Finished greet

# Decorator with Arguments
def repeat(times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            results = []
            for _ in range(times):
                results.append(func(*args, **kwargs))
            return results
        return wrapper
    return decorator

@repeat(3)
def say_hello():
    return "Hello!"

print(say_hello())  # ['Hello!', 'Hello!', 'Hello!']

# Practical: Timing Decorator
import functools
import time

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end-start:.2f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)

# Class Decorator
def add_repr(cls):
    def __repr__(self):
        attrs = ', '.join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"{cls.__name__}({attrs})"
    cls.__repr__ = __repr__
    return cls

@add_repr
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

person = Person("John", 30)
print(person)  # Person(name=John, age=30)

# Property Decorator
class Circle:
    def __init__(self, radius):
        self._radius = radius
    
    @property
    def radius(self):
        return self._radius
    
    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Radius must be positive")
        self._radius = value
    
    @property
    def area(self):
        return 3.14159 * self._radius ** 2

circle = Circle(5)
print(circle.area)   # 78.53975
circle.radius = 10   # Uses setter
```

### Q2: Explain Context Managers and the `with` statement.

**A:** Context managers handle resource setup/cleanup automatically.

```python
# Basic Context Manager
class FileManager:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        if exc_type:
            print(f"Exception occurred: {exc_type}")
        return False  # Don't suppress exceptions

with FileManager("test.txt", "w") as f:
    f.write("Hello, World!")

# Using contextlib decorator
from contextlib import contextmanager

@contextmanager
def database_connection(connection_string):
    conn = create_connection(connection_string)
    try:
        yield conn
    finally:
        conn.close()

with database_connection("postgres://localhost") as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")

# Practical: Timer Context Manager
import time

@contextmanager
def timer(name):
    start = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start
        print(f"{name} took {elapsed:.2f}s")

with timer("database query"):
    # Simulate query
    time.sleep(1)

# Multiple Context Managers
from contextlib import ExitStack

with ExitStack() as stack:
    file1 = stack.enter_context(open("file1.txt"))
    file2 = stack.enter_context(open("file2.txt"))
    # Both files closed automatically

# Generator Context Manager
@contextmanager
def temporary_attribute(obj, name, value):
    old_value = getattr(obj, name, None)
    setattr(obj, name, value)
    try:
        yield
    finally:
        if old_value is None:
            delattr(obj, name)
        else:
            setattr(obj, name, old_value)
```

### Q3: Explain Python Generators, Iterators, and the iteration protocol.

**A:** Generators produce values lazily; Iterators define the iteration protocol.

```python
# Generator Function
def simple_generator():
    yield 1
    yield 2
    yield 3

gen = simple_generator()
print(next(gen))  # 1
print(next(gen))  # 2
print(next(gen))  # 3
# next(gen)  # StopIteration

# Generator Expression
numbers = (x**2 for x in range(5))  # Generator, not list
print(list(numbers))  # [0, 1, 4, 9, 16]

# Infinite Generator
def infinite_counter():
    count = 0
    while True:
        yield count
        count += 1

counter = infinite_counter()
print(next(counter))  # 0
print(next(counter))  # 1

# Generator with Two-way Communication
def echo():
    while True:
        value = yield
        print(f"Received: {value}")

gen = echo()
next(gen)  # Prime the generator
gen.send("Hello")  # Output: Received: Hello

# Custom Iterator
class Countdown:
    def __init__(self, n):
        self.n = n
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.n == 0:
            raise StopIteration
        self.n -= 1
        return self.n + 1

for num in Countdown(3):
    print(num)  # 3, 2, 1

# Lazy Evaluation
def read_large_file(file_path):
    with open(file_path) as f:
        for line in f:
            yield line.strip()

# Reads one line at a time, not entire file
for line in read_large_file("huge_file.txt"):
    process(line)

# Chaining Generators
def squares(numbers):
    for n in numbers:
        yield n ** 2

def evens(numbers):
    for n in numbers:
        if n % 2 == 0:
            yield n

result = evens(squares(range(10)))
print(list(result))  # [0, 4, 16, 36, 64]
```

### Q4: Explain Python Metaclasses.

**A:** Metaclasses are "classes of classes"; they control class creation.

```python
# Basic Metaclass
class Meta(type):
    def __new__(mcs, name, bases, namespace):
        print(f"Creating class {name}")
        namespace['custom_attr'] = True
        return super().__new__(mcs, name, bases, namespace)

class MyClass(metaclass=Meta):
    pass

print(hasattr(MyClass, 'custom_attr'))  # True

# Metaclass for Property Enforcement
class PropertyMeta(type):
    def __new__(mcs, name, bases, namespace):
        for key, value in namespace.items():
            if isinstance(value, property):
                print(f"Property {key} defined in {name}")
        return super().__new__(mcs, name, bases, namespace)

class User(metaclass=PropertyMeta):
    def __init__(self, name):
        self._name = name
    
    @property
    def name(self):
        return self._name

# Metaclass for Singleton Pattern
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
print(db1 is db2)  # True

# Metaclass for ORM-like Behavior
class FieldDescriptor:
    def __init__(self, name, field_type):
        self.name = name
        self.field_type = field_type
    
    def __get__(self, obj, objtype):
        return obj.__dict__.get(self.name)
    
    def __set__(self, obj, value):
        if not isinstance(value, self.field_type):
            raise TypeError(f"{self.name} must be {self.field_type}")
        obj.__dict__[self.name] = value

class ModelMeta(type):
    def __new__(mcs, name, bases, namespace):
        fields = {}
        for key, value in list(namespace.items()):
            if isinstance(value, tuple) and len(value) == 2:
                field_type = value[0]
                fields[key] = FieldDescriptor(key, field_type)
        
        namespace['_fields'] = fields
        namespace.update(fields)
        return super().__new__(mcs, name, bases, namespace)

class Model(metaclass=ModelMeta):
    pass

class User(Model):
    name = (str, "")
    age = (int, 0)

user = User()
user.name = "John"
user.age = 30
# user.age = "invalid"  # TypeError
```

### Q5: Explain Python Async/Await and asyncio.

**A:** Async/await enables concurrent I/O operations efficiently.

```python
import asyncio

# Basic async function
async def fetch_data(url):
    print(f"Fetching {url}")
    await asyncio.sleep(1)  # Simulate API call
    print(f"Completed {url}")
    return {"url": url, "data": "example"}

# Run single coroutine
result = asyncio.run(fetch_data("http://example.com"))

# Concurrent execution with gather
async def main():
    results = await asyncio.gather(
        fetch_data("http://example.com/1"),
        fetch_data("http://example.com/2"),
        fetch_data("http://example.com/3")
    )
    return results

results = asyncio.run(main())

# Task management
async def with_timeout():
    try:
        result = await asyncio.wait_for(
            fetch_data("http://slow.com"),
            timeout=2.0
        )
    except asyncio.TimeoutError:
        print("Request timed out")

# Async context managers
class AsyncResource:
    async def __aenter__(self):
        print("Acquiring resource")
        await asyncio.sleep(0.5)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("Releasing resource")
        await asyncio.sleep(0.5)

async def use_resource():
    async with AsyncResource() as res:
        print("Using resource")

# Async iterator
class AsyncCounter:
    def __init__(self, n):
        self.n = n
        self.i = 0
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.i >= self.n:
            raise StopAsyncIteration
        self.i += 1
        await asyncio.sleep(0.1)
        return self.i

async def iterate():
    async for num in AsyncCounter(5):
        print(num)

# Producer-Consumer Pattern
async def producer(queue):
    for i in range(5):
        await queue.put(f"item-{i}")
        await asyncio.sleep(0.1)

async def consumer(queue):
    while True:
        item = await queue.get()
        print(f"Processing {item}")
        queue.task_done()

async def producer_consumer():
    queue = asyncio.Queue()
    await asyncio.gather(
        producer(queue),
        consumer(queue)
    )
```

### Q6: Explain Python Type Hints and mypy.

**A:** Type hints improve code clarity and catch errors early.

```python
# Basic Type Hints
def add(a: int, b: int) -> int:
    return a + b

def greet(name: str) -> None:
    print(f"Hello, {name}")

# Complex Types
from typing import List, Dict, Tuple, Optional, Union, Callable

def process_data(
    items: List[int],
    mapping: Dict[str, int],
    callback: Callable[[int], str]
) -> Optional[str]:
    if not items:
        return None
    return callback(items[0])

# Generic Types
from typing import TypeVar, Generic

T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self):
        self.items: List[T] = []
    
    def push(self, item: T) -> None:
        self.items.append(item)
    
    def pop(self) -> T:
        return self.items.pop()

stack: Stack[int] = Stack()
stack.push(1)

# Type Aliases
UserId = int
UserName = str
User = Dict[str, Union[UserId, UserName]]

def get_user(user_id: UserId) -> User:
    return {"id": user_id, "name": "John"}

# Protocol (structural typing)
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:
    def draw(self) -> None:
        print("Drawing circle")

class Square:
    def draw(self) -> None:
        print("Drawing square")

def render(shape: Drawable) -> None:
    shape.draw()

# mypy verification
# Save as example.py and run: mypy example.py
def safe_add(a: int, b: int) -> int:
    return a + b

result: int = safe_add(5, 3)  # OK
# result: int = safe_add(5, "3")  # mypy error!
```

### Q7: Explain Python GIL (Global Interpreter Lock) and its implications.

**A:** GIL prevents multiple threads from executing Python code simultaneously.

```python
import threading
import time

# GIL impact on CPU-bound tasks
def cpu_bound():
    total = 0
    for i in range(100_000_000):
        total += i
    return total

# Single-threaded
start = time.time()
cpu_bound()
print(f"Single thread: {time.time() - start:.2f}s")

# Multi-threaded (slower due to GIL)
start = time.time()
t1 = threading.Thread(target=cpu_bound)
t2 = threading.Thread(target=cpu_bound)
t1.start()
t2.start()
t1.join()
t2.join()
print(f"Two threads: {time.time() - start:.2f}s")

# I/O-bound tasks benefit from threading
def io_bound():
    time.sleep(1)  # Simulate I/O

start = time.time()
threads = [threading.Thread(target=io_bound) for _ in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(f"5 I/O threads: {time.time() - start:.2f}s")

# Alternatives to GIL
# 1. multiprocessing for CPU-bound
from multiprocessing import Process

processes = [Process(target=cpu_bound) for _ in range(2)]
for p in processes:
    p.start()
for p in processes:
    p.join()

# 2. asyncio for I/O-bound
import asyncio

async def async_io_bound():
    await asyncio.sleep(1)

async def run_async():
    await asyncio.gather(*[async_io_bound() for _ in range(5)])

# asyncio.run(run_async())
```

### Q8: Explain Python Design Patterns.

**A:** Design patterns provide solutions to common problems.

```python
# Singleton Pattern
class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

db1 = Database()
db2 = Database()
assert db1 is db2

# Factory Pattern
class AnimalFactory:
    @staticmethod
    def create_animal(animal_type):
        if animal_type == "dog":
            return Dog()
        elif animal_type == "cat":
            return Cat()

class Dog:
    def speak(self):
        return "Woof"

class Cat:
    def speak(self):
        return "Meow"

# Observer Pattern
class Subject:
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def detach(self, observer):
        self._observers.remove(observer)
    
    def notify(self, event):
        for observer in self._observers:
            observer.update(event)

class Observer:
    def update(self, event):
        print(f"Observer received: {event}")

# Strategy Pattern
class PaymentStrategy:
    def pay(self, amount):
        raise NotImplementedError

class CreditCardPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"Paying ${amount} with credit card")

class PayPalPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"Paying ${amount} with PayPal")

class Checkout:
    def __init__(self, strategy: PaymentStrategy):
        self.strategy = strategy
    
    def process(self, amount):
        self.strategy.pay(amount)

# Decorator Pattern
def log_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Finished {func.__name__}")
        return result
    return wrapper

@log_decorator
def process_order(order_id):
    print(f"Processing order {order_id}")
```

---

## SUMMARY & KEY TAKEAWAYS

### HTML
- Semantic HTML improves accessibility and SEO
- Web Components enable reusable encapsulated elements
- ARIA makes dynamic content accessible
- Data attributes store custom application data

### CSS
- Grid for 2D layouts, Flexbox for 1D layouts
- Custom properties enable dynamic theming
- Stacking context controls layering
- Performance optimization through containment

### JavaScript
- Closures enable data privacy and factory patterns
- Event Loop/Microtask queue understand async behavior
- Promises and async/await manage asynchronous code
- Prototypal inheritance powers JavaScript's flexibility
- Proxy/Reflect enable metaprogramming
- Generators provide lazy evaluation
- Memory management prevents leaks

### Python
- Decorators modify behavior without changing code
- Context managers handle resource cleanup
- Generators provide memory-efficient iteration
- Metaclasses control class creation
- Async/await enables concurrent I/O
- Type hints improve code quality
- GIL impacts multithreading performance
- Design patterns solve recurring problems

---

**Last Updated:** 2024
**For Developers:** 7+ Years Experience
**Difficulty Level:** Advanced
