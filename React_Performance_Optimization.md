# React Performance Optimization Techniques

## Table of Contents
1. [React.memo](#1-reactmemo--prevent-unnecessary-re-renders)
2. [useCallback](#2-usecallback--memoize-functions)
3. [useMemo](#3-usememo--memoize-expensive-computations)
4. [Proper Key Prop](#4-proper-key-prop--optimize-list-rendering)
5. [Code Splitting & Lazy Loading](#5-code-splitting--lazy-loading--reduce-bundle-size)
6. [Virtual Lists](#6-virtual-lists--handle-large-lists)
7. [useReducer](#7-usereducer--optimize-complex-state)
8. [Optimize Dependencies](#8-optimize-dependencies--fix-useeffect-issues)
9. [Avoid Inline Objects/Functions](#9-avoid-inline-objectsfunctions-as-props)
10. [Production Build & Profiling](#10-production-build--profiling)

---

## 1. React.memo – Prevent Unnecessary Re-renders

Memoizes component to prevent re-renders unless props change.

```jsx
// Without memo - re-renders on every parent render
const UserCard = ({ name, age }) => {
  console.log('UserCard rendered');
  return <div>{name}, {age}</div>;
};

// With memo - only re-renders if props change
const UserCard = React.memo(({ name, age }) => {
  console.log('UserCard rendered');
  return <div>{name}, {age}</div>;
});

// With custom comparison
const UserCard = React.memo(
  ({ user }) => <div>{user.name}</div>,
  (prev, next) => prev.user.id === next.user.id // returns true if props are equal (skip render)
);
```

**When to use:**
- Component receives same props frequently
- Component is expensive to render
- Parent re-renders often but child props rarely change

---

## 2. useCallback – Memoize Functions

Prevents child components from re-rendering due to new function references.

```jsx
// ❌ Without useCallback - new function every render
function Parent() {
  const handleClick = () => console.log('clicked');
  return <Child onClick={handleClick} />;
}

// ✅ With useCallback - function stays the same
function Parent() {
  const handleClick = useCallback(() => {
    console.log('clicked');
  }, []); // empty dependency = never changes
  
  return <Child onClick={handleClick} />;
}

// With dependencies
const handleChange = useCallback((id, value) => {
  updateUser(id, value);
}, [userId]); // recreate if userId changes
```

**When to use:**
- Passing callbacks to memoized child components
- Callback is used in useEffect dependency array
- Callback function is expensive

---

## 3. useMemo – Memoize Expensive Computations

Prevents recalculating expensive operations.

```jsx
// ❌ Without useMemo - recalculates on every render
function TodoList({ todos, filter }) {
  const expensiveList = todos
    .filter(t => t.status === filter)
    .sort((a, b) => b.priority - a.priority)
    .map(t => ({ ...t, timeLeft: calculateTime(t) }));
  
  return <ul>{expensiveList.map(t => <li key={t.id}>{t.text}</li>)}</ul>;
}

// ✅ With useMemo - recalculates only if todos/filter change
function TodoList({ todos, filter }) {
  const expensiveList = useMemo(() => {
    return todos
      .filter(t => t.status === filter)
      .sort((a, b) => b.priority - a.priority)
      .map(t => ({ ...t, timeLeft: calculateTime(t) }));
  }, [todos, filter]);
  
  return <ul>{expensiveList.map(t => <li key={t.id}>{t.text}</li>)}</ul>;
}
```

**When to use:**
- Heavy computations (sorting, filtering, mapping large arrays)
- Creating objects/arrays passed to memoized children
- Expensive calculations that run frequently

---

## 4. Proper Key Prop – Optimize List Rendering

Use stable, unique identifiers, not array indices.

```jsx
// ❌ Bad - keys change when list reorders
todos.map((todo, index) => <TodoItem key={index} {...todo} />)

// ✅ Good - stable unique identifier
todos.map(todo => <TodoItem key={todo.id} {...todo} />)

// ✅ Also good for filtered/sorted lists
const sortedTodos = useMemo(() => 
  [...todos].sort((a, b) => a.priority - b.priority),
  [todos]
);

return sortedTodos.map(todo => <TodoItem key={todo.id} {...todo} />);
```

**Why it matters:**
- Helps React identify which items have changed
- Prevents state issues when list reorders
- Improves performance of list updates

---

## 5. Code Splitting & Lazy Loading – Reduce Bundle Size

Load components only when needed.

```jsx
import { lazy, Suspense } from 'react';

// Lazy load component
const HeavyChart = lazy(() => import('./HeavyChart'));
const Dashboard = lazy(() => import('./pages/Dashboard'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <HeavyChart />
    </Suspense>
  );
}

// Route-based code splitting
const routes = [
  {
    path: '/dashboard',
    element: lazy(() => import('./pages/Dashboard'))
  },
  {
    path: '/analytics',
    element: lazy(() => import('./pages/Analytics'))
  }
];
```

**Benefits:**
- Smaller initial bundle size
- Faster time to interactive (TTI)
- Load heavy components on demand

---

## 6. Virtual Lists – Handle Large Lists

Only render visible items for massive lists.

```jsx
import { FixedSizeList } from 'react-window';

function LargeList({ items }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      {items[index].name}
    </div>
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

// Alternative: Intersection Observer API
function VirtualList({ items }) {
  const [visibleRange, setVisibleRange] = useState({ start: 0, end: 20 });
  const containerRef = useRef();

  useEffect(() => {
    const observer = new IntersectionObserver(entries => {
      // Calculate visible items and update state
    });
    
    return () => observer.disconnect();
  }, []);

  const visibleItems = items.slice(visibleRange.start, visibleRange.end);
  return <ul>{visibleItems.map(item => <li key={item.id}>{item.name}</li>)}</ul>;
}
```

**Use cases:**
- Lists with 100+ items
- Infinite scroll applications
- Data tables with thousands of rows

**Popular libraries:**
- `react-window` - Lightweight virtual scrolling
- `react-virtualized` - Full-featured virtualization

---

## 7. useReducer – Optimize Complex State

Better than multiple `useState` calls for related state.

```jsx
// ❌ Multiple useState - causes multiple renders
function Form() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
}

// ✅ useReducer - single render for all state updates
const initialState = {
  name: '',
  email: '',
  errors: {},
  isSubmitting: false
};

const reducer = (state, action) => {
  switch (action.type) {
    case 'SET_FIELD':
      return { ...state, [action.field]: action.value };
    case 'SET_ERRORS':
      return { ...state, errors: action.errors };
    case 'SET_SUBMITTING':
      return { ...state, isSubmitting: action.value };
    default:
      return state;
  }
};

function Form() {
  const [state, dispatch] = useReducer(reducer, initialState);
  
  const handleChange = (e) => {
    dispatch({ type: 'SET_FIELD', field: e.target.name, value: e.target.value });
  };
}
```

**Advantages:**
- Reduces number of re-renders
- Related state updates in one place
- Easier to test reducer logic

---

## 8. Optimize Dependencies – Fix useEffect Issues

Carefully manage dependency arrays to avoid infinite loops or missed updates.

```jsx
// ❌ Missing dependency - stale closure
useEffect(() => {
  const timer = setTimeout(() => {
    setCount(count + 1); // 'count' is stale
  }, 1000);
}, []); // count not in dependencies

// ✅ Correct dependency
useEffect(() => {
  const timer = setTimeout(() => {
    setCount(count + 1);
  }, 1000);
}, [count]);

// ✅ Better - use functional update
useEffect(() => {
  const timer = setTimeout(() => {
    setCount(prev => prev + 1);
  }, 1000);
}, []); // no dependency needed
```

**Best practices:**
- Include all values that change and are used in effect
- Use functional updates to avoid dependency issues
- Use linter: `eslint-plugin-react-hooks`

---

## 9. Avoid Inline Objects/Functions as Props

These create new references every render.

```jsx
// ❌ Bad - new object every render
<UserCard style={{ color: 'red', fontSize: 14 }} />

// ✅ Good - move outside component
const CARD_STYLE = { color: 'red', fontSize: 14 };
<UserCard style={CARD_STYLE} />

// ❌ Bad - new config every render
<DataTable config={{ sortable: true, pagination: 10 }} />

// ✅ Good - memoize or move outside
const TABLE_CONFIG = useMemo(() => ({
  sortable: true,
  pagination: 10
}), []);
<DataTable config={TABLE_CONFIG} />
```

**Why it matters:**
- New object/function reference breaks memoization
- Causes unnecessary re-renders of memoized children
- Can break strict equality checks

---

## 10. Production Build & Profiling

```bash
# Create optimized production build (minified, optimized)
npm run build

# Development with profiling
npm start

# Using React DevTools Profiler:
# 1. Open React DevTools (Chrome/Firefox extension)
# 2. Go to Profiler tab
# 3. Click Record button
# 4. Interact with your app
# 5. Analyze the recorded interactions
# 6. Look for:
#    - Components that re-render unexpectedly
#    - Renders that take too long
#    - Frequent re-renders
```

**Profiling tips:**
- Profile in production build mode
- Look for unexpected re-renders
- Measure actual performance impact
- Don't optimize prematurely

---

## Performance Checklist

- ✅ Use React.memo for expensive components
- ✅ Use useCallback for callbacks passed to memoized children
- ✅ Use useMemo for expensive computations
- ✅ Code split at route boundaries with lazy()
- ✅ Use virtual lists for 100+ items
- ✅ Provide stable keys (avoid array indices)
- ✅ Avoid inline objects/functions as props
- ✅ Profile with React DevTools Profiler
- ✅ Use production build for deployment
- ✅ Consider server-side rendering (SSR) or static generation (SSG)

---

## General Best Practices

### 1. **Profile First**
Start by profiling to identify actual bottlenecks. Premature optimization wastes time.

### 2. **Measure Impact**
Always measure performance before and after optimization using:
- React DevTools Profiler
- Browser DevTools Performance tab
- Web Vitals metrics (LCP, FID, CLS)

### 3. **Avoid Over-Optimization**
- Not every component needs React.memo
- useCallback/useMemo have their own cost
- Only optimize where it matters

### 4. **Consider Alternatives**
- Sometimes moving state down is better than memoization
- Sometimes breaking into smaller components is better
- Consider context/state management libraries (Redux, Zustand)

### 5. **Watch for Common Pitfalls**
- Empty dependency arrays in useEffect
- Missing dependencies in useCallback/useMemo
- Creating new objects/functions every render
- Inefficient list keys

---

## Additional Resources

- [React Documentation - Performance Optimization](https://react.dev/reference/react/memo)
- [React DevTools Profiler Guide](https://react.dev/learn/react-developer-tools)
- [Web.dev Performance](https://web.dev/performance/)
- [Bundle Analysis Tools](https://www.npmjs.com/package/webpack-bundle-analyzer)

---

**Remember:** Start profiling first to identify actual bottlenecks. Use the React DevTools Profiler to measure before and after changes to ensure your optimizations actually help.
