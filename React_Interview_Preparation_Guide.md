# React Advanced Concepts - Interview Preparation Guide

## 5 Years Experience | 80/20 Method | 1-Week Comprehensive Study Plan

### Core Topics Covered:
- React Hooks & State Management Patterns
- Performance Optimization & Memoization
- Advanced Rendering Techniques
- Custom Hooks & Code Reusability
- Concurrent Features & Suspense
- System Design & Real-world Scenarios

---

# Day 1: React Hooks & State Management Mastery

**Focus Area:** Understanding hooks deeply with practical patterns that appear in real interviews

**Estimated Time:** 8 hours

---

## 1. useState Deep Dive - Beyond Basics

**Why It Matters:** 80% of React state management uses useState. Master the nuances.

### Key Concepts to Master:
- Functional updates vs direct updates
- State batching in event handlers vs async operations
- Lazy initialization pattern
- Multiple state vs single object state

### Interview Example #1: Functional vs Direct Updates

**WRONG - Direct update loses pending updates:**
```javascript
setCount(count + 1);
```

**CORRECT - Functional update ensures accuracy:**
```javascript
setCount(prev => prev + 1);
setCount(prev => prev + 1);
// Result: count += 2
```

### Interview Example #2: Lazy Initialization (CRITICAL)

**WRONG - Runs on every render:**
```javascript
const [state, setState] = useState(expensiveComputation());
```

**CORRECT - Runs only once:**
```javascript
const [state, setState] = useState(() => expensiveComputation());
```

**Use Case:** When initial state requires heavy computation (parsing data, API calls)

---

## 2. useEffect Mastery - The Most Misunderstood Hook

**Reality:** 60% of React bugs are related to useEffect dependencies

### The Dependency Array Bible:
- **Empty []:** Runs once after mount (perfect for setup, subscriptions)
- **[dep1, dep2]:** Runs when dependencies change
- **No array:** Runs after EVERY render (usually wrong!)

### Interview Problem #1: Memory Leak Prevention

```javascript
// CORRECT: Cleanup function pattern
useEffect(() => {
  const subscription = subscribe(onUpdate);
  return () => subscription.unsubscribe();
}, []);

// Handles: unmounting, re-subscriptions
```

### Interview Problem #2: Dependency Warning Fixes

**WRONG - Missing dependency causes stale data:**
```javascript
useEffect(() => {
  const timer = setTimeout(() => setCount(count + 1), 1000);
  return () => clearTimeout(timer);
}, []); // ← count is missing!
```

**CORRECT - Use functional update:**
```javascript
useEffect(() => {
  const timer = setTimeout(() => setCount(prev => prev + 1), 1000);
  return () => clearTimeout(timer);
}, []);
```

---

## 3. useCallback & useMemo - Performance Patterns

**When to Use (The 80/20):** Only when passing callbacks to memoized children or as dependencies

### useCallback Rules:
- Memoizes function reference (not execution)
- Use when: Passing to React.memo component + deep object comparison
- Dependencies: List every value used inside the callback

### Interview Code Pattern:

```javascript
// Parent with memoized child
const Parent = () => {
  const [count, setCount] = useState(0);
  
  // Without useCallback: new function every render → Child re-renders
  const handleClick = useCallback(() => {
    setCount(prev => prev + 1);
  }, []); // Dependencies
  
  return <MemoizedChild onClick={handleClick} />;
};

const MemoizedChild = React.memo(({ onClick }) => (
  <button onClick={onClick}>Click</button>
));
```

### useMemo Pattern:

```javascript
// Memoize expensive computation
const expensiveValue = useMemo(() => {
  return sortLargeArray(data);
}, [data]); // Only recompute when data changes

// CRITICAL: Only use if computation actually matters
// Don't memoize simple operations like string concatenation
```

---

## 4. useReducer - State Logic in Complex Apps

**Use Instead Of:** Multiple useState calls for related state pieces

```javascript
const [state, dispatch] = useReducer(reducer, initialState);

function reducer(state, action) {
  switch(action.type) {
    case 'ADD_TODO':
      return { todos: [...state.todos, action.payload] };
    case 'REMOVE_TODO':
      return { todos: state.todos.filter(t => t.id !== action.id) };
    default:
      return state;
  }
}
```

---

## 5. Context + useContext - Avoiding Prop Drilling

**Reality:** Context causes unnecessary re-renders if not optimized

### Common Interview Mistake:

```javascript
// SLOW: Every consumer re-renders on any value change
const ThemeContext = createContext();

<ThemeContext.Provider value={{ theme, user, language }}>
  {/* theme change causes user/language subscribers to re-render */}
</ThemeContext.Provider>
```

### SOLUTION: Split Context

```javascript
// FAST: Separate contexts for separate concerns
const ThemeContext = createContext();
const UserContext = createContext();

<ThemeContext.Provider value={theme}>
  <UserContext.Provider value={user}>
    {children}
  </UserContext.Provider>
</ThemeContext.Provider>
```

---

# Day 2: Advanced State Management & Patterns

**Focus Area:** Custom hooks, state management patterns, and interview-level complexity

**Estimated Time:** 8 hours

---

## 1. Custom Hooks - Code Reusability Pattern

**Interview Reality:** Ability to write custom hooks shows deep React understanding

### Pattern #1: useAsync - Handle API Calls

```javascript
function useAsync(asyncFunction, immediate = true) {
  const [status, setStatus] = useState('idle');
  const [value, setValue] = useState(null);
  const [error, setError] = useState(null);

  const execute = useCallback(async () => {
    setStatus('pending');
    setValue(null);
    setError(null);
    try {
      const response = await asyncFunction();
      setValue(response);
      setStatus('success');
    } catch (error) {
      setError(error);
      setStatus('error');
    }
  }, [asyncFunction]);

  useEffect(() => {
    if (immediate) execute();
  }, [execute, immediate]);

  return { execute, status, value, error };
}
```

**Usage:**
```javascript
function UserProfile({ userId }) {
  const { status, value: user } = useAsync(
    () => fetch(`/api/users/${userId}`).then(r => r.json()),
    true
  );

  if (status === 'pending') return <Loading />;
  if (status === 'error') return <Error />;
  return <User data={user} />;
}
```

### Pattern #2: useLocalStorage - Persist State

```javascript
function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.log(error);
      return initialValue;
    }
  });

  const setValue = useCallback((value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.log(error);
    }
  }, [key, storedValue]);

  return [storedValue, setValue];
}
```

### Pattern #3: useDebounce - Optimize Search

```javascript
function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
}

// Usage: Search optimization
function SearchUsers() {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 500);

  useEffect(() => {
    if (debouncedQuery) {
      // Make API call only after user stops typing
      searchUsers(debouncedQuery);
    }
  }, [debouncedQuery]);

  return <input onChange={(e) => setQuery(e.target.value)} />;
}
```

---

## 2. State Management Patterns - Redux vs Alternatives

### When to Use What:
- **Redux:** Large apps, complex state, time-travel debugging needed
- **Zustand:** Simple alternative, less boilerplate than Redux
- **Recoil:** Atomic state management, granular re-renders
- **Context:** Simple cases, avoid for frequently changing data

---

## 3. Compound Component Pattern

**Use Case:** Complex UI components with related sub-components

```javascript
// Flexible, composable API
<Tabs>
  <Tabs.Header>
    <Tabs.Tab label="Tab 1" />
    <Tabs.Tab label="Tab 2" />
  </Tabs.Header>
  <Tabs.Content>
    <Tabs.Panel>Content 1</Tabs.Panel>
    <Tabs.Panel>Content 2</Tabs.Panel>
  </Tabs.Content>
</Tabs>
```

**Implementation:**
```javascript
const TabsContext = createContext();

function Tabs({ children }) {
  const [activeTab, setActiveTab] = useState(0);
  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      {children}
    </TabsContext.Provider>
  );
}

function Tab({ label, index }) {
  const { activeTab, setActiveTab } = useContext(TabsContext);
  return (
    <button 
      onClick={() => setActiveTab(index)}
      className={activeTab === index ? 'active' : ''}
    >
      {label}
    </button>
  );
}

Tabs.Tab = Tab;
Tabs.Panel = Panel; // Similar pattern
```

---

## 4. Render Props Pattern

**Legacy but still appears in interviews**

```javascript
// Instead of custom hook, pass a function as child
<AsyncData 
  url="/api/users"
  render={({ data, loading, error }) => (
    loading ? <Spinner /> : <UserList users={data} />
  )}
/>

// Implementation
function AsyncData({ url, render }) {
  const { status, value } = useAsync(() => fetch(url).then(r => r.json()));
  return render({ 
    data: value, 
    loading: status === 'pending', 
    error: status === 'error' 
  });
}
```

---

## 5. Higher-Order Component (HOC) Pattern

```javascript
// withAuthentication HOC
function withAuthentication(Component) {
  return function ProtectedComponent(props) {
    const { user, isLoading } = useAuth();
    
    if (isLoading) return <Loading />;
    if (!user) return <Redirect to="/login" />;
    
    return <Component {...props} user={user} />;
  };
}

// Usage
export default withAuthentication(Dashboard);
```

---

# Day 3: Performance Optimization & Rendering

**Focus Area:** Making React apps blazing fast - interview gold

**Estimated Time:** 8 hours

---

## 1. React.memo - Prevent Unnecessary Re-renders

**Key Insight:** Prevents re-render only if props are equal (shallow comparison)

### Basic Usage:

```javascript
// Before: Re-renders every time parent renders
function UserCard({ user, onSelect }) {
  return <div onClick={onSelect}>{user.name}</div>;
}

// After: Only re-renders if props change
export default React.memo(UserCard);
```

### Custom Comparison (Interview Trick):

```javascript
// Custom comparison function
function areEqual(prevProps, nextProps) {
  return prevProps.userId === nextProps.userId 
    && prevProps.theme === nextProps.theme;
    // Return true = skip render, false = do render
}

export default React.memo(UserCard, areEqual);
```

---

## 2. Code Splitting - Lazy Loading

**Critical for large apps:** Reduce initial bundle size

```javascript
import { Suspense, lazy } from 'react';

const HeavyComponent = lazy(() => import('./HeavyComponent'));
const AdminPanel = lazy(() => import('./AdminPanel'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/admin" element={<AdminPanel />} />
      </Routes>
    </Suspense>
  );
}
```

---

## 3. Virtual Scrolling - Handle Massive Lists

**Performance Boost:** Render only visible items

```javascript
// Using react-window library
import { FixedSizeList } from 'react-window';

function LargeList({ items }) {
  const Row = ({ index, style }) => (
    <div style={style}>{items[index].name}</div>
  );

  return (
    <FixedSizeList
      height={600}
      itemCount={items.length}
      itemSize={35}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
}

// With 1M items: renders only ~17 visible items at a time
```

---

## 4. Batching & Automatic Batching

**React 18+:** Batches multiple state updates automatically

```javascript
// React 18: Both setCount and setFlag batched together
function Counter() {
  const [count, setCount] = useState(0);
  const [flag, setFlag] = useState(false);

  const handleClick = () => {
    setCount(prev => prev + 1);
    setFlag(!flag); // Single re-render
  };

  return <button onClick={handleClick}>{count}</button>;
}
```

---

## 5. Suspense & Concurrent Rendering

**The Future:** New React 18 features for better UX

```javascript
// Suspense for data fetching
<Suspense fallback={<Skeleton />}>
  <UserProfile userId={1} />
</Suspense>

// Transition API - non-blocking updates
function SearchUsers() {
  const [query, setQuery] = useState('');
  const [isPending, startTransition] = useTransition();

  const handleChange = (e) => {
    startTransition(() => {
      setQuery(e.target.value); // Low priority
    });
  };

  return (
    <>
      <input onChange={handleChange} disabled={isPending} />
      {isPending && <Spinner />}
    </>
  );
}
```

---

## 6. Production Build Optimization

### Key Tools:
- **Bundle Analyzer:** Find large dependencies
- **Tree-shaking:** Remove dead code
- **Minification:** Uglify code
- **Source maps:** Debug production (optional)

```bash
# Analyze bundle
npm run build -- --stats
webpack-bundle-analyzer

# Check for unnecessary re-renders
```

```javascript
import { Profiler } from 'react';

<Profiler id="UserList" onRender={onRenderCallback}>
  <UserList />
</Profiler>
```

---

# Day 4: Advanced Patterns & System Design

**Focus Area:** Architectural patterns used in large-scale applications

**Estimated Time:** 8 hours

---

## 1. Controlled vs Uncontrolled Components

**Interview Question:** "When would you use each?"

### Controlled Components - React Manages State:

```javascript
function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // Both values in React state
    login(email, password);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
    </form>
  );
}
```

### Uncontrolled Components - DOM Manages State:

```javascript
function LoginForm() {
  const emailRef = useRef();
  const passwordRef = useRef();

  const handleSubmit = (e) => {
    e.preventDefault();
    // Values come from DOM
    login(emailRef.current.value, passwordRef.current.value);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input ref={emailRef} />
      <input type="password" ref={passwordRef} />
    </form>
  );
}
```

### When to Use Each:
- **Controlled:** Complex validation, real-time feedback, conditional rendering
- **Uncontrolled:** File inputs, rich text editors, integration with non-React code

---

## 2. Error Boundaries - Graceful Error Handling

```javascript
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    logErrorToService(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />;
    }
    return this.props.children;
  }
}

// Usage
<ErrorBoundary>
  <RiskyComponent />
</ErrorBoundary>
```

---

## 3. Portal Pattern - Render Outside DOM Hierarchy

```javascript
import { createPortal } from 'react-dom';

function Modal({ children, isOpen }) {
  if (!isOpen) return null;
  
  // Renders to #modal-root, not parent component
  return createPortal(
    <div className="modal-overlay">
      <div className="modal-content">
        {children}
      </div>
    </div>,
    document.getElementById('modal-root')
  );
}

// Use case: Modals, tooltips, dropdowns that need z-index independence
```

---

## 4. Ref Forwarding - Pass Refs to Child Components

```javascript
// Without forwardRef: ref won't work on custom components
const TextInput = ({ ref }) => <input ref={ref} />;

// With forwardRef: parent can access input
const TextInput = forwardRef((props, ref) => (
  <input ref={ref} />
));

// Parent component
function TextInputWithFocus() {
  const inputRef = useRef();

  const focusInput = () => {
    inputRef.current.focus();
  };

  return (
    <>
      <TextInput ref={inputRef} />
      <button onClick={focusInput}>Focus</button>
    </>
  );
}
```

---

## 5. Observer Pattern with Custom Hooks

```javascript
// Simple observer for form changes
function useFormState(initialValues) {
  const [values, setValues] = useState(initialValues);
  const [touched, setTouched] = useState({});
  const [errors, setErrors] = useState({});

  const setFieldValue = useCallback((field, value) => {
    setValues(prev => ({ ...prev, [field]: value }));
  }, []);

  const setFieldTouched = useCallback((field) => {
    setTouched(prev => ({ ...prev, [field]: true }));
  }, []);

  const validateField = useCallback((field, value) => {
    const fieldErrors = validate(field, value);
    setErrors(prev => ({ ...prev, [field]: fieldErrors }));
  }, []);

  return {
    values,
    touched,
    errors,
    setFieldValue,
    setFieldTouched,
    validateField,
  };
}
```

---

## 6. Provider Pattern - Share Logic Across App

```javascript
// Theme provider
const ThemeContext = createContext();

export function ThemeProvider({ children, initialTheme = 'light' }) {
  const [theme, setTheme] = useState(initialTheme);

  const toggleTheme = useCallback(() => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  }, []);

  const value = useMemo(() => ({ theme, toggleTheme }), [theme]);

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}
```

---

# Day 5: Real-World Scenarios & System Design

**Focus Area:** Interview questions that combine multiple concepts

**Estimated Time:** 8 hours

---

## System Design Scenario #1: Build a Data Table Component

**Requirements:** Sorting, filtering, pagination, search, large datasets

```javascript
function DataTable({ data, columns, pageSize = 10 }) {
  const [sortBy, setSortBy] = useState(null);
  const [filters, setFilters] = useState({});
  const [page, setPage] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const debouncedSearch = useDebounce(searchQuery, 300);

  // Filter data
  const filtered = useMemo(() => {
    return data.filter(row => {
      // Search filter
      const matchesSearch = columns.some(col =>
        String(row[col.key]).toLowerCase().includes(debouncedSearch.toLowerCase())
      );
      
      // Column filters
      const matchesFilters = Object.entries(filters).every(([key, value]) => {
        return !value || row[key] === value;
      });
      
      return matchesSearch && matchesFilters;
    });
  }, [data, filters, debouncedSearch]);

  // Sort data
  const sorted = useMemo(() => {
    const copy = [...filtered];
    if (sortBy) {
      copy.sort((a, b) => {
        const aVal = a[sortBy.key];
        const bVal = b[sortBy.key];
        return sortBy.direction === 'asc' 
          ? aVal > bVal ? 1 : -1 
          : aVal < bVal ? 1 : -1;
      });
    }
    return copy;
  }, [filtered, sortBy]);

  // Paginate
  const pageData = sorted.slice(page * pageSize, (page + 1) * pageSize);
  const totalPages = Math.ceil(sorted.length / pageSize);

  return (
    <>
      <input
        placeholder="Search..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />
      <table>
        <thead>
          <tr>
            {columns.map(col => (
              <th key={col.key} onClick={() => setSortBy({ key: col.key, direction: 'asc' })}>
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {pageData.map((row, idx) => (
            <tr key={idx}>
              {columns.map(col => <td key={col.key}>{row[col.key]}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
    </>
  );
}
```

---

## System Design Scenario #2: Form Builder with Validation

```javascript
function useFormBuilder(initialValues, onSubmit) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = useCallback((fieldName, value) => {
    // Add validation logic
    return validationErrors;
  }, []);

  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setValues(prev => ({ ...prev, [name]: value }));
    
    if (touched[name]) {
      const fieldErrors = validate(name, value);
      setErrors(prev => ({ ...prev, [name]: fieldErrors }));
    }
  }, [touched, validate]);

  const handleBlur = useCallback((e) => {
    const { name } = e.target;
    setTouched(prev => ({ ...prev, [name]: true }));
    const fieldErrors = validate(name, values[name]);
    setErrors(prev => ({ ...prev, [name]: fieldErrors }));
  }, [values, validate]);

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    const newErrors = {};
    Object.entries(values).forEach(([key, value]) => {
      const fieldErrors = validate(key, value);
      if (fieldErrors) newErrors[key] = fieldErrors;
    });

    setErrors(newErrors);

    if (Object.keys(newErrors).length === 0) {
      await onSubmit(values);
    }
    setIsSubmitting(false);
  }, [values, validate, onSubmit]);

  return {
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
  };
}
```

---

## System Design Scenario #3: Infinite Scroll with API Pagination

```javascript
function InfiniteList({ fetchData }) {
  const [items, setItems] = useState([]);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const observerTarget = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && hasMore && !isLoading) {
        setPage(prev => prev + 1);
      }
    });

    if (observerTarget.current) {
      observer.observe(observerTarget.current);
    }

    return () => observer.disconnect();
  }, [hasMore, isLoading]);

  useEffect(() => {
    if (!isLoading && hasMore) {
      setIsLoading(true);
      fetchData(page).then(newItems => {
        setItems(prev => [...prev, ...newItems]);
        setHasMore(newItems.length > 0);
        setIsLoading(false);
      });
    }
  }, [page, isLoading, hasMore, fetchData]);

  return (
    <>
      {items.map(item => <ItemCard key={item.id} item={item} />)}
      <div ref={observerTarget}>
        {isLoading && <Spinner />}
      </div>
    </>
  );
}
```

---

## Common Interview Questions to Master:

1. **"How would you optimize a 10,000-item list?"**
   - Answer: Virtual scrolling, pagination, or infinite scroll

2. **"What causes a component to re-render?"**
   - Answer: State/props change, parent render, context change

3. **"How do you prevent unnecessary re-renders?"**
   - Answer: React.memo, useMemo, useCallback, proper dependencies

4. **"Explain the dependency array in useEffect"**
   - Answer: Lists value dependencies, affects re-runs

5. **"What's the difference between controlled and uncontrolled components?"**
   - Answer: Who manages state (React vs DOM)

6. **"Design a modal component"**
   - Answer: Portal, event handling, focus management, accessibility

7. **"How do you handle authentication?"**
   - Answer: Context + custom hook, middleware, protected routes

8. **"What's a memory leak in React?"**
   - Answer: Subscriptions/timers not cleaned up in useEffect

9. **"Explain the fiber architecture"**
   - Answer: React's reconciliation engine, enables incremental rendering

10. **"Design a state management solution"**
    - Answer: Consider Redux, Context, Zustand based on requirements

---

## Performance Debugging Tools:

- **Chrome DevTools:** Rendering tab shows re-render highlights
- **React Profiler:** Measures component render times
- **Lighthouse:** Audits overall performance
- **Bundle Analyzer:** Identifies large dependencies

---

## Key Takeaways for 5-Year Experience Level:

✅ You should know **WHY**, not just **HOW**

✅ Understand **trade-offs** between patterns

✅ Know when **NOT** to use advanced patterns

✅ Explain **performance implications** of decisions

✅ Design systems considering **maintainability** and **scalability**

✅ Write hooks that are **reusable** across projects

---

## Quick Reference: Essential Hooks

| Hook | Use Case |
|------|----------|
| useState | Manage component state |
| useEffect | Side effects, subscriptions, cleanup |
| useCallback | Memoize callbacks for child components |
| useMemo | Memoize expensive computations |
| useReducer | Complex state logic |
| useContext | Access context values |
| useRef | Direct DOM access, mutable values |
| useReducer | State management for complex logic |

---

## Interview Question Bank:

1. What's the difference between let, const, and var? (Foundation)
2. Explain closure in JavaScript (Context for custom hooks)
3. What is the virtual DOM and how does React use it?
4. How do you optimize rendering performance?
5. Design a form component with validation
6. Implement a data table with sorting and filtering
7. What's the difference between useCallback and useMemo?
8. How would you handle authentication in a React app?
9. Explain the fiber architecture
10. Design a state management solution for a large app

---

## Practice Project Ideas:

- Build a Todo app with local storage persistence
- Create a weather app with API integration and caching
- Build an e-commerce product filter with multiple dimensions
- Implement a real-time collaborative editor (use WebSockets)
- Create a dashboard with charts and real-time data updates

---

## Pre-Interview Checklist:

- ☐ Can explain hooks lifecycle and dependencies
- ☐ Know when to use memo, callback, reducer vs context
- ☐ Can design a component that handles complex state
- ☐ Understand event delegation and synthetic events
- ☐ Can optimize a slow component
- ☐ Know about error boundaries and error handling
- ☐ Familiar with Suspense and concurrent features
- ☐ Can write custom hooks that are reusable
- ☐ Understand portals and ref forwarding
- ☐ Know testing basics (React Testing Library)

---

**Good luck with your interviews! 🚀**
