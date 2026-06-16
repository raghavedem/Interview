"""
ADVANCED REACT + TYPESCRIPT PATTERNS
Topics:
- Advanced state management with Redux/Zustand
- React Router for navigation
- Advanced hook patterns
- Code splitting and lazy loading
- Error boundaries
- Server-side rendering concepts
- Performance optimization techniques
"""

# Structure overview for advanced React patterns

ADVANCED_REACT_PATTERNS = """

// ============================================================================
// 1. REDUX WITH TYPESCRIPT
// ============================================================================

import { createSlice, configureStore, PayloadAction } from '@reduxjs/toolkit';
import { RootState, AppDispatch } from './store';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';

// Define state type
interface User {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'user';
}

interface UsersState {
  items: User[];
  loading: boolean;
  error: string | null;
  selectedId: number | null;
}

const initialState: UsersState = {
  items: [],
  loading: false,
  error: null,
  selectedId: null,
};

// Create slice with reducers
const usersSlice = createSlice({
  name: 'users',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setUsers: (state, action: PayloadAction<User[]>) => {
      state.items = action.payload;
      state.error = null;
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.loading = false;
    },
    selectUser: (state, action: PayloadAction<number>) => {
      state.selectedId = action.payload;
    },
    addUser: (state, action: PayloadAction<User>) => {
      state.items.push(action.payload);
    },
    deleteUser: (state, action: PayloadAction<number>) => {
      state.items = state.items.filter((user) => user.id !== action.payload);
    },
  },
});

// Async thunks
export const fetchUsers = async (dispatch: AppDispatch): Promise<void> => {
  dispatch(usersSlice.actions.setLoading(true));
  try {
    const response = await fetch('/api/users');
    const users: User[] = await response.json();
    dispatch(usersSlice.actions.setUsers(users));
  } catch (error) {
    dispatch(
      usersSlice.actions.setError(
        error instanceof Error ? error.message : 'Unknown error'
      )
    );
  }
};

// Store configuration
export const store = configureStore({
  reducer: {
    users: usersSlice.reducer,
  },
});

// Export types
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Custom hooks for typed Redux
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// Component using Redux
const UsersList: React.FC = () => {
  const dispatch = useAppDispatch();
  const { items, loading, error } = useAppSelector((state) => state.users);

  React.useEffect(() => {
    fetchUsers(dispatch);
  }, [dispatch]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      {items.map((user) => (
        <div key={user.id}>
          <h3>{user.name}</h3>
          <p>{user.email}</p>
        </div>
      ))}
    </div>
  );
};

// ============================================================================
// 2. ZUSTAND STATE MANAGEMENT (LIGHTWEIGHT ALTERNATIVE)
// ============================================================================

import create from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { devtools } from 'zustand/middleware/devtools';

interface Product {
  id: number;
  name: string;
  price: number;
  quantity: number;
}

interface CartStore {
  items: Product[];
  total: number;
  addItem: (product: Product) => void;
  removeItem: (id: number) => void;
  updateQuantity: (id: number, quantity: number) => void;
  clearCart: () => void;
}

// Zustand store with TypeScript
export const useCartStore = create<CartStore>()(
  devtools(
    immer((set) => ({
      items: [],
      total: 0,
      
      addItem: (product: Product) =>
        set((state) => {
          const existing = state.items.find((item) => item.id === product.id);
          if (existing) {
            existing.quantity += 1;
          } else {
            state.items.push(product);
          }
          state.total = state.items.reduce(
            (sum, item) => sum + item.price * item.quantity,
            0
          );
        }),

      removeItem: (id: number) =>
        set((state) => {
          const item = state.items.find((i) => i.id === id);
          if (item) {
            state.total -= item.price * item.quantity;
          }
          state.items = state.items.filter((i) => i.id !== id);
        }),

      updateQuantity: (id: number, quantity: number) =>
        set((state) => {
          const item = state.items.find((i) => i.id === id);
          if (item && quantity > 0) {
            item.quantity = quantity;
          }
          state.total = state.items.reduce(
            (sum, item) => sum + item.price * item.quantity,
            0
          );
        }),

      clearCart: () =>
        set((state) => {
          state.items = [];
          state.total = 0;
        }),
    }))
  )
);

// Component using Zustand
const CartComponent: React.FC = () => {
  const { items, total, addItem, removeItem } = useCartStore();

  return (
    <div>
      <h1>Cart - \${total.toFixed(2)}</h1>
      {items.map((item) => (
        <div key={item.id}>
          <span>{item.name}</span>
          <button onClick={() => removeItem(item.id)}>Remove</button>
        </div>
      ))}
    </div>
  );
};

// ============================================================================
// 3. REACT ROUTER WITH TYPESCRIPT
// ============================================================================

import {
  BrowserRouter,
  Routes,
  Route,
  Link,
  useParams,
  useNavigate,
  useSearchParams,
} from 'react-router-dom';

interface UserParams {
  userId: string;
}

// Route components
const HomePage: React.FC = () => <h1>Home</h1>;

const UserDetailPage: React.FC = () => {
  const { userId } = useParams<UserParams>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const tab = searchParams.get('tab') || 'profile';

  return (
    <div>
      <h1>User {userId}</h1>
      <p>Current tab: {tab}</p>
      <button onClick={() => navigate('/users')}>Back to Users</button>
    </div>
  );
};

const NotFoundPage: React.FC = () => <h1>404 - Not Found</h1>;

// Router configuration
const AppRouter: React.FC = () => {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/">Home</Link>
        <Link to="/users">Users</Link>
      </nav>

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/users/:userId" element={<UserDetailPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
};

// ============================================================================
// 4. ERROR BOUNDARY
// ============================================================================

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: (error: Error) => React.ReactNode;
}

class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    console.error('Error caught by boundary:', error, errorInfo);
    // Log to error reporting service
  }

  render(): React.ReactNode {
    if (this.state.hasError && this.state.error) {
      return (
        this.props.fallback?.(this.state.error) || (
          <div>
            <h1>Something went wrong</h1>
            <p>{this.state.error.message}</p>
          </div>
        )
      );
    }

    return this.props.children;
  }
}

// Usage
const App: React.FC = () => {
  return (
    <ErrorBoundary
      fallback={(error) => (
        <div style={{ padding: '20px', color: 'red' }}>
          <h2>Application Error</h2>
          <p>{error.message}</p>
        </div>
      )}
    >
      <UsersList />
    </ErrorBoundary>
  );
};

// ============================================================================
// 5. CODE SPLITTING & LAZY LOADING
// ============================================================================

import { Suspense, lazy } from 'react';

// Lazy load components
const HeavyComponent = lazy(() => import('./HeavyComponent'));
const AdminPanel = lazy(() => import('./AdminPanel'));

const LazyApp: React.FC = () => {
  const [showHeavy, setShowHeavy] = React.useState(false);

  return (
    <div>
      <button onClick={() => setShowHeavy(!showHeavy)}>
        Toggle Heavy Component
      </button>

      <Suspense fallback={<div>Loading component...</div>}>
        {showHeavy && <HeavyComponent />}
      </Suspense>

      {/* In router */}
      <Routes>
        <Route
          path="/admin"
          element={
            <Suspense fallback={<div>Loading admin panel...</div>}>
              <AdminPanel />
            </Suspense>
          }
        />
      </Routes>
    </div>
  );
};

// ============================================================================
// 6. ADVANCED HOOK PATTERNS
// ============================================================================

// useAsync - Handle async operations
interface UseAsyncState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

const useAsync = <T,>(
  asyncFunction: () => Promise<T>,
  immediate = true
): UseAsyncState<T> & { execute: () => Promise<void> } => {
  const [state, setState] = React.useState<UseAsyncState<T>>({
    data: null,
    loading: immediate,
    error: null,
  });

  const execute = React.useCallback(async (): Promise<void> => {
    setState({ data: null, loading: true, error: null });
    try {
      const response = await asyncFunction();
      setState({ data: response, loading: false, error: null });
    } catch (error) {
      setState({
        data: null,
        loading: false,
        error: error instanceof Error ? error : new Error('Unknown error'),
      });
    }
  }, [asyncFunction]);

  React.useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [execute, immediate]);

  return { ...state, execute };
};

// useDebounce - Debounce value changes
const useDebounce = <T,>(value: T, delay: number = 500): T => {
  const [debouncedValue, setDebouncedValue] = React.useState<T>(value);

  React.useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
};

// Usage
const SearchUsers: React.FC = () => {
  const [search, setSearch] = React.useState('');
  const debouncedSearch = useDebounce(search, 300);

  const { data: results, loading } = useAsync(
    () => fetch(`/api/search?q=\${debouncedSearch}`).then((r) => r.json()),
    !!debouncedSearch
  );

  return (
    <div>
      <input
        type="text"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search users..."
      />
      {loading && <p>Searching...</p>}
      {results && <ul>{/* render results */}</ul>}
    </div>
  );
};

// ============================================================================
// 7. PERFORMANCE OPTIMIZATION - VIRTUALIZATION
// ============================================================================

import { FixedSizeList as List } from 'react-window';

interface Item {
  id: number;
  name: string;
}

interface VirtualListProps {
  items: Item[];
}

const VirtualList: React.FC<VirtualListProps> = ({ items }) => {
  const itemSize = 50;
  const height = 400;

  const Row: React.FC<{ index: number; style: React.CSSProperties }> = ({
    index,
    style,
  }) => (
    <div style={style} className="list-item">
      {items[index].name}
    </div>
  );

  return (
    <List
      height={height}
      itemCount={items.length}
      itemSize={itemSize}
      width="100%"
    >
      {Row}
    </List>
  );
};

// ============================================================================
// 8. FORM HANDLING WITH REACT-HOOK-FORM & TYPESCRIPT
// ============================================================================

import { useForm, SubmitHandler, Controller } from 'react-hook-form';

interface LoginFormInputs {
  email: string;
  password: string;
  rememberMe: boolean;
}

const LoginForm: React.FC = () => {
  const { register, handleSubmit, formState: { errors }, control } = useForm<LoginFormInputs>(
    {
      defaultValues: {
        email: '',
        password: '',
        rememberMe: false,
      },
    }
  );

  const onSubmit: SubmitHandler<LoginFormInputs> = async (data) => {
    console.log('Form data:', data);
    // API call
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input
        {...register('email', {
          required: 'Email is required',
          pattern: {
            value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}$/i,
            message: 'Invalid email address',
          },
        })}
        type="email"
        placeholder="Email"
      />
      {errors.email && <span>{errors.email.message}</span>}

      <input
        {...register('password', {
          required: 'Password is required',
          minLength: { value: 8, message: 'Min 8 characters' },
        })}
        type="password"
        placeholder="Password"
      />
      {errors.password && <span>{errors.password.message}</span>}

      <button type="submit">Login</button>
    </form>
  );
};

// ============================================================================
// 9. TESTING REACT COMPONENTS WITH TYPESCRIPT
// ============================================================================

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

// Component test example
describe('UserProfile', () => {
  it('should display user information', async () => {
    const mockUser = {
      id: 1,
      name: 'John Doe',
      email: 'john@example.com',
    };

    render(<UserProfile userId={1} />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('john@example.com')).toBeInTheDocument();
    });
  });

  it('should call onDelete when delete button is clicked', () => {
    const mockOnDelete = jest.fn();
    render(
      <User
        id={1}
        name="John"
        email="john@example.com"
        role="user"
        isActive={true}
        onDelete={mockOnDelete}
      />
    );

    const deleteButton = screen.getByText('Delete');
    fireEvent.click(deleteButton);

    expect(mockOnDelete).toHaveBeenCalledWith(1);
  });
});

// ============================================================================
// 10. CONCURRENT FEATURES (React 18+)
// ============================================================================

import { useTransition, useDeferredValue } from 'react';

const SearchWithTransition: React.FC = () => {
  const [input, setInput] = React.useState('');
  const [isPending, startTransition] = useTransition();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const value = e.target.value;
    
    // Mark update as non-urgent
    startTransition(() => {
      setInput(value);
      // Expensive update here
    });
  };

  return (
    <div>
      <input value={input} onChange={handleChange} />
      {isPending && <p>Searching...</p>}
    </div>
  );
};

// useDeferredValue - Defer expensive computations
const SearchResults: React.FC<{ query: string }> = ({ query }) => {
  const deferredQuery = useDeferredValue(query);
  const results = filterExpensively(deferredQuery);

  return (
    <div>
      <h2>Results for: {query}</h2>
      {query !== deferredQuery && <p>Updating results...</p>}
      <ul>
        {results.map((result) => (
          <li key={result.id}>{result.name}</li>
        ))}
      </ul>
    </div>
  );
};

// ============================================================================
// INTERVIEW QUESTIONS - ADVANCED
// ============================================================================

/*
Q1: What's the difference between Redux and Zustand?
A: Redux: Predictable, centralized, boilerplate-heavy, great for large apps
   Zustand: Simple, lightweight, less boilerplate, great for medium apps
   Choose: Redux for enterprise, Zustand for startups/smaller projects

Q2: Explain code splitting and lazy loading in React.
A: Code splitting: Split bundle into smaller chunks
   Lazy loading: Load components only when needed
   Use React.lazy() + Suspense
   Benefits: Faster initial load, better performance

Q3: What's an Error Boundary and when to use it?
A: Class component that catches JavaScript errors
   Shows fallback UI instead of crashing entire app
   Doesn't catch: Event handlers (use try/catch), async code, SSR
   Use: Wrap critical sections, handle unexpected errors

Q4: Explain useTransition and concurrent rendering.
A: useTransition: Mark updates as non-urgent
   Allows React to interrupt work for urgent updates
   Improves responsiveness for slow devices
   Use for: Heavy computations, background tasks

Q5: What's the difference between controlled and uncontrolled form inputs?
A: Controlled: Value in React state, updated via onChange
   Uncontrolled: Value in DOM, accessed via refs
   Controlled: Better for validation, complex forms
   Uncontrolled: Simpler, better for file inputs

Q6: How do you handle async operations in Redux?
A: Redux Thunk: Return function from action creator
   Redux Saga: Side effect management with generators
   Redux Toolkit: createAsyncThunk (recommended)
   Use: For API calls, timers, side effects

Q7: Explain useCallback and useMemo - when to use?
A: useCallback: Memoize callback functions (pass to child components)
   useMemo: Memoize computed values (expensive calculations)
   When: Child uses callback in useEffect/dependency
   Don't: Overuse, measure performance first

Q8: What's the difference between React Router v5 and v6?
A: v6: <Routes> instead of <Switch>, useNavigate instead of useHistory
   v6: Better TypeScript support, simpler API, better performance
   v6: Relative routes, layout routes, better error handling
   Migrate: Use codemods for automatic updates

Q9: How to test async components in React?
A: Use waitFor() to wait for async operations
   Use act() to wrap state updates
   Mock fetch/axios with jest.mock()
   Test: Loading state, success state, error state

Q10: Explain Server-Side Rendering (SSR) with React.
A: Render React on server, send HTML to client
   Benefits: Better SEO, faster initial load, better perceived performance
   Frameworks: Next.js (recommended), Gatsby, Remix
   Trade-offs: More complex, server resources, hydration issues
*/

export {
  usersSlice,
  fetchUsers,
  store,
  useAppDispatch,
  useAppSelector,
  UsersList,
  useCartStore,
  CartComponent,
  AppRouter,
  ErrorBoundary,
  App,
  LazyApp,
  useAsync,
  useDebounce,
  SearchUsers,
  VirtualList,
  LoginForm,
  SearchWithTransition,
  SearchResults,
};
"""

print("Advanced React patterns created")
print("Topics covered:")
print("- Redux with Redux Toolkit and TypeScript")
print("- Zustand as lightweight alternative")
print("- React Router v6 with TypeScript")
print("- Error boundaries for error handling")
print("- Code splitting and lazy loading")
print("- Advanced hooks: useAsync, useDebounce")
print("- Virtualization for large lists")
print("- Form handling with react-hook-form")
print("- Testing React components")
print("- Concurrent features (React 18+)")
print("- 10 advanced interview questions")
