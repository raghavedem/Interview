# React + TypeScript Cheat Sheet & Study Plan
## Quick Reference + 7-14 Day Learning Schedule

---

## 🎯 QUICK REFERENCE - REACT FUNDAMENTALS

### Component Structure
```typescript
interface ButtonProps {
  label: string;
  onClick?: () => void;
}

const Button: React.FC<ButtonProps> = ({ label, onClick }) => {
  return <button onClick={onClick}>{label}</button>;
};

export default Button;
```

### Hooks Quick Reference
```typescript
// useState
const [count, setCount] = useState<number>(0);

// useEffect (runs after render)
useEffect(() => {
  // Side effect here
  return () => {
    // Cleanup here
  };
}, [dependencies]);

// useReducer (complex state)
const [state, dispatch] = useReducer(reducer, initialState);

// useContext
const value = useContext(MyContext);

// useCallback (memoize function)
const memoFn = useCallback(() => {}, [dependencies]);

// useMemo (memoize value)
const memoValue = useMemo(() => expensiveCalc(), [dependencies]);

// useRef
const inputRef = useRef<HTMLInputElement>(null);
```

### Conditional Rendering
```typescript
// If/else
{isLoading ? <LoadingSpinner /> : <Content />}

// Short circuit
{isReady && <Content />}

// Switch
{(() => {
  switch(status) {
    case 'loading': return <Spinner />;
    case 'error': return <Error />;
    default: return <Success />;
  }
})()}
```

### Lists
```typescript
{items.map(item => (
  <div key={item.id}>
    {item.name}
  </div>
))}
```

### Forms
```typescript
const [email, setEmail] = useState('');

<input
  value={email}
  onChange={(e) => setEmail(e.target.value)}
  type="email"
/>
```

---

## 🎓 7-DAY INTENSIVE STUDY PLAN

### Day 1: TypeScript + React Basics (4 hours)

**Morning Session (2 hours)**
- [ ] Read REACT_README.md overview
- [ ] Study TypeScript types for React
  - React.FC<Props>
  - Event types: React.FormEvent, React.ChangeEvent
  - Children type: React.ReactNode
- [ ] Study functional components
- [ ] Understand props and interfaces

**Afternoon Session (2 hours)**
- [ ] Study useState hook deeply
  - Type inference
  - Initializer functions
  - Functional updates
- [ ] Study useEffect hook
  - Dependency array
  - Cleanup functions
  - Common patterns
- [ ] Write 5 simple components

**Daily Exercises**
- [ ] Create a counter component
- [ ] Create a form component
- [ ] Create a todo list component
- [ ] Understand component composition

---

### Day 2: Hooks Deep Dive (4 hours)

**Morning Session (2 hours)**
- [ ] Study useReducer with TypeScript
  - Type-safe actions
  - Complex state management
  - When to use vs useState
- [ ] Study Custom Hooks
  - Creating reusable logic
  - Return types with generics
  - Best practices

**Afternoon Session (2 hours)**
- [ ] Study useContext
  - Creating contexts
  - Provider pattern
  - Custom context hooks
- [ ] Study memoization
  - React.memo
  - useMemo
  - useCallback

**Daily Exercises**
- [ ] Create useLocalStorage hook
- [ ] Create useFetch hook
- [ ] Create useAsync hook
- [ ] Implement useContext for theme

---

### Day 3: State Management (4 hours)

**Morning Session (2 hours)**
- [ ] Understand state management options
  - Context API
  - Redux
  - Zustand
- [ ] Study Redux with Redux Toolkit
  - createSlice
  - configureStore
  - useSelector, useDispatch

**Afternoon Session (2 hours)**
- [ ] Study Zustand as lightweight alternative
  - Creating store
  - Using hooks
  - Middleware
- [ ] Compare approaches
  - When to use each
  - Trade-offs

**Daily Exercises**
- [ ] Build todo app with useState
- [ ] Refactor with Redux
- [ ] Refactor with Zustand
- [ ] Understand state flow

---

### Day 4: Routing & Advanced Patterns (4 hours)

**Morning Session (2 hours)**
- [ ] Study React Router v6
  - Routes and Route
  - useParams, useNavigate
  - useSearchParams
  - Nested routes
  - Layout routes

**Afternoon Session (2 hours)**
- [ ] Study Code Splitting
  - React.lazy
  - Suspense
  - Dynamic imports
- [ ] Study Error Boundaries
  - When they catch/don't catch errors
  - Fallback UI

**Daily Exercises**
- [ ] Create multi-page app with Router
- [ ] Implement lazy loading
- [ ] Add Error Boundary
- [ ] Implement nested routes

---

### Day 5: Testing (4 hours)

**Morning Session (2 hours)**
- [ ] Study Jest basics
  - Writing tests
  - Assertions
  - Test organization
- [ ] Study React Testing Library
  - Render function
  - screen queries
  - userEvent vs fireEvent

**Afternoon Session (2 hours)**
- [ ] Test strategies
  - What to test
  - Mocking API calls
  - Testing hooks
  - Accessibility testing
- [ ] Write comprehensive tests

**Daily Exercises**
- [ ] Write unit tests for components
- [ ] Mock API calls
- [ ] Test custom hooks
- [ ] Test user interactions

---

### Day 6: Styling & Performance (4 hours)

**Morning Session (2 hours)**
- [ ] Study Tailwind CSS
  - Utility classes
  - Component patterns
  - Configuration
- [ ] Study Styled Components
  - Tagged templates
  - Props-based styling
  - Theming

**Afternoon Session (2 hours)**
- [ ] Study Performance Optimization
  - Profiling
  - Code splitting
  - Lazy loading
  - Image optimization
- [ ] Study Core Web Vitals
  - LCP, FID, CLS
  - Measuring performance

**Daily Exercises**
- [ ] Style app with Tailwind
- [ ] Style app with Styled Components
- [ ] Profile performance
- [ ] Optimize bundle size

---

### Day 7: Integration & Interview Prep (5 hours)

**Morning Session (2 hours)**
- [ ] Review all concepts
- [ ] Study interview questions
- [ ] Practice explaining concepts

**Afternoon Session (3 hours)**
- [ ] Build small complete project
- [ ] Do mock interview
- [ ] Review weak areas
- [ ] Practice coding

---

## 📚 14-DAY STANDARD STUDY PLAN

### Week 1: Fundamentals & Hooks

**Days 1-2: TypeScript + React Basics (3 hours/day)**
- Fundamentals file thoroughly
- Types, interfaces, generics
- Function components
- Props and composition
- Practice: 10+ simple components

**Days 3-4: Hooks In-Depth (3 hours/day)**
- useState, useEffect, useReducer
- useContext, useCallback, useMemo
- Custom hooks
- Practice: 5+ custom hooks

**Days 5-6: State Management (3 hours/day)**
- Redux with TypeScript
- Zustand as alternative
- When to use each
- Practice: Refactor app with different approaches

**Day 7: Review & Practice (2 hours)**
- Weekly review quiz
- Practice coding
- Identify weak areas

### Week 2: Advanced & Production

**Days 8-9: Routing & Advanced (3 hours/day)**
- React Router v6
- Code splitting & lazy loading
- Error boundaries
- Practice: Multi-page application

**Days 10-11: Testing & Quality (3 hours/day)**
- Jest + React Testing Library
- Component and hook testing
- Mocking strategies
- Practice: 80%+ test coverage

**Days 12-13: Styling & Performance (3 hours/day)**
- Tailwind CSS
- Styled Components
- Performance monitoring
- Practice: Style complete app

**Day 14: Complete Project (4 hours)**
- Build end-to-end application
- All concepts integrated
- Fully tested
- Production-ready

---

## 🎯 LEARNING OUTCOMES BY DAY

### After Day 1
- [ ] Understand TypeScript with React
- [ ] Can write simple components
- [ ] Know basic hooks
- [ ] Understand props

### After Day 2
- [ ] Expert in hooks
- [ ] Can create custom hooks
- [ ] Understand Context API
- [ ] Know performance optimization

### After Day 3
- [ ] Expert in state management
- [ ] Choose appropriate tool
- [ ] Understand trade-offs
- [ ] Can refactor complex state

### After Day 4
- [ ] Can build multi-page apps
- [ ] Understand code splitting
- [ ] Know error handling
- [ ] Expert in routing

### After Day 5
- [ ] Can test comprehensively
- [ ] Understand testing strategies
- [ ] Know how to mock
- [ ] Can reach 80%+ coverage

### After Day 6
- [ ] Can style efficiently
- [ ] Know performance best practices
- [ ] Can optimize bundle
- [ ] Understand Web Vitals

### After Day 7+
- [ ] Ready for interviews
- [ ] Can build production apps
- [ ] Expert-level knowledge
- [ ] Confident in abilities

---

## 📝 DAILY CHECKLIST TEMPLATE

### Each Day Should Include

**Theory (30%)**
- [ ] Read relevant sections
- [ ] Understand concepts
- [ ] Note key points
- [ ] Review cheat sheet

**Practice (40%)**
- [ ] Run code examples
- [ ] Write your own code
- [ ] Modify examples
- [ ] Build mini-projects

**Testing (20%)**
- [ ] Write tests
- [ ] Test your code
- [ ] Debug issues
- [ ] Understand errors

**Review (10%)**
- [ ] Summarize learning
- [ ] Answer questions
- [ ] Plan next steps
- [ ] Fill knowledge gaps

---

## 🏆 SUCCESS METRICS

### Beginner Level
- Can write simple components
- Understand useState
- Know basic hooks
- Can handle events

### Intermediate Level
- Expert in all hooks
- Create custom hooks
- Understand state management
- Can write tests

### Advanced Level
- Optimize performance
- Design complex apps
- Implement best practices
- Ready for senior role

---

## 📋 STUDY RESOURCES

### Code Examples Provided
- 3 main TSX files (3,000+ lines)
- 30+ working examples
- 40+ interview questions
- Complete patterns

### Your Study Materials
- react_01_fundamentals.tsx - Start here
- react_02_advanced_patterns.tsx - After fundamentals
- react_03_testing_styling.tsx - For production readiness
- REACT_CHEAT_SHEET.md - Quick reference
- REACT_README.md - Detailed guide

---

## ✅ COMPLETION CHECKLIST

### Learning Phase
- [ ] Read all code files
- [ ] Run all examples
- [ ] Modify at least 10 examples
- [ ] Understand each concept deeply

### Practice Phase
- [ ] Write 5+ custom components
- [ ] Create 3+ custom hooks
- [ ] Build 2+ multi-page apps
- [ ] Implement state management

### Testing Phase
- [ ] Write 20+ tests
- [ ] Test components
- [ ] Test hooks
- [ ] Test integrations

### Production Phase
- [ ] Build complete project
- [ ] Achieve 80%+ test coverage
- [ ] Optimize performance
- [ ] Deploy application

### Interview Phase
- [ ] Answer all questions
- [ ] Do mock interviews
- [ ] Review weak areas
- [ ] Confident in abilities

---

## 🚀 WHAT'S NEXT

### Week After Course
- [ ] Deploy project
- [ ] Add more features
- [ ] Code review
- [ ] Contribute to open source

### Month After Course
- [ ] Learn Next.js
- [ ] Learn GraphQL
- [ ] Build larger project
- [ ] Interview practice

### 3 Months After Course
- [ ] Expert-level projects
- [ ] System design knowledge
- [ ] Advanced patterns
- [ ] Mentor others

---

## 💬 REMEMBER

> "Learning React is not just about knowing the syntax. 
> It's about understanding when and why to use each pattern 
> to build maintainable, performant applications."

Focus on:
1. **Understanding** - Why, not just how
2. **Practice** - Write real code
3. **Testing** - Ensure quality
4. **Performance** - Optimize constantly
5. **Best Practices** - Follow conventions

---

**You've got this! 🎉**

*Last Updated: 2024*
*React 18+ | TypeScript 5+*
