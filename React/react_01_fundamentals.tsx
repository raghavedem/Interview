"""
REACT + TYPESCRIPT FUNDAMENTALS
Complete guide to building production-ready React applications with TypeScript

Topics:
- React hooks and component patterns
- TypeScript types and interfaces
- State management with useState, useReducer
- Side effects with useEffect
- Context API for global state
- Custom hooks
- Component composition and reusability
"""

import json

# This file would be written in TypeScript/JSX
# Below is the structure and explanation

REACT_TYPESCRIPT_FUNDAMENTALS = """
// ============================================================================
// 1. TYPESCRIPT TYPES & INTERFACES FOR REACT
// ============================================================================

// Basic types
type Props = {
  name: string;
  age: number;
  active?: boolean; // Optional
};

// Function component type
type FC<P = {}> = React.FC<P>;

// Component with children
type WithChildren<P = {}> = P & {
  children: React.ReactNode;
};

// Union types for complex states
type Status = 'idle' | 'loading' | 'success' | 'error';

// ============================================================================
// 2. FUNCTIONAL COMPONENTS & TYPESCRIPT
// ============================================================================

interface UserProps {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'moderator';
  isActive: boolean;
  onDelete?: (id: number) => void;
}

const User: React.FC<UserProps> = ({
  id,
  name,
  email,
  role,
  isActive,
  onDelete,
}) => {
  return (
    <div className="user">
      <h2>{name}</h2>
      <p>Email: {email}</p>
      <p>Role: {role}</p>
      <p>Status: {isActive ? 'Active' : 'Inactive'}</p>
      {onDelete && (
        <button onClick={() => onDelete(id)}>Delete</button>
      )}
    </div>
  );
};

// ============================================================================
// 3. USESTATE HOOK WITH TYPESCRIPT
// ============================================================================

interface Task {
  id: number;
  title: string;
  completed: boolean;
  createdAt: Date;
}

const TodoApp: React.FC = () => {
  // Explicit type for state
  const [tasks, setTasks] = React.useState<Task[]>([]);
  const [input, setInput] = React.useState<string>('');
  const [filter, setFilter] = React.useState<'all' | 'active' | 'completed'>('all');
  const [count, setCount] = React.useState<number>(0);

  // Type-safe event handlers
  const handleAddTask = (e: React.FormEvent<HTMLFormElement>): void => {
    e.preventDefault();
    if (!input.trim()) return;

    const newTask: Task = {
      id: Date.now(),
      title: input,
      completed: false,
      createdAt: new Date(),
    };

    setTasks([...tasks, newTask]);
    setInput('');
  };

  const handleToggleTask = (id: number): void => {
    setTasks(
      tasks.map((task) =>
        task.id === id ? { ...task, completed: !task.completed } : task
      )
    );
  };

  const handleDeleteTask = (id: number): void => {
    setTasks(tasks.filter((task) => task.id !== id));
  };

  // Filter tasks
  const filteredTasks = tasks.filter((task) => {
    if (filter === 'active') return !task.completed;
    if (filter === 'completed') return task.completed;
    return true;
  });

  return (
    <div className="todo-app">
      <h1>Todo App</h1>
      <form onSubmit={handleAddTask}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.currentTarget.value)}
          placeholder="Add a task..."
        />
        <button type="submit">Add</button>
      </form>

      <div className="filters">
        {(['all', 'active', 'completed'] as const).map((filterType) => (
          <button
            key={filterType}
            onClick={() => setFilter(filterType)}
            className={filter === filterType ? 'active' : ''}
          >
            {filterType.charAt(0).toUpperCase() + filterType.slice(1)}
          </button>
        ))}
      </div>

      <ul>
        {filteredTasks.map((task) => (
          <li key={task.id}>
            <input
              type="checkbox"
              checked={task.completed}
              onChange={() => handleToggleTask(task.id)}
            />
            <span
              style={{
                textDecoration: task.completed ? 'line-through' : 'none',
              }}
            >
              {task.title}
            </span>
            <button onClick={() => handleDeleteTask(task.id)}>Delete</button>
          </li>
        ))}
      </ul>

      <p>
        Total: {tasks.length} | Completed: {tasks.filter((t) => t.completed).length}
      </p>
    </div>
  );
};

// ============================================================================
// 4. USEREDUCER FOR COMPLEX STATE
// ============================================================================

interface ShoppingCart {
  items: CartItem[];
  total: number;
  count: number;
}

interface CartItem {
  id: number;
  name: string;
  price: number;
  quantity: number;
}

type CartAction =
  | { type: 'ADD_ITEM'; payload: CartItem }
  | { type: 'REMOVE_ITEM'; payload: number }
  | { type: 'UPDATE_QUANTITY'; payload: { id: number; quantity: number } }
  | { type: 'CLEAR_CART' };

const initialCart: ShoppingCart = {
  items: [],
  total: 0,
  count: 0,
};

const cartReducer = (
  state: ShoppingCart,
  action: CartAction
): ShoppingCart => {
  switch (action.type) {
    case 'ADD_ITEM': {
      const existingItem = state.items.find((item) => item.id === action.payload.id);

      if (existingItem) {
        return {
          ...state,
          items: state.items.map((item) =>
            item.id === action.payload.id
              ? { ...item, quantity: item.quantity + 1 }
              : item
          ),
          count: state.count + 1,
          total: state.total + action.payload.price,
        };
      }

      return {
        ...state,
        items: [...state.items, action.payload],
        count: state.count + 1,
        total: state.total + action.payload.price,
      };
    }

    case 'REMOVE_ITEM': {
      const item = state.items.find((i) => i.id === action.payload);
      if (!item) return state;

      return {
        ...state,
        items: state.items.filter((i) => i.id !== action.payload),
        count: state.count - item.quantity,
        total: state.total - item.price * item.quantity,
      };
    }

    case 'UPDATE_QUANTITY': {
      const item = state.items.find((i) => i.id === action.payload.id);
      if (!item) return state;

      const quantityDiff = action.payload.quantity - item.quantity;
      const priceDiff = item.price * quantityDiff;

      return {
        ...state,
        items: state.items.map((i) =>
          i.id === action.payload.id
            ? { ...i, quantity: action.payload.quantity }
            : i
        ),
        count: state.count + quantityDiff,
        total: state.total + priceDiff,
      };
    }

    case 'CLEAR_CART':
      return initialCart;

    default:
      return state;
  }
};

const ShoppingCartApp: React.FC = () => {
  const [cart, dispatch] = React.useReducer(cartReducer, initialCart);

  const handleAddItem = (item: CartItem): void => {
    dispatch({ type: 'ADD_ITEM', payload: item });
  };

  const handleRemoveItem = (id: number): void => {
    dispatch({ type: 'REMOVE_ITEM', payload: id });
  };

  return (
    <div className="shopping-cart">
      <h1>Shopping Cart</h1>
      <p>Items: {cart.count} | Total: \${cart.total.toFixed(2)}</p>
      {/* Item list and actions */}
    </div>
  );
};

// ============================================================================
// 5. USEEFFECT FOR SIDE EFFECTS
// ============================================================================

interface ApiResponse<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

interface Post {
  id: number;
  title: string;
  body: string;
  userId: number;
}

const PostList: React.FC = () => {
  const [posts, setPosts] = React.useState<Post[]>([]);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [error, setError] = React.useState<Error | null>(null);

  // Fetch posts on mount
  React.useEffect(() => {
    const fetchPosts = async (): Promise<void> => {
      try {
        setLoading(true);
        const response = await fetch('https://jsonplaceholder.typicode.com/posts');
        if (!response.ok) throw new Error('Failed to fetch');
        const data: Post[] = await response.json();
        setPosts(data.slice(0, 10)); // Get first 10
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Unknown error'));
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, []); // Empty dependency array = run once on mount

  // Cleanup example
  React.useEffect(() => {
    const handleResize = (): void => {
      console.log('Window resized');
    };

    window.addEventListener('resize', handleResize);

    // Cleanup function - runs before unmount
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h1>Posts</h1>
      {posts.map((post) => (
        <article key={post.id}>
          <h2>{post.title}</h2>
          <p>{post.body}</p>
        </article>
      ))}
    </div>
  );
};

// ============================================================================
// 6. CONTEXT API FOR GLOBAL STATE
// ============================================================================

interface User {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'user';
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = React.createContext<AuthContextType | undefined>(undefined);

const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = React.useState<User | null>(null);
  const [loading, setLoading] = React.useState<boolean>(true);

  React.useEffect(() => {
    // Check if user is logged in on mount
    const checkAuth = async (): Promise<void> => {
      try {
        const response = await fetch('/api/me');
        if (response.ok) {
          const userData: User = await response.json();
          setUser(userData);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (email: string, password: string): Promise<void> => {
    setLoading(true);
    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) throw new Error('Login failed');

      const userData: User = await response.json();
      setUser(userData);
    } finally {
      setLoading(false);
    }
  };

  const logout = (): void => {
    setUser(null);
    localStorage.removeItem('token');
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    login,
    logout,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

const useAuth = (): AuthContextType => {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

// Usage in component
const Dashboard: React.FC = () => {
  const { user, logout, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <div>Please log in</div>;
  }

  return (
    <div>
      <h1>Welcome, {user?.name}</h1>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

// ============================================================================
// 7. CUSTOM HOOKS WITH TYPESCRIPT
// ============================================================================

// useLocalStorage hook
const useLocalStorage = <T,>(
  key: string,
  initialValue: T
): [T, (value: T | ((val: T) => T)) => void] => {
  const [storedValue, setStoredValue] = React.useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(error);
      return initialValue;
    }
  });

  const setValue = (value: T | ((val: T) => T)): void => {
    try {
      const valueToStore =
        value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(error);
    }
  };

  return [storedValue, setValue];
};

// useFetch hook
interface UseFetchOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  headers?: Record<string, string>;
  body?: any;
}

const useFetch = <T,>(
  url: string,
  options?: UseFetchOptions
): ApiResponse<T> & { refetch: () => Promise<void> } => {
  const [data, setData] = React.useState<T | null>(null);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [error, setError] = React.useState<Error | null>(null);

  const refetch = React.useCallback(async (): Promise<void> => {
    setLoading(true);
    try {
      const response = await fetch(url, options);
      if (!response.ok) throw new Error('Fetch failed');
      const result: T = await response.json();
      setData(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setLoading(false);
    }
  }, [url, options]);

  React.useEffect(() => {
    refetch();
  }, [refetch]);

  return { data, loading, error, refetch };
};

// Usage
const UserProfile: React.FC<{ userId: number }> = ({ userId }) => {
  const { data: user, loading, error, refetch } = useFetch<User>(
    `/api/users/\${userId}`
  );

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h1>{user?.name}</h1>
      <p>{user?.email}</p>
      <button onClick={() => refetch()}>Refresh</button>
    </div>
  );
};

// ============================================================================
// 8. COMPONENT COMPOSITION
// ============================================================================

// Button component
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'small' | 'medium' | 'large';
  loading?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'medium', loading = false, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={`btn btn-\${variant} btn-\${size}`}
        disabled={loading || props.disabled}
        {...props}
      >
        {loading ? 'Loading...' : props.children}
      </button>
    );
  }
);

// Form component
interface FormProps<T> {
  initialValues: T;
  onSubmit: (values: T) => Promise<void> | void;
  children: (
    values: T,
    errors: Record<string, string>,
    handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void,
    isSubmitting: boolean
  ) => React.ReactNode;
}

const Form = <T extends Record<string, any>>({
  initialValues,
  onSubmit,
  children,
}: FormProps<T>): React.ReactElement => {
  const [values, setValues] = React.useState<T>(initialValues);
  const [errors, setErrors] = React.useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = React.useState<boolean>(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const { name, value } = e.target;
    setValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onSubmit(values);
    } catch (error) {
      setErrors({
        submit: error instanceof Error ? error.message : 'An error occurred',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {children(values, errors, handleChange, isSubmitting)}
    </form>
  );
};

// ============================================================================
// 9. MEMOIZATION & PERFORMANCE
// ============================================================================

interface ItemProps {
  item: CartItem;
  onUpdate: (id: number, quantity: number) => void;
  onRemove: (id: number) => void;
}

// Memoized component - prevents re-renders if props haven't changed
const CartItemComponent = React.memo<ItemProps>(
  ({ item, onUpdate, onRemove }) => {
    console.log('Rendering CartItem:', item.id);

    return (
      <div className="cart-item">
        <h3>{item.name}</h3>
        <p>\${item.price}</p>
        <input
          type="number"
          value={item.quantity}
          onChange={(e) => onUpdate(item.id, parseInt(e.target.value))}
          min="1"
        />
        <button onClick={() => onRemove(item.id)}>Remove</button>
      </div>
    );
  }
);

// useMemo - memoize expensive calculations
const ShoppingCart2: React.FC<{ items: CartItem[] }> = ({ items }) => {
  const total = React.useMemo(
    () => items.reduce((sum, item) => sum + item.price * item.quantity, 0),
    [items]
  );

  return (
    <div>
      <h1>Total: \${total.toFixed(2)}</h1>
    </div>
  );
};

// useCallback - memoize callback functions
const ItemList: React.FC<{ items: CartItem[] }> = ({ items }) => {
  const [cart, setCart] = React.useState<CartItem[]>([]);

  const handleAddItem = React.useCallback(
    (item: CartItem): void => {
      setCart((prev) => [...prev, item]);
    },
    []
  );

  return (
    <div>
      {items.map((item) => (
        <CartItemComponent
          key={item.id}
          item={item}
          onUpdate={(id, quantity) => {}}
          onRemove={(id) => {}}
        />
      ))}
    </div>
  );
};

// ============================================================================
// INTERVIEW QUESTIONS
// ============================================================================

/*
Q1: What are the differences between useState and useReducer?
A: useState: For simple state. useReducer: For complex state with multiple actions.
   useState: Multiple state variables. useReducer: Single reducer function.
   When to use: useState for simple, useReducer for complex interdependent state.

Q2: Explain the useEffect cleanup function.
A: Runs before component unmounts or effect runs again.
   Used to prevent memory leaks (remove listeners, cancel requests).
   Return a function from useEffect for cleanup.

Q3: What's the Context API and when to use it?
A: Allows passing data deep through component tree without prop drilling.
   Avoid: Overusing context (creates unnecessary re-renders).
   Use: Global state (auth, theme), configuration, language settings.

Q4: How to optimize React performance?
A: - React.memo for components
   - useMemo for expensive calculations
   - useCallback for stable function references
   - Code splitting and lazy loading
   - Proper key prop in lists

Q5: What are controlled vs uncontrolled components?
A: Controlled: Value managed by React state. Uncontrolled: Value in DOM.
   Controlled: Better for validation and real-time updates.
   Uncontrolled: Simpler for simple forms, file inputs.

Q6: Explain TypeScript generics in React.
A: <T> allows creating reusable components with type safety.
   Example: const useFetch<T> works with any data type.
   Benefits: Type safety, intellisense, catch errors at compile time.

Q7: What's the difference between class and functional components?
A: Functional: Simpler, use hooks. Class: More verbose, lifecycle methods.
   Modern React: Use functional components and hooks.
   Class components: Still supported but not recommended.

Q8: How to handle forms in React with TypeScript?
A: - Use useRef for uncontrolled inputs
   - Use useState for controlled inputs
   - Type form events: React.FormEvent<HTMLFormElement>
   - Validate before submission
   - Show error messages

Q9: What's the key prop in lists and why important?
A: Unique identifier for each list item. Helps React identify which items changed.
   Without it: Re-renders entire list, state gets mixed up.
   Use: Unique ID from data, not array index.

Q10: Explain TypeScript utility types for React.
A: - React.FC<Props>: Function component type
   - React.ReactNode: Any renderable content
   - React.CSSProperties: Type for inline styles
   - Partial<T>: Make all properties optional
   - Record<K, V>: Object type with specific keys/values
*/

export default {
  User,
  TodoApp,
  ShoppingCartApp,
  PostList,
  AuthProvider,
  Dashboard,
  useLocalStorage,
  useFetch,
  UserProfile,
  Button,
  Form,
  CartItemComponent,
  ShoppingCart2,
  ItemList,
};
"""

# This demonstrates the structure. In actual implementation:
# 1. Create a React project with TypeScript support
# 2. Install dependencies: npm create vite@latest my-app -- --template react-ts
# 3. Implement these patterns in actual TSX files
# 4. Run the development server: npm run dev
# 5. Build for production: npm run build

print("React + TypeScript Fundamentals structure created")
print("Topics covered:")
print("- TypeScript types and interfaces")
print("- Functional components with React.FC")
print("- useState and useReducer hooks")
print("- useEffect for side effects")
print("- Context API for global state")
print("- Custom hooks with TypeScript")
print("- Component composition patterns")
print("- Memoization and performance optimization")
print("- Form handling and validation")
print("- 10 interview questions embedded")
