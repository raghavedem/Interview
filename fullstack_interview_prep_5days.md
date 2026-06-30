# 🚀 Full Stack Developer Interview Preparation Guide
### 5-Year Experience Level | React · JavaScript · FastAPI · PostgreSQL · Redis · Advanced Architecture

> **How to use this guide:** This single document covers the 80/20 of everything asked in senior full-stack interviews. Each day builds on the previous. Code examples are production-grade — understand the *why*, not just the *what*.

---

## 📅 Study Plan Overview

| Day | Topics | Focus |
|-----|--------|-------|
| Day 1 | JavaScript Deep Dive | Closures, Async, Event Loop, Prototypes, ES6+ |
| Day 2 | React Core + Hooks | State, Lifecycle, Performance, Patterns |
| Day 3 | FastAPI + Python | Routing, Auth, Dependency Injection, Async |
| Day 4 | PostgreSQL + Redis | Queries, Indexing, Caching, Transactions |
| Day 5 | Advanced Architecture | System Design, Performance, Security, DevOps |

---

# DAY 1: JavaScript Deep Dive

## 1.1 The Event Loop (Most Asked Topic)

JavaScript is **single-threaded** but handles concurrency via the Event Loop.

```
Call Stack → Web APIs → Callback Queue → Microtask Queue → Event Loop
```

**Execution Order:**
1. Synchronous code (Call Stack)
2. Microtasks (Promise `.then`, `queueMicrotask`, `MutationObserver`)
3. Macrotasks (setTimeout, setInterval, I/O)

```javascript
console.log('1');                          // Sync → runs first

setTimeout(() => console.log('2'), 0);    // Macrotask → runs last

Promise.resolve().then(() => {
  console.log('3');                        // Microtask → runs before macrotask
  Promise.resolve().then(() => console.log('4')); // Nested microtask → still before macrotask
});

console.log('5');                          // Sync → runs second

// Output: 1, 5, 3, 4, 2
```

**Why this matters:** Understanding this prevents bugs with async state updates in React and explains why `setTimeout(fn, 0)` doesn't always run "immediately."

---

## 1.2 Closures (Core Concept)

A closure is a function that **retains access to its lexical scope** even when executed outside that scope.

```javascript
// Classic interview trap
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 100); // Prints: 3, 3, 3 (var is function-scoped)
}

// Fix 1: Use let (block-scoped)
for (let i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 100); // Prints: 0, 1, 2
}

// Fix 2: IIFE closure
for (var i = 0; i < 3; i++) {
  ((j) => setTimeout(() => console.log(j), 100))(i);
}
```

**Real-world closure: Module Pattern**
```javascript
const counter = (() => {
  let count = 0; // Private state

  return {
    increment: () => ++count,
    decrement: () => --count,
    getCount: () => count,
  };
})();

counter.increment(); // 1
counter.increment(); // 2
counter.getCount();  // 2
// count is not accessible from outside — true encapsulation
```

**Closure in React (common bug)**
```javascript
// ❌ Stale closure bug
function Timer() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setCount(count + 1); // 'count' is captured at 0, always sets to 1!
    }, 1000);
    return () => clearInterval(id);
  }, []); // Empty deps = stale closure
}

// ✅ Fix: Use functional update form
useEffect(() => {
  const id = setInterval(() => {
    setCount(prev => prev + 1); // Always uses latest value
  }, 1000);
  return () => clearInterval(id);
}, []);
```

---

## 1.3 Prototypal Inheritance

JavaScript uses **prototype chains**, not classical inheritance.

```javascript
// Every object has __proto__ pointing to its prototype
const animal = {
  breathe() { return 'breathing'; }
};

const dog = Object.create(animal);
dog.bark = () => 'woof';

dog.bark();     // 'woof' — own property
dog.breathe();  // 'breathing' — found on prototype chain
dog.toString(); // Found on Object.prototype

// Property lookup chain:
// dog → animal → Object.prototype → null
```

**ES6 Class (syntactic sugar over prototypes)**
```javascript
class Animal {
  constructor(name) {
    this.name = name;
  }
  speak() {
    return `${this.name} makes a sound`;
  }
}

class Dog extends Animal {
  constructor(name) {
    super(name); // Calls Animal constructor
  }
  speak() {
    return `${this.name} barks`; // Overrides parent
  }
}

const d = new Dog('Rex');
d.speak();              // "Rex barks"
d instanceof Dog;       // true
d instanceof Animal;    // true — prototype chain
Object.getPrototypeOf(Dog.prototype) === Animal.prototype; // true
```

**`this` context (most confusing JS topic)**
```javascript
const obj = {
  name: 'Alice',
  greet() { return `Hi, I'm ${this.name}`; },
  greetArrow: () => `Hi, I'm ${this.name}` // Arrow has no own 'this'
};

obj.greet();          // "Hi, I'm Alice"
obj.greetArrow();     // "Hi, I'm undefined" — 'this' is window/undefined

const fn = obj.greet;
fn();                 // "Hi, I'm undefined" — lost context

// Fix: bind
const bound = obj.greet.bind(obj);
bound(); // "Hi, I'm Alice"

// call/apply: immediate invocation with context
obj.greet.call({ name: 'Bob' });   // "Hi, I'm Bob"
obj.greet.apply({ name: 'Carol' }); // "Hi, I'm Carol"
```

---

## 1.4 Async/Await & Promises

**Promise states:** Pending → Fulfilled | Rejected

```javascript
// Creating promises
const fetchUser = (id) => new Promise((resolve, reject) => {
  if (id <= 0) reject(new Error('Invalid ID'));
  else resolve({ id, name: 'Alice' });
});

// Chaining
fetchUser(1)
  .then(user => user.name.toUpperCase())
  .then(name => console.log(name))
  .catch(err => console.error(err))
  .finally(() => console.log('Done'));

// Async/Await (cleaner syntax)
async function getUser(id) {
  try {
    const user = await fetchUser(id);
    return user.name.toUpperCase();
  } catch (err) {
    console.error(err);
    throw err; // Re-throw to caller
  }
}
```

**Promise combinators — critical for interviews**
```javascript
const p1 = fetch('/api/user');
const p2 = fetch('/api/posts');
const p3 = fetch('/api/comments');

// Promise.all — ALL must succeed, fails fast on any rejection
const [user, posts, comments] = await Promise.all([p1, p2, p3]);

// Promise.allSettled — waits for ALL, returns status of each
const results = await Promise.allSettled([p1, p2, p3]);
results.forEach(r => {
  if (r.status === 'fulfilled') console.log(r.value);
  else console.error(r.reason);
});

// Promise.race — resolves/rejects as soon as first settles
const result = await Promise.race([p1, p2, p3]); // Fastest wins

// Promise.any — resolves on first success, rejects if ALL fail (AggregateError)
const firstSuccess = await Promise.any([p1, p2, p3]);
```

**Sequential vs Parallel Async**
```javascript
// ❌ Sequential (slow — waits for each)
const user = await fetchUser(1);    // 100ms
const posts = await fetchPosts(1);  // 100ms
// Total: 200ms

// ✅ Parallel (fast — concurrent)
const [user, posts] = await Promise.all([fetchUser(1), fetchPosts(1)]);
// Total: ~100ms

// ✅ Parallel with for loop using map
const userIds = [1, 2, 3];
const users = await Promise.all(userIds.map(id => fetchUser(id)));
```

---

## 1.5 Destructuring, Spread & Rest

```javascript
// Array destructuring
const [first, second, ...rest] = [1, 2, 3, 4, 5];
// first=1, second=2, rest=[3,4,5]

// Object destructuring with rename and default
const { name: userName = 'Guest', age = 18 } = { name: 'Alice' };
// userName='Alice', age=18

// Nested destructuring
const { user: { profile: { avatar } } } = data;

// Function params destructuring
function render({ title, children, className = '' }) {
  return `<div class="${className}"><h1>${title}</h1>${children}</div>`;
}

// Spread operator
const arr1 = [1, 2, 3];
const arr2 = [...arr1, 4, 5]; // [1, 2, 3, 4, 5]

const obj1 = { a: 1, b: 2 };
const obj2 = { ...obj1, c: 3, b: 99 }; // b is overridden: { a:1, b:99, c:3 }

// Shallow vs Deep copy
const shallow = { ...obj1 };        // Shallow — nested objects are referenced
const deep = JSON.parse(JSON.stringify(obj1)); // Deep — but loses functions/dates
```

---

## 1.6 Higher-Order Functions (80/20 Staples)

```javascript
const products = [
  { id: 1, name: 'Laptop', price: 999, category: 'Electronics', inStock: true },
  { id: 2, name: 'Shirt', price: 29, category: 'Clothing', inStock: false },
  { id: 3, name: 'Phone', price: 699, category: 'Electronics', inStock: true },
];

// map — transform each element
const names = products.map(p => p.name); // ['Laptop', 'Shirt', 'Phone']

// filter — subset
const inStock = products.filter(p => p.inStock); // Laptop, Phone

// reduce — accumulate to single value
const totalValue = products.reduce((sum, p) => sum + p.price, 0); // 1727

// find — first match (returns element or undefined)
const laptop = products.find(p => p.name === 'Laptop');

// findIndex — first match index
const idx = products.findIndex(p => p.id === 2);

// some/every — boolean checks
const hasExpensive = products.some(p => p.price > 500);   // true
const allInStock = products.every(p => p.inStock);         // false

// sort (mutates!) — always return copy first
const sorted = [...products].sort((a, b) => a.price - b.price); // ascending

// Chaining
const result = products
  .filter(p => p.inStock && p.category === 'Electronics')
  .map(p => ({ ...p, discounted: p.price * 0.9 }))
  .sort((a, b) => a.discounted - b.discounted);
```

---

## 1.7 Currying & Function Composition

```javascript
// Currying — converting multi-arg function into chain of single-arg functions
const multiply = (a) => (b) => a * b;
const double = multiply(2);   // Partially applied
double(5);  // 10
double(10); // 20

// Practical currying
const withTax = (rate) => (price) => price * (1 + rate);
const withGST = withTax(0.18);
withGST(100); // 118

// Function composition
const compose = (...fns) => (x) => fns.reduceRight((v, f) => f(v), x);
const pipe = (...fns) => (x) => fns.reduce((v, f) => f(v), x);

const trim = s => s.trim();
const toLowerCase = s => s.toLowerCase();
const removeSpaces = s => s.replace(/\s+/g, '-');

const slugify = pipe(trim, toLowerCase, removeSpaces);
slugify('  Hello World  '); // 'hello-world'
```

---

## 1.8 JavaScript Memory & Performance

```javascript
// WeakMap/WeakSet — don't prevent garbage collection
const cache = new WeakMap();

function processUser(user) {
  if (cache.has(user)) return cache.get(user);
  const result = heavyComputation(user);
  cache.set(user, result); // Cleared when 'user' is garbage collected
  return result;
}

// Memory leak patterns to avoid
// 1. Global variables
window.leaky = { data: massiveArray }; // Never GC'd

// 2. Detached DOM nodes
let node = document.createElement('div');
document.body.appendChild(node);
document.body.removeChild(node);
// If 'node' variable still references it, it won't be GC'd

// 3. Forgotten event listeners
const handler = () => console.log('click');
button.addEventListener('click', handler);
// Always remove when done:
button.removeEventListener('click', handler);
// Or use AbortController
const controller = new AbortController();
button.addEventListener('click', handler, { signal: controller.signal });
controller.abort(); // Removes all listeners attached to this controller
```

---

## 1.9 ES2020+ Features (Must Know)

```javascript
// Optional chaining (?.)
const city = user?.address?.city ?? 'Unknown';

// Nullish coalescing (??) — only null/undefined, not falsy
const port = config.port ?? 3000; // 0 is valid, '' is valid

// Logical assignment
user.name ??= 'Guest';    // Assign if null/undefined
user.active ||= true;     // Assign if falsy
user.count &&= user.count + 1; // Assign if truthy

// Object.fromEntries (reverse of Object.entries)
const entries = [['a', 1], ['b', 2]];
const obj = Object.fromEntries(entries); // { a: 1, b: 2 }

// Useful pattern: transform object values
const prices = { laptop: 1000, phone: 700 };
const discounted = Object.fromEntries(
  Object.entries(prices).map(([k, v]) => [k, v * 0.9])
); // { laptop: 900, phone: 630 }

// Array.at() — access from end
const arr = [1, 2, 3, 4, 5];
arr.at(-1); // 5 (last element)
arr.at(-2); // 4

// structuredClone — true deep clone (replaces JSON parse/stringify)
const original = { date: new Date(), arr: [1, 2, 3] };
const clone = structuredClone(original); // Preserves Date, handles circular refs

// Promise.any
const result = await Promise.any([rejectingPromise, resolvingPromise]);
// Returns first fulfilled value, unlike Promise.race
```

---

## 1.10 Design Patterns in JavaScript

```javascript
// Singleton
class Database {
  static #instance = null;

  constructor(config) {
    if (Database.#instance) return Database.#instance;
    this.connection = connect(config);
    Database.#instance = this;
  }

  static getInstance(config) {
    return Database.#instance || new Database(config);
  }
}

// Observer Pattern (EventEmitter)
class EventEmitter {
  #listeners = new Map();

  on(event, callback) {
    if (!this.#listeners.has(event)) this.#listeners.set(event, []);
    this.#listeners.get(event).push(callback);
    return () => this.off(event, callback); // Return unsubscribe fn
  }

  emit(event, ...args) {
    this.#listeners.get(event)?.forEach(fn => fn(...args));
  }

  off(event, callback) {
    const fns = this.#listeners.get(event) || [];
    this.#listeners.set(event, fns.filter(fn => fn !== callback));
  }
}

// Factory Pattern
class NotificationFactory {
  static create(type, data) {
    const types = { email: EmailNotification, sms: SMSNotification, push: PushNotification };
    if (!types[type]) throw new Error(`Unknown notification type: ${type}`);
    return new types[type](data);
  }
}

// Strategy Pattern
const sortStrategies = {
  bubble: arr => { /* bubble sort */ },
  quick: arr => { /* quick sort */ },
  merge: arr => { /* merge sort */ },
};

function sort(arr, strategy = 'quick') {
  return sortStrategies[strategy](arr);
}
```

---

# DAY 2: React Core + Hooks

## 2.1 React Rendering & Virtual DOM

React uses a **Virtual DOM** — a JS representation of the real DOM. It diffs (reconciles) the virtual DOM tree on each render and only updates what changed.

```
State Change → Re-render → New Virtual DOM → Diff (Fiber Reconciler) → Minimal DOM Updates
```

**Key insight:** Re-rendering doesn't mean DOM updates. React is smart about batching DOM operations.

```jsx
// React 18: automatic batching — all state updates in async code are batched
async function handleClick() {
  setCount(c => c + 1);  // ← These don't individually trigger re-renders
  setName('Alice');       // ← They're batched together
  setLoading(false);      // ← One single re-render at the end
}

// Force synchronous update (rarely needed)
import { flushSync } from 'react-dom';
flushSync(() => setCount(c => c + 1)); // Immediate DOM update
```

---

## 2.2 useState — Deep Dive

```jsx
// State update is ASYNC — don't read state immediately after setting
const [count, setCount] = useState(0);

// ❌ Bug: relies on potentially stale state
const increment = () => {
  setCount(count + 1);
  setCount(count + 1); // count is still 0 here! Result: 1, not 2
};

// ✅ Functional update: always uses latest value
const increment = () => {
  setCount(prev => prev + 1);
  setCount(prev => prev + 1); // Result: 2 ✓
};

// Lazy initialization — compute initial state once
const [data, setData] = useState(() => {
  return JSON.parse(localStorage.getItem('data')) || []; // Only runs once
});

// Object state — always spread to avoid losing other fields
const [user, setUser] = useState({ name: '', email: '', age: 0 });

const updateName = (name) => {
  setUser(prev => ({ ...prev, name })); // Merge, don't replace
};

// State initialization with prop (one-time sync)
function ProfileForm({ initialName }) {
  const [name, setName] = useState(initialName); // Synced once at mount
  // Changes to initialName prop won't update state — this is intentional
}
```

---

## 2.3 useEffect — Every Pattern You Need

```jsx
// Pattern 1: Run once on mount (componentDidMount)
useEffect(() => {
  fetchData();
}, []);

// Pattern 2: Run when dependency changes
useEffect(() => {
  fetchUserData(userId);
}, [userId]); // Re-runs only when userId changes

// Pattern 3: Cleanup (componentWillUnmount)
useEffect(() => {
  const subscription = subscribe(userId);
  return () => subscription.unsubscribe(); // Cleanup on unmount or before re-run
}, [userId]);

// Pattern 4: Async in useEffect (can't make the effect async directly)
useEffect(() => {
  let cancelled = false;

  async function load() {
    const data = await fetchUser(id);
    if (!cancelled) setUser(data); // Prevent state update if unmounted
  }

  load();
  return () => { cancelled = true; }; // Cleanup: ignore late responses
}, [id]);

// Pattern 5: Debouncing
useEffect(() => {
  const timer = setTimeout(() => {
    search(query);
  }, 300);
  return () => clearTimeout(timer); // Cancel on each keystroke, only fires after 300ms idle
}, [query]);

// Pattern 6: Event listeners
useEffect(() => {
  const handler = (e) => setKey(e.key);
  window.addEventListener('keydown', handler);
  return () => window.removeEventListener('keydown', handler);
}, []);
```

**What NOT to do with useEffect:**
```jsx
// ❌ Infinite loop — setCount triggers re-render, which runs effect, which calls setCount...
useEffect(() => {
  setCount(count + 1); // count is in effect but not in deps
}); // No dependency array = runs every render

// ❌ Missing dependency (eslint-plugin-react-hooks will warn)
useEffect(() => {
  doSomethingWith(userId); // userId used but not listed
}, []); // Stale closure!

// ✅ Suppress only when you're certain it's correct
// eslint-disable-next-line react-hooks/exhaustive-deps
```

---

## 2.4 useRef — Beyond DOM Access

```jsx
// Use 1: Access DOM elements
const inputRef = useRef(null);
<input ref={inputRef} />;
inputRef.current.focus(); // Imperative DOM access

// Use 2: Store mutable value without triggering re-render
const renderCount = useRef(0);
useEffect(() => { renderCount.current += 1; }); // Track renders without re-rendering

// Use 3: Store previous value
function usePrevious(value) {
  const ref = useRef();
  useEffect(() => { ref.current = value; }); // Update AFTER render
  return ref.current; // Returns value from BEFORE this render
}

// Use 4: Hold stable reference to callbacks (avoids stale closures)
function useEventCallback(fn) {
  const ref = useRef(fn);
  useEffect(() => { ref.current = fn; }); // Always current
  return useCallback((...args) => ref.current(...args), []); // Stable reference
}

// Use 5: Prevent initial effect run
const isFirstRender = useRef(true);
useEffect(() => {
  if (isFirstRender.current) {
    isFirstRender.current = false;
    return;
  }
  console.log('Not first render — value changed:', value);
}, [value]);
```

---

## 2.5 useMemo & useCallback — Performance

```jsx
// useMemo: memoize expensive computation result
const sortedAndFiltered = useMemo(() => {
  return products
    .filter(p => p.category === selectedCategory)
    .sort((a, b) => a.price - b.price);
}, [products, selectedCategory]); // Only recompute when these change

// useCallback: memoize function reference (for stable prop passing)
const handleDelete = useCallback((id) => {
  setItems(prev => prev.filter(item => item.id !== id));
}, []); // Empty deps = stable forever (uses functional state update)

// Why useCallback matters for child components
const List = React.memo(({ items, onDelete }) => {
  // Only re-renders if items or onDelete reference changes
  return items.map(item => (
    <Item key={item.id} item={item} onDelete={onDelete} />
  ));
});

// ❌ Without useCallback — creates new function every render
// Every render of Parent creates new onDelete → List always re-renders
<List items={items} onDelete={(id) => deleteItem(id)} />

// ✅ With useCallback — same function reference across renders
<List items={items} onDelete={handleDelete} />
```

**When NOT to memoize:**
```jsx
// ❌ Over-optimization — simple computations don't need useMemo
const doubled = useMemo(() => count * 2, [count]); // Overkill

// ❌ Primitive props don't need useCallback
<Button onClick={() => setCount(c => c + 1)} /> // Fine — primitives compare by value

// Rule of thumb: profile first, optimize second
```

---

## 2.6 useReducer — Complex State Management

```jsx
// Great for: multiple related state values, complex state transitions, state logic testing

const initialState = { count: 0, status: 'idle', error: null };

function reducer(state, action) {
  switch (action.type) {
    case 'INCREMENT':
      return { ...state, count: state.count + action.payload || 1 };
    case 'FETCH_START':
      return { ...state, status: 'loading', error: null };
    case 'FETCH_SUCCESS':
      return { ...state, status: 'success', data: action.payload };
    case 'FETCH_ERROR':
      return { ...state, status: 'error', error: action.payload };
    case 'RESET':
      return initialState;
    default:
      throw new Error(`Unknown action: ${action.type}`);
  }
}

function Counter() {
  const [state, dispatch] = useReducer(reducer, initialState);

  const fetchData = async () => {
    dispatch({ type: 'FETCH_START' });
    try {
      const data = await api.getData();
      dispatch({ type: 'FETCH_SUCCESS', payload: data });
    } catch (err) {
      dispatch({ type: 'FETCH_ERROR', payload: err.message });
    }
  };

  return (
    <div>
      {state.status === 'loading' && <Spinner />}
      {state.status === 'error' && <Error message={state.error} />}
      {state.status === 'success' && <Data data={state.data} />}
    </div>
  );
}
```

---

## 2.7 Context API — When and How

```jsx
// Good for: theme, auth user, language, low-frequency updates
// Bad for: high-frequency state (every keystroke, animation frames)

// 1. Create Context with meaningful default
const AuthContext = React.createContext({
  user: null,
  login: () => {},
  logout: () => {},
});

// 2. Provider with state
function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  const login = useCallback(async (credentials) => {
    const user = await authApi.login(credentials);
    setUser(user);
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    authApi.logout();
  }, []);

  // Memoize value to prevent unnecessary re-renders
  const value = useMemo(() => ({ user, login, logout }), [user, login, logout]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// 3. Custom hook for consuming (better DX + error boundary)
function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

// 4. Usage
function Profile() {
  const { user, logout } = useAuth();
  return <div>{user?.name} <button onClick={logout}>Logout</button></div>;
}

// Context optimization: split contexts to minimize re-renders
const UserContext = React.createContext(null);    // Changes rarely
const ThemeContext = React.createContext('light'); // Changes on toggle
// Components only re-render when their specific context changes
```

---

## 2.8 Custom Hooks — Reusable Logic

```jsx
// useFetch — data fetching with loading/error states
function useFetch(url, options = {}) {
  const [state, dispatch] = useReducer(
    (s, a) => ({ ...s, ...a }),
    { data: null, loading: true, error: null }
  );

  const stableOptions = useRef(options);

  useEffect(() => {
    let cancelled = false;
    dispatch({ loading: true, error: null });

    fetch(url, stableOptions.current)
      .then(r => r.json())
      .then(data => { if (!cancelled) dispatch({ data, loading: false }); })
      .catch(error => { if (!cancelled) dispatch({ error, loading: false }); });

    return () => { cancelled = true; };
  }, [url]);

  return state;
}

// useLocalStorage — sync state with localStorage
function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem(key)) ?? initialValue;
    } catch { return initialValue; }
  });

  const setStoredValue = useCallback((newValue) => {
    setValue(prev => {
      const resolved = typeof newValue === 'function' ? newValue(prev) : newValue;
      localStorage.setItem(key, JSON.stringify(resolved));
      return resolved;
    });
  }, [key]);

  return [value, setStoredValue];
}

// useDebounce
function useDebounce(value, delay) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debounced;
}

// useMediaQuery
function useMediaQuery(query) {
  const [matches, setMatches] = useState(
    () => window.matchMedia(query).matches
  );
  useEffect(() => {
    const mq = window.matchMedia(query);
    const handler = (e) => setMatches(e.matches);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, [query]);
  return matches;
}

// useIntersectionObserver — for infinite scroll / lazy loading
function useIntersectionObserver(ref, options = {}) {
  const [isIntersecting, setIsIntersecting] = useState(false);
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => setIsIntersecting(entry.isIntersecting),
      options
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [ref, options]);
  return isIntersecting;
}
```

---

## 2.9 React Performance Patterns

```jsx
// 1. React.memo — skip re-render if props haven't changed
const ExpensiveChild = React.memo(function Child({ data, onAction }) {
  console.log('Child rendered'); // Only logs when data or onAction actually changes
  return <div>{data.map(d => <Item key={d.id} {...d} />)}</div>;
}, (prevProps, nextProps) => {
  // Custom comparison: return true to SKIP re-render
  return prevProps.data.length === nextProps.data.length &&
         prevProps.onAction === nextProps.onAction;
});

// 2. Code splitting & lazy loading
const HeavyChart = React.lazy(() => import('./HeavyChart'));

function Dashboard() {
  return (
    <Suspense fallback={<Skeleton />}>
      <HeavyChart data={data} />
    </Suspense>
  );
}

// 3. Virtualization for long lists (react-window)
import { FixedSizeList } from 'react-window';

function VirtualList({ items }) {
  const Row = ({ index, style }) => (
    <div style={style}>{items[index].name}</div>
  );

  return (
    <FixedSizeList height={400} width={600} itemCount={items.length} itemSize={50}>
      {Row}
    </FixedSizeList>
    // Only renders ~8 visible rows regardless of list size
  );
}

// 4. Avoid creating objects/arrays inline in JSX
// ❌ Creates new object every render → breaks React.memo
<Component style={{ color: 'red' }} config={{ debug: false }} />

// ✅ Move outside component or use useMemo
const STYLE = { color: 'red' };
const CONFIG = { debug: false };
<Component style={STYLE} config={CONFIG} />
```

---

## 2.10 Error Boundaries

```jsx
// Class component (only class components can be error boundaries)
class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    logErrorToService(error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <h2>Something went wrong.</h2>;
    }
    return this.props.children;
  }
}

// Usage
<ErrorBoundary fallback={<ErrorUI />}>
  <UserProfile />
</ErrorBoundary>

// React 19 / react-error-boundary library: useErrorBoundary hook
import { ErrorBoundary, useErrorBoundary } from 'react-error-boundary';

function UserProfile() {
  const { showBoundary } = useErrorBoundary();

  const loadData = async () => {
    try {
      const data = await fetchProfile();
    } catch (err) {
      showBoundary(err); // Trigger error boundary from inside function
    }
  };
}
```

---

## 2.11 React Patterns (Interview Favorites)

```jsx
// 1. Compound Components
function Tabs({ children, defaultTab }) {
  const [active, setActive] = useState(defaultTab);
  return (
    <TabsContext.Provider value={{ active, setActive }}>
      {children}
    </TabsContext.Provider>
  );
}
Tabs.List = function TabsList({ children }) { return <div role="tablist">{children}</div>; };
Tabs.Tab = function Tab({ value, children }) {
  const { active, setActive } = useContext(TabsContext);
  return <button onClick={() => setActive(value)} aria-selected={active === value}>{children}</button>;
};
Tabs.Panel = function Panel({ value, children }) {
  const { active } = useContext(TabsContext);
  return active === value ? <div>{children}</div> : null;
};

// Usage — expressive, flexible API
<Tabs defaultTab="profile">
  <Tabs.List>
    <Tabs.Tab value="profile">Profile</Tabs.Tab>
    <Tabs.Tab value="settings">Settings</Tabs.Tab>
  </Tabs.List>
  <Tabs.Panel value="profile"><Profile /></Tabs.Panel>
  <Tabs.Panel value="settings"><Settings /></Tabs.Panel>
</Tabs>

// 2. Render Props
function MouseTracker({ render }) {
  const [pos, setPos] = useState({ x: 0, y: 0 });
  return (
    <div onMouseMove={e => setPos({ x: e.clientX, y: e.clientY })}>
      {render(pos)}
    </div>
  );
}
<MouseTracker render={pos => <span>{pos.x}, {pos.y}</span>} />

// 3. Higher-Order Components (HOC)
function withAuth(Component) {
  return function AuthenticatedComponent(props) {
    const { user } = useAuth();
    if (!user) return <Navigate to="/login" />;
    return <Component {...props} user={user} />;
  };
}
const ProtectedDashboard = withAuth(Dashboard);

// 4. Container/Presenter Pattern
// Container — handles logic
function UserListContainer() {
  const { data, loading, error } = useFetch('/api/users');
  if (loading) return <Spinner />;
  if (error) return <Error />;
  return <UserList users={data} />;
}

// Presenter — pure UI, easily testable
function UserList({ users }) {
  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}
```

---

# DAY 3: FastAPI + Python

## 3.1 FastAPI Fundamentals

FastAPI is built on **Starlette** (ASGI) + **Pydantic** (validation) + Python type hints.

```python
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
import uvicorn

app = FastAPI(
    title="My API",
    version="1.0.0",
    description="Production-ready FastAPI application"
)

# Pydantic models — input validation + serialization
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=0, le=150)
    role: str = Field(default="user", pattern="^(admin|user|moderator)$")

    @validator('name')
    def name_must_not_contain_special_chars(cls, v):
        if any(c in v for c in ['<', '>', '&', '"']):
            raise ValueError('Name contains invalid characters')
        return v.strip()

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True  # Allow ORM model conversion

# Routes
@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    user = await db.fetch_one("SELECT * FROM users WHERE id = $1", user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return user

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    try:
        result = await db.fetch_one(
            "INSERT INTO users (name, email, role) VALUES ($1, $2, $3) RETURNING *",
            user.name, user.email, user.role
        )
        return result
    except UniqueViolationError:
        raise HTTPException(status_code=409, detail="Email already registered")
```

---

## 3.2 Dependency Injection System

FastAPI's DI is one of its killer features — injectable, testable, composable.

```python
from fastapi import Depends
from functools import lru_cache
from typing import Generator

# Database session dependency
async def get_db() -> Generator:
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Settings dependency (singleton)
@lru_cache()
def get_settings() -> Settings:
    return Settings()  # Loaded from environment once

# Auth dependency
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Role-based access
def require_role(role: str):
    async def check_role(current_user: User = Depends(get_current_user)):
        if current_user.role != role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return check_role

# Usage
@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    # Only admins can reach here
    await db.delete(await db.get(User, user_id))
```

---

## 3.3 JWT Authentication — Full Implementation

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    def create_token(self, data: dict, expires_in: timedelta) -> str:
        to_encode = data.copy()
        to_encode["exp"] = datetime.utcnow() + expires_in
        to_encode["iat"] = datetime.utcnow()
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_tokens(self, user_id: int) -> dict:
        return {
            "access_token": self.create_token(
                {"sub": str(user_id), "type": "access"},
                timedelta(minutes=15)
            ),
            "refresh_token": self.create_token(
                {"sub": str(user_id), "type": "refresh"},
                timedelta(days=7)
            ),
            "token_type": "bearer",
        }

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

# Endpoints
@app.post("/auth/login")
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, form.username)
    if not user or not auth.verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return auth.create_tokens(user.id)

@app.post("/auth/refresh")
async def refresh(refresh_token: str, db: AsyncSession = Depends(get_db)):
    payload = auth.decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    return auth.create_tokens(int(payload["sub"]))
```

---

## 3.4 Async & Database with SQLAlchemy

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, select, func
from typing import Optional

engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before use
    echo=False,
)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    posts: Mapped[list["Post"]] = relationship(back_populates="author", lazy="selectin")

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="posts")

# Repository pattern
class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        return await self.db.get(User, user_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        result = await self.db.execute(
            select(User).offset(skip).limit(limit).order_by(User.id)
        )
        return result.scalars().all()

    async def create(self, **kwargs) -> User:
        user = User(**kwargs)
        self.db.add(user)
        await self.db.flush()  # Get generated ID without committing
        return user

    async def get_users_with_post_count(self):
        result = await self.db.execute(
            select(User, func.count(Post.id).label("post_count"))
            .outerjoin(Post)
            .group_by(User.id)
        )
        return result.all()
```

---

## 3.5 Middleware & Background Tasks

```python
from fastapi import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
import uuid

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com"],  # Never use ["*"] in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Custom middleware — request ID + timing
@app.middleware("http")
async def add_request_metadata(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{duration:.3f}s"

    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
    return response

# Background tasks — fire and forget
def send_welcome_email(user_email: str, user_name: str):
    # Runs after response is sent to client
    email_service.send(
        to=user_email,
        subject="Welcome!",
        body=f"Hi {user_name}, welcome to our platform!"
    )

@app.post("/users", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    new_user = await user_repo.create(**user.dict())
    background_tasks.add_task(send_welcome_email, new_user.email, new_user.name)
    return new_user  # Returns immediately, email sent in background
```

---

## 3.6 FastAPI Error Handling

```python
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Custom exception classes
class BusinessError(Exception):
    def __init__(self, message: str, code: str, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code

class ResourceNotFoundError(BusinessError):
    def __init__(self, resource: str, identifier):
        super().__init__(
            message=f"{resource} with id {identifier} not found",
            code="RESOURCE_NOT_FOUND",
            status_code=404
        )

# Global exception handlers
@app.exception_handler(BusinessError)
async def business_error_handler(request: Request, exc: BusinessError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.code, "message": exc.message}
    )

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "details": [
                {
                    "field": " -> ".join(str(loc) for loc in e["loc"][1:]),
                    "message": e["msg"],
                }
                for e in exc.errors()
            ]
        }
    )

@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception):
    logger.exception("Unexpected error", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"error": "INTERNAL_ERROR", "message": "An unexpected error occurred"}
    )
```

---

## 3.7 WebSockets & Server-Sent Events

```python
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        self.active_connections.setdefault(room, []).append(websocket)

    def disconnect(self, websocket: WebSocket, room: str):
        self.active_connections.get(room, []).remove(websocket)

    async def broadcast(self, room: str, message: dict):
        for connection in self.active_connections.get(room, []):
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(room_id, {
                "user": data["user"],
                "message": data["message"],
                "timestamp": datetime.utcnow().isoformat()
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        await manager.broadcast(room_id, {"system": f"User left the room"})

# Server-Sent Events (SSE) — one-way streaming
from sse_starlette.sse import EventSourceResponse

@app.get("/events/live")
async def live_events(request: Request):
    async def generator():
        while True:
            if await request.is_disconnected():
                break
            data = await get_latest_events()
            yield {"data": json.dumps(data), "event": "update"}
            await asyncio.sleep(1)
    return EventSourceResponse(generator())
```

---

# DAY 4: PostgreSQL + Redis

## 4.1 PostgreSQL — Core SQL (Must Know)

```sql
-- Window functions — rank/aggregate without collapsing rows
SELECT
    user_id,
    order_date,
    amount,
    SUM(amount) OVER (PARTITION BY user_id ORDER BY order_date) AS running_total,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY amount DESC) AS rank_by_amount,
    LAG(amount) OVER (PARTITION BY user_id ORDER BY order_date) AS prev_amount,
    LEAD(amount) OVER (PARTITION BY user_id ORDER BY order_date) AS next_amount
FROM orders;

-- CTE (Common Table Expressions) — readable, reusable
WITH monthly_sales AS (
    SELECT
        DATE_TRUNC('month', created_at) AS month,
        SUM(amount) AS total,
        COUNT(*) AS order_count
    FROM orders
    WHERE created_at >= NOW() - INTERVAL '12 months'
    GROUP BY 1
),
ranked_months AS (
    SELECT *,
        RANK() OVER (ORDER BY total DESC) AS rank
    FROM monthly_sales
)
SELECT * FROM ranked_months WHERE rank <= 3; -- Top 3 months

-- Recursive CTE — hierarchical data (org charts, categories)
WITH RECURSIVE category_tree AS (
    -- Base case
    SELECT id, name, parent_id, 0 AS depth, name::TEXT AS path
    FROM categories
    WHERE parent_id IS NULL

    UNION ALL

    -- Recursive case
    SELECT c.id, c.name, c.parent_id, ct.depth + 1, ct.path || ' > ' || c.name
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT * FROM category_tree ORDER BY path;

-- LATERAL JOIN — dependent subquery for each row
SELECT u.id, u.name, recent_orders.order_id, recent_orders.amount
FROM users u
CROSS JOIN LATERAL (
    SELECT id AS order_id, amount
    FROM orders
    WHERE user_id = u.id
    ORDER BY created_at DESC
    LIMIT 3  -- Last 3 orders per user
) recent_orders;

-- UPSERT (INSERT ... ON CONFLICT)
INSERT INTO user_stats (user_id, login_count, last_login)
VALUES ($1, 1, NOW())
ON CONFLICT (user_id)
DO UPDATE SET
    login_count = user_stats.login_count + 1,
    last_login = NOW()
RETURNING *;
```

---

## 4.2 Indexing Strategy

```sql
-- B-Tree (default) — equality, range, sorting
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_created ON orders(created_at DESC); -- Sorted
CREATE INDEX idx_orders_user_amount ON orders(user_id, amount); -- Composite

-- Partial index — index only relevant rows (smaller, faster)
CREATE INDEX idx_active_users ON users(email) WHERE is_active = true;
CREATE INDEX idx_pending_orders ON orders(created_at) WHERE status = 'pending';

-- GIN index — full text search, arrays, JSONB
CREATE INDEX idx_products_tags ON products USING GIN(tags); -- Array column
CREATE INDEX idx_docs_content ON documents USING GIN(to_tsvector('english', content));

-- BRIN — large tables with natural ordering (logs, time-series)
CREATE INDEX idx_logs_created ON logs USING BRIN(created_at);

-- Full text search
ALTER TABLE products ADD COLUMN search_vector tsvector;
UPDATE products SET search_vector = to_tsvector('english', name || ' ' || description);
CREATE INDEX idx_products_search ON products USING GIN(search_vector);

SELECT * FROM products
WHERE search_vector @@ plainto_tsquery('english', 'wireless bluetooth headphones')
ORDER BY ts_rank(search_vector, plainto_tsquery('english', 'wireless bluetooth headphones')) DESC;

-- EXPLAIN ANALYZE — understand query performance
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM orders WHERE user_id = 123 AND status = 'pending';
-- Look for: Seq Scan (bad on large tables) vs Index Scan (good)
-- Look for: actual rows vs estimated rows (statistics quality)
```

---

## 4.3 Transactions & ACID

```sql
-- Transaction with savepoints
BEGIN;

SAVEPOINT before_payment;

UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

-- Conditional rollback to savepoint
DO $$
BEGIN
    IF (SELECT balance FROM accounts WHERE id = 1) < 0 THEN
        ROLLBACK TO SAVEPOINT before_payment;
        RAISE EXCEPTION 'Insufficient funds';
    END IF;
END;
$$;

COMMIT;

-- Isolation levels
-- READ COMMITTED (default) — sees committed data from other transactions
-- REPEATABLE READ — consistent snapshot; prevents dirty/non-repeatable reads
-- SERIALIZABLE — full ACID; prevents phantoms but slowest

SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN;
-- Both queries see the same snapshot even if other transactions commit
SELECT * FROM inventory WHERE product_id = 1;
-- ... some processing ...
SELECT * FROM inventory WHERE product_id = 1; -- Same result as above
COMMIT;

-- Advisory locks — application-level distributed locks
SELECT pg_advisory_lock(user_id); -- Blocks until acquired
-- ... critical section ...
SELECT pg_advisory_unlock(user_id);

-- Or try-acquire (non-blocking)
SELECT pg_try_advisory_lock(user_id); -- Returns false if can't acquire
```

---

## 4.4 Advanced PostgreSQL Features

```sql
-- JSONB — flexible schema within structured schema
CREATE TABLE events (
    id BIGSERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- JSONB operators
SELECT payload->>'email' FROM events WHERE type = 'user.created';
SELECT * FROM events WHERE payload @> '{"status": "active"}'; -- Contains
SELECT * FROM events WHERE payload ? 'email'; -- Key exists

-- JSONB indexing
CREATE INDEX idx_events_payload ON events USING GIN(payload jsonb_path_ops);

-- Table partitioning — critical for large tables
CREATE TABLE orders (
    id BIGSERIAL,
    user_id INT,
    amount DECIMAL,
    created_at TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY RANGE (created_at);

CREATE TABLE orders_2024_q1 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');
CREATE TABLE orders_2024_q2 PARTITION OF orders
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

-- Materialized views — precomputed expensive queries
CREATE MATERIALIZED VIEW user_analytics AS
SELECT
    u.id,
    u.name,
    COUNT(o.id) AS total_orders,
    SUM(o.amount) AS total_spent,
    AVG(o.amount) AS avg_order_value
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;

CREATE INDEX ON user_analytics(total_spent DESC);
REFRESH MATERIALIZED VIEW CONCURRENTLY user_analytics; -- Non-blocking refresh

-- Connection pooling best practices (PgBouncer)
-- Pool modes: session (default), transaction (recommended), statement
-- Transaction mode: connections returned to pool between transactions
-- This allows 100 connections to serve thousands of app instances
```

---

## 4.5 Redis — Patterns & Data Structures

```python
import redis.asyncio as redis
from typing import Optional
import json

# Async Redis client
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# ── String: Simple cache ─────────────────────────────────────────────────────
async def get_user_cached(user_id: int) -> Optional[dict]:
    key = f"user:{user_id}"
    cached = await r.get(key)
    if cached:
        return json.loads(cached)

    user = await db.fetch_user(user_id)
    if user:
        await r.setex(key, 3600, json.dumps(user))  # TTL: 1 hour
    return user

# ── Hash: Store structured data ──────────────────────────────────────────────
async def cache_user_hash(user: dict):
    key = f"user:hash:{user['id']}"
    await r.hset(key, mapping=user)
    await r.expire(key, 3600)

user_email = await r.hget("user:hash:123", "email")

# ── List: Message queue / recent items ───────────────────────────────────────
async def push_notification(user_id: int, message: str):
    key = f"notifications:{user_id}"
    await r.lpush(key, json.dumps({"msg": message, "ts": time.time()}))
    await r.ltrim(key, 0, 99)  # Keep only last 100

async def get_notifications(user_id: int) -> list:
    key = f"notifications:{user_id}"
    items = await r.lrange(key, 0, -1)
    return [json.loads(i) for i in items]

# ── Set: Unique members ──────────────────────────────────────────────────────
async def track_visitor(page_id: str, user_id: str):
    key = f"visitors:{page_id}:{today()}"
    await r.sadd(key, user_id)
    await r.expire(key, 86400)  # 24h TTL

async def unique_visitors(page_id: str) -> int:
    return await r.scard(f"visitors:{page_id}:{today()}")

# ── Sorted Set: Leaderboard / rate limiting ──────────────────────────────────
async def update_leaderboard(user_id: str, score: float):
    await r.zadd("leaderboard", {user_id: score})

async def get_top_10():
    return await r.zrevrange("leaderboard", 0, 9, withscores=True)

# Rate limiting with sorted set (sliding window)
async def is_rate_limited(user_id: str, limit: int = 100, window: int = 60) -> bool:
    key = f"rate:{user_id}"
    now = time.time()
    pipe = r.pipeline()
    pipe.zremrangebyscore(key, 0, now - window)  # Remove old entries
    pipe.zadd(key, {str(now): now})              # Add current request
    pipe.zcard(key)                               # Count requests in window
    pipe.expire(key, window)
    results = await pipe.execute()
    return results[2] > limit  # True if over limit

# ── Pub/Sub: Real-time events ────────────────────────────────────────────────
async def publish_event(channel: str, event: dict):
    await r.publish(channel, json.dumps(event))

async def subscribe_to_events(channel: str, handler):
    pubsub = r.pubsub()
    await pubsub.subscribe(channel)
    async for message in pubsub.listen():
        if message['type'] == 'message':
            await handler(json.loads(message['data']))
```

---

## 4.6 Cache Invalidation Strategies

```python
# Strategy 1: Cache-Aside (most common)
async def get_product(product_id: int):
    cache_key = f"product:{product_id}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)                         # Cache hit

    product = await db.fetch_product(product_id)         # Cache miss
    await redis.setex(cache_key, 300, json.dumps(product))
    return product

# Invalidation on update
async def update_product(product_id: int, data: dict):
    await db.update_product(product_id, data)
    await redis.delete(f"product:{product_id}")          # Invalidate cache

# Strategy 2: Write-Through — update cache on every write
async def save_user(user: dict):
    await db.save_user(user)
    await redis.setex(f"user:{user['id']}", 3600, json.dumps(user))

# Strategy 3: Tag-based invalidation
async def invalidate_user_cache(user_id: int):
    # Find all keys related to this user
    keys = await redis.keys(f"*user:{user_id}*")
    if keys:
        await redis.delete(*keys)

# Strategy 4: Cache stampede prevention (mutex lock)
async def get_with_lock(key: str, fetch_fn, ttl: int = 300):
    cached = await redis.get(key)
    if cached:
        return json.loads(cached)

    lock_key = f"lock:{key}"
    lock = await redis.set(lock_key, "1", nx=True, ex=5)  # 5s lock

    if lock:
        try:
            data = await fetch_fn()
            await redis.setex(key, ttl, json.dumps(data))
            return data
        finally:
            await redis.delete(lock_key)
    else:
        # Wait and retry (someone else is fetching)
        await asyncio.sleep(0.1)
        return await get_with_lock(key, fetch_fn, ttl)
```

---

# DAY 5: Advanced Architecture & Performance

## 5.1 System Design Principles

**SOLID Principles applied to Full Stack:**

```python
# Single Responsibility — each class does ONE thing
class UserRepository:  # Only data access
    async def find_by_email(self, email: str) -> Optional[User]: ...

class PasswordHasher:  # Only password ops
    def hash(self, password: str) -> str: ...
    def verify(self, password: str, hash: str) -> bool: ...

class EmailService:  # Only email sending
    async def send_welcome(self, user: User) -> None: ...

class UserService:  # Orchestrates above
    def __init__(self, repo, hasher, emailer):
        self.repo = repo
        self.hasher = hasher
        self.emailer = emailer

    async def register(self, email: str, password: str) -> User:
        existing = await self.repo.find_by_email(email)
        if existing:
            raise EmailTakenError(email)
        hashed = self.hasher.hash(password)
        user = await self.repo.create(email=email, password=hashed)
        await self.emailer.send_welcome(user)  # Background task in real app
        return user

# Open/Closed — open for extension, closed for modification
class NotificationSender(ABC):
    @abstractmethod
    async def send(self, recipient: str, message: str) -> None: ...

class EmailSender(NotificationSender):
    async def send(self, recipient, message): ...  # Send email

class SmsSender(NotificationSender):
    async def send(self, recipient, message): ...  # Send SMS

class PushSender(NotificationSender):
    async def send(self, recipient, message): ...  # Send push

class NotificationService:
    def __init__(self, senders: list[NotificationSender]):
        self.senders = senders  # Add new channel without changing this class

# Dependency Inversion — depend on abstractions
class OrderService:
    def __init__(self, payment_gateway: PaymentGateway):  # Interface, not Stripe
        self.gateway = payment_gateway  # Swap Stripe for PayPal without changing OrderService
```

---

## 5.2 API Design Best Practices

```python
# RESTful resource naming
# ✅ Nouns, plural, hierarchical
GET    /api/v1/users               # List users
POST   /api/v1/users               # Create user
GET    /api/v1/users/{id}          # Get user
PUT    /api/v1/users/{id}          # Replace user
PATCH  /api/v1/users/{id}          # Partial update
DELETE /api/v1/users/{id}          # Delete user
GET    /api/v1/users/{id}/orders   # User's orders (sub-resource)

# ❌ Verbs in URLs
POST /api/createUser       # Bad
GET  /api/getUserById      # Bad
POST /api/deleteUser       # Terrible

# Pagination
@app.get("/api/v1/users")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(id|name|email|created_at)$"),
    sort_dir: str = Query("desc", regex="^(asc|desc)$"),
):
    offset = (page - 1) * page_size
    total = await count_users()
    users = await fetch_users(offset=offset, limit=page_size, sort=f"{sort_by} {sort_dir}")

    return {
        "data": users,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": math.ceil(total / page_size),
            "has_next": page * page_size < total,
            "has_prev": page > 1,
        }
    }

# Versioning strategies
# URL versioning: /api/v1/ vs /api/v2/ — most visible, easiest
# Header versioning: Accept: application/vnd.myapi.v2+json — cleaner URLs
# Query param: /api/users?version=2 — easy to test
```

---

## 5.3 Performance Optimization Patterns

```python
# N+1 Query problem
# ❌ N+1 — 1 query for users + N queries for orders
users = await db.execute(select(User))
for user in users:
    user.orders = await db.execute(select(Order).where(Order.user_id == user.id))

# ✅ Eager loading — 2 queries total
users = await db.execute(select(User).options(selectinload(User.orders)))

# ✅ Or use JOIN
result = await db.execute(
    select(User, Order)
    .outerjoin(Order)
    .where(User.is_active == True)
)

# Database connection pooling
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,           # Permanent connections
    max_overflow=20,        # Extra connections when pool exhausted
    pool_timeout=30,        # Wait time for connection from pool
    pool_recycle=1800,      # Recycle connections after 30min (prevent stale)
    pool_pre_ping=True,     # Test connection before use
)

# Request coalescing — combine simultaneous DB requests
from aiocache import cached, Cache

@cached(ttl=60, cache=Cache.REDIS, key_builder=lambda f, *a, **kw: f"user:{a[1]}")
async def get_user(user_id: int): ...

# Async parallel operations
async def get_dashboard_data(user_id: int):
    # Run all 4 queries concurrently instead of sequentially
    user, orders, notifications, stats = await asyncio.gather(
        get_user(user_id),
        get_recent_orders(user_id),
        get_notifications(user_id),
        get_user_stats(user_id),
    )
    return {"user": user, "orders": orders, "notifications": notifications, "stats": stats}

# Response compression
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=500)  # Compress responses > 500 bytes
```

---

## 5.4 Security Best Practices

```python
# Input validation at every layer
from pydantic import BaseModel, validator
import bleach  # HTML sanitization

class CommentCreate(BaseModel):
    content: str

    @validator('content')
    def sanitize_content(cls, v):
        return bleach.clean(v, tags=[], strip=True)  # Strip all HTML

# SQL injection prevention — always use parameterized queries
# ❌ NEVER do this
query = f"SELECT * FROM users WHERE email = '{user_input}'"

# ✅ Always use parameters
result = await db.execute("SELECT * FROM users WHERE email = $1", [user_input])
# Or with SQLAlchemy ORM (automatically parameterized)
result = await db.execute(select(User).where(User.email == user_email))

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/auth/login")
@limiter.limit("5/minute")  # Max 5 login attempts per minute per IP
async def login(request: Request, form: LoginForm): ...

# Sensitive data handling
import secrets
from cryptography.fernet import Fernet

class SecureConfig:
    def __init__(self, key: bytes):
        self.fernet = Fernet(key)

    def encrypt(self, data: str) -> str:
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, encrypted: str) -> str:
        return self.fernet.decrypt(encrypted.encode()).decode()

# Security headers middleware
@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

---

## 5.5 Microservices & Message Queues

```python
# Event-driven architecture with Celery + Redis/RabbitMQ
from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/1",
    backend="redis://localhost:6379/2",
)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, recipient: str, subject: str, body: str):
    try:
        email_service.send(recipient, subject, body)
    except Exception as exc:
        raise self.retry(exc=exc)  # Retry up to 3 times

# Dispatch from FastAPI
@app.post("/orders")
async def create_order(order: OrderCreate):
    new_order = await order_service.create(order)
    # Non-blocking — email sent asynchronously by Celery worker
    send_email_task.delay(
        recipient=new_order.user.email,
        subject="Order Confirmed",
        body=f"Your order #{new_order.id} is confirmed!"
    )
    return new_order

# Scheduled tasks
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=0, minute=0),  # Daily at midnight
        cleanup_expired_sessions.s(),
    )
    sender.add_periodic_task(300, sync_analytics.s())  # Every 5 minutes

# Health check endpoint
@app.get("/health")
async def health_check():
    checks = {}
    try:
        await db.execute("SELECT 1")
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {e}"

    try:
        await redis.ping()
        checks["redis"] = "healthy"
    except Exception as e:
        checks["redis"] = f"unhealthy: {e}"

    all_healthy = all(v == "healthy" for v in checks.values())
    return JSONResponse(
        content={"status": "healthy" if all_healthy else "degraded", "checks": checks},
        status_code=200 if all_healthy else 503
    )
```

---

## 5.6 Docker & Deployment

```dockerfile
# Multi-stage Dockerfile — lean production image
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12-slim AS production
WORKDIR /app
# Copy only installed packages from builder
COPY --from=builder /root/.local /root/.local
COPY . .

# Non-root user for security
RUN useradd --create-home --no-log-init appuser && chown -R appuser:appuser /app
USER appuser

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

```yaml
# docker-compose.yml for development
version: "3.9"
services:
  api:
    build: .
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql+asyncpg://user:pass@db/mydb
      REDIS_URL: redis://redis:6379
    volumes:
      - .:/app  # Hot reload in dev
    depends_on:
      db: { condition: service_healthy }
      redis: { condition: service_healthy }

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]

volumes:
  postgres_data:
```

---

## 5.7 Advanced React Architecture

```jsx
// Feature-based folder structure (scalable)
// src/
//   features/
//     auth/
//       api.ts          ← API calls for this feature
//       hooks.ts        ← Custom hooks
//       store.ts        ← Zustand/Redux slice
//       components/     ← Feature-specific components
//       index.ts        ← Public API (export only what's needed)
//     products/
//     orders/
//   shared/
//     components/       ← Reusable UI components
//     hooks/            ← Shared hooks
//     utils/            ← Pure utility functions
//   app/
//     router.tsx        ← Route definitions
//     store.ts          ← Global store setup

// Zustand — lightweight state management
import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { persist } from 'zustand/middleware';

interface CartState {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (id: string) => void;
  clearCart: () => void;
  total: () => number;
}

const useCartStore = create<CartState>()(
  persist(
    immer((set, get) => ({
      items: [],

      addItem: (item) => set(state => {
        const existing = state.items.find(i => i.id === item.id);
        if (existing) {
          existing.quantity += 1;
        } else {
          state.items.push({ ...item, quantity: 1 });
        }
      }),

      removeItem: (id) => set(state => {
        state.items = state.items.filter(i => i.id !== id);
      }),

      clearCart: () => set({ items: [] }),

      total: () => get().items.reduce((sum, i) => sum + i.price * i.quantity, 0),
    })),
    { name: 'cart-storage' } // Persists to localStorage
  )
);

// React Query — server state management
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: () => fetch('/api/users').then(r => r.json()),
    staleTime: 5 * 60 * 1000, // Data considered fresh for 5 minutes
    gcTime: 10 * 60 * 1000,   // Keep in cache for 10 minutes
  });
}

function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (user) => fetch('/api/users', {
      method: 'POST',
      body: JSON.stringify(user),
    }).then(r => r.json()),

    onSuccess: (newUser) => {
      // Optimistic update — add to cache immediately
      queryClient.setQueryData(['users'], (old) => [...(old || []), newUser]);
      // Or just invalidate to refetch
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },

    onError: (error) => {
      toast.error(`Failed to create user: ${error.message}`);
    },
  });
}
```

---

## 5.8 Testing Strategy

```javascript
// Unit Tests — pure functions and hooks
import { renderHook, act } from '@testing-library/react';
import { useDebounce } from './useDebounce';

test('useDebounce delays value update', async () => {
  const { result, rerender } = renderHook(({ val }) => useDebounce(val, 300), {
    initialProps: { val: 'initial' },
  });

  expect(result.current).toBe('initial');

  rerender({ val: 'updated' });
  expect(result.current).toBe('initial'); // Not updated yet

  await act(async () => { await new Promise(r => setTimeout(r, 300)); });
  expect(result.current).toBe('updated'); // Now updated
});

// Integration Tests — component + API
import { render, screen, waitFor, userEvent } from '@testing-library/react';
import { server } from '../mocks/server'; // MSW mock server
import { http, HttpResponse } from 'msw';

test('user can create a post', async () => {
  server.use(
    http.post('/api/posts', () => HttpResponse.json({ id: 1, title: 'Test Post' }))
  );

  render(<CreatePostForm />);

  await userEvent.type(screen.getByLabelText('Title'), 'Test Post');
  await userEvent.click(screen.getByRole('button', { name: 'Create' }));

  await waitFor(() => {
    expect(screen.getByText('Post created successfully!')).toBeInTheDocument();
  });
});

// FastAPI Testing
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/users", json={
            "name": "Alice",
            "email": "alice@example.com",
            "age": 30,
        })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice"
    assert "id" in data

@pytest.fixture
async def authenticated_client(test_db):
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login to get token
        response = await client.post("/auth/login", data={
            "username": "admin@test.com",
            "password": "testpass",
        })
        token = response.json()["access_token"]
        client.headers["Authorization"] = f"Bearer {token}"
        yield client
```

---

## 5.9 Common Interview Questions & Answers

### JavaScript
| Question | Key Points |
|----------|------------|
| What is the event loop? | Call stack → Web APIs → Callback queue → Microtask queue |
| Explain closures | Function retains lexical scope; used for encapsulation, modules |
| var vs let vs const | var: function-scoped, hoisted; let/const: block-scoped; const: no reassign |
| == vs === | == coerces types; === strict equality; always use === |
| What is hoisting? | var declarations and function declarations moved to top of scope |
| Explain Promise.all vs Promise.allSettled | all: fails fast; allSettled: waits for all, reports individual status |
| What is a generator? | function* that can yield multiple values; used for lazy evaluation, async control |

### React
| Question | Key Points |
|----------|------------|
| Why do we need keys in lists? | Help React identify which elements changed; use stable unique IDs, not indexes |
| Reconciliation | Fiber algorithm; compares virtual DOM trees; O(n) heuristic diffing |
| When to use useReducer vs useState? | useReducer for complex state with multiple sub-values or complex transitions |
| How to prevent unnecessary re-renders? | React.memo, useMemo, useCallback, code splitting |
| Controlled vs uncontrolled components | Controlled: state in React; Uncontrolled: state in DOM via ref |
| What is React 18 concurrent mode? | Renders can be interrupted; `useTransition` for non-urgent updates |
| Explain Suspense | Declarative loading states; works with lazy() and React Query |

### FastAPI & Backend
| Question | Key Points |
|----------|------------|
| How does DI work in FastAPI? | Depends() decorator; dependencies are cached per request; testable |
| Sync vs Async in FastAPI | async def for I/O bound (DB, HTTP); sync def runs in threadpool |
| How to handle background tasks? | BackgroundTasks (same process) or Celery (separate workers) |
| What is Pydantic? | Data validation using Python type hints; V2 is 5-50x faster than V1 |
| Explain ASGI vs WSGI | ASGI: async, supports WebSockets, streaming; WSGI: sync only |

### PostgreSQL
| Question | Key Points |
|----------|------------|
| What is a B-tree index? | Balanced tree; O(log n) lookup; good for equality and range queries |
| When not to use an index? | Small tables; high write tables; low-selectivity columns (boolean) |
| Explain VACUUM | Reclaims dead tuple space; AUTOVACUUM runs automatically |
| INNER vs LEFT vs FULL JOIN | INNER: matching rows only; LEFT: all left + matching right; FULL: all from both |
| What is MVCC? | Multi-Version Concurrency Control; readers don't block writers |

---

## 5.10 System Design Template

**When asked "Design X" — structure your answer:**

```
1. Clarify Requirements (2 min)
   - Scale: how many users, requests/sec, data size?
   - Features: what's in scope for this design?
   - Non-functional: latency, availability, consistency requirements?

2. Estimation (2 min)
   - Daily active users × actions = requests/sec
   - Data storage = users × data/user × retention

3. High-Level Design (5 min)
   Client → CDN → Load Balancer → API Servers → Cache → Database

4. Deep Dive Components (10 min)
   - Database schema + indexing strategy
   - Cache strategy (what to cache, TTL, invalidation)
   - API design (endpoints, pagination)
   - Scaling approach (horizontal, vertical, sharding)

5. Bottlenecks & Trade-offs (3 min)
   - Single points of failure
   - What you'd do differently at 10x scale
   - CAP theorem trade-offs (consistency vs availability)
```

**Example: Design a URL Shortener**
```
Requirements: shorten URLs, redirect, analytics, 100M URLs, 1B redirects/day

Scale:
  - Write: 100M URLs / (365 × 86400) ≈ 3 writes/sec (easy)
  - Read: 1B / 86400 ≈ 11,500 reads/sec (needs caching)

Schema:
  CREATE TABLE urls (
      id BIGSERIAL PRIMARY KEY,
      short_code CHAR(7) UNIQUE NOT NULL,  -- base62 encoded
      original_url TEXT NOT NULL,
      user_id INT,
      created_at TIMESTAMPTZ DEFAULT NOW(),
      expires_at TIMESTAMPTZ
  );
  CREATE INDEX idx_short_code ON urls(short_code); -- Primary lookup

Short code generation:
  - Option 1: MD5(url)[:7] — risk of collision
  - Option 2: Auto-increment ID encoded as base62 — unique, no collision
  - Option 3: Redis counter + base62 — distributed, fast

Caching:
  - 80/20: 20% URLs get 80% traffic
  - Cache hot URLs in Redis: GET short:abc123 → original_url
  - TTL: 24 hours with refresh on access

Redirect flow:
  1. Check Redis cache — hit: 302 redirect (< 1ms)
  2. Cache miss: query Postgres, populate cache, redirect

Analytics:
  - Write-behind: log to Kafka → batch process → analytics DB
  - Async so it doesn't slow down redirect
```

---

## 5.11 Behavioral Questions for Senior Engineers

**Use STAR format: Situation → Task → Action → Result**

| Question | What They're Really Asking |
|----------|--------------------------|
| Tell me about a system you designed from scratch | Architecture thinking, trade-off decisions |
| A production incident happened. How did you handle it? | Incident management, communication, post-mortem thinking |
| How do you handle disagreement with technical decisions? | Collaboration, data-driven arguments, knowing when to defer |
| Describe a time you improved system performance | Profiling, bottleneck identification, measurement before/after |
| How do you balance technical debt with feature delivery? | Engineering judgment, prioritization, business awareness |
| How do you mentor junior developers? | Leadership, code reviews, knowledge sharing approach |

**Performance debugging checklist (use in answers):**
```
1. Measure first (don't guess) — profiler, logs, APM
2. Identify bottleneck — CPU, I/O, network, DB?
3. Check N+1 queries — enable query logging
4. Check missing indexes — EXPLAIN ANALYZE
5. Check slow queries — pg_stat_statements
6. Check cache hit rates — Redis INFO stats
7. Check connection pool saturation
8. Profile React renders — React DevTools Profiler
9. Check bundle size — webpack-bundle-analyzer
10. Check Core Web Vitals — Lighthouse
```

---

## 📋 Quick Reference Card

### HTTP Status Codes
| Code | Meaning | When to Use |
|------|---------|-------------|
| 200 | OK | Successful GET/PUT/PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Not authenticated |
| 403 | Forbidden | Authenticated but no permission |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource |
| 422 | Unprocessable | Validation error |
| 429 | Too Many Requests | Rate limited |
| 500 | Server Error | Unexpected server failure |
| 503 | Service Unavailable | Down for maintenance |

### JavaScript Cheat Sheet
```javascript
// Type coercion gotchas
0 == false   // true  (type coercion)
0 === false  // false (strict)
'' == false  // true
null == undefined // true (special rule)
null === undefined // false

// typeof
typeof null          // 'object' (historical bug)
typeof undefined     // 'undefined'
typeof function(){}  // 'function'
typeof []            // 'object'

// Falsy values: false, 0, '', null, undefined, NaN, 0n
// Truthy: everything else, including [] and {}

// Array methods that mutate: push, pop, shift, unshift, splice, sort, reverse
// Array methods that return new: map, filter, reduce, slice, concat, flat, flatMap
```

### React Hooks Dependencies Rules
```javascript
// useEffect deps: include ALL values from component scope used inside
// If you can't add something to deps without infinite loop → use ref or extract logic

// Common patterns:
// [] → run once on mount
// [value] → run when value changes
// no array → run every render (rarely needed)
// Cleanup fn → return from effect for subscriptions/timers/listeners
```

---

*Last updated: 2025 | Good luck with your interviews! 🎯*
