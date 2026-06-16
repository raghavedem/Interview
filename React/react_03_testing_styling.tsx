"""
REACT TESTING, STYLING & PRODUCTION PATTERNS
Topics:
- Unit testing with Jest and React Testing Library
- Component testing strategies
- CSS-in-JS and Tailwind CSS
- Accessibility (a11y)
- Performance monitoring
- Deployment and CI/CD
"""

REACT_TESTING_STYLING = """

// ============================================================================
// 1. UNIT TESTING WITH JEST & REACT TESTING LIBRARY
// ============================================================================

import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

// Component to test
interface LoginFormProps {
  onSubmit: (email: string, password: string) => Promise<void>;
}

const LoginForm: React.FC<LoginFormProps> = ({ onSubmit }) => {
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [error, setError] = React.useState('');
  const [loading, setLoading] = React.useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await onSubmit(email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        aria-label="Email"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        aria-label="Password"
      />
      {error && <div role="alert">{error}</div>}
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
};

// Test suite
describe('LoginForm', () => {
  it('should render login form', () => {
    render(<LoginForm onSubmit={jest.fn()} />);

    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('should call onSubmit with email and password', async () => {
    const handleSubmit = jest.fn().mockResolvedValue(undefined);
    render(<LoginForm onSubmit={handleSubmit} />);

    await userEvent.type(screen.getByLabelText('Email'), 'john@example.com');
    await userEvent.type(screen.getByLabelText('Password'), 'password123');
    await userEvent.click(screen.getByRole('button', { name: /login/i }));

    expect(handleSubmit).toHaveBeenCalledWith('john@example.com', 'password123');
  });

  it('should show error message on failed login', async () => {
    const handleSubmit = jest.fn().mockRejectedValue(new Error('Invalid credentials'));
    render(<LoginForm onSubmit={handleSubmit} />);

    await userEvent.type(screen.getByLabelText('Email'), 'wrong@example.com');
    await userEvent.type(screen.getByLabelText('Password'), 'wrong');
    await userEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('Invalid credentials');
    });
  });

  it('should disable button while loading', async () => {
    const handleSubmit = jest.fn(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );
    render(<LoginForm onSubmit={handleSubmit} />);

    const button = screen.getByRole('button');

    await userEvent.type(screen.getByLabelText('Email'), 'john@example.com');
    await userEvent.type(screen.getByLabelText('Password'), 'password123');
    await userEvent.click(button);

    expect(button).toBeDisabled();

    await waitFor(() => {
      expect(button).not.toBeDisabled();
    });
  });

  it('should clear form on successful login', async () => {
    const handleSubmit = jest.fn().mockResolvedValue(undefined);
    render(<LoginForm onSubmit={handleSubmit} />);

    const emailInput = screen.getByLabelText('Email') as HTMLInputElement;
    const passwordInput = screen.getByLabelText('Password') as HTMLInputElement;

    await userEvent.type(emailInput, 'john@example.com');
    await userEvent.type(passwordInput, 'password123');
    await userEvent.click(screen.getByRole('button'));

    await waitFor(() => {
      // Form should be empty after successful submission
      expect(emailInput.value).toBe('');
      expect(passwordInput.value).toBe('');
    });
  });
});

// ============================================================================
// 2. MOCKING API CALLS
// ============================================================================

import fetch from 'jest-fetch-mock';

describe('UserList', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  it('should display users from API', async () => {
    const mockUsers = [
      { id: 1, name: 'John', email: 'john@example.com' },
      { id: 2, name: 'Jane', email: 'jane@example.com' },
    ];

    fetch.mockResponseOnce(JSON.stringify(mockUsers));

    render(<UserList />);

    await waitFor(() => {
      expect(screen.getByText('John')).toBeInTheDocument();
      expect(screen.getByText('Jane')).toBeInTheDocument();
    });

    expect(fetch).toHaveBeenCalledWith('/api/users');
  });

  it('should handle API errors', async () => {
    fetch.mockRejectOnce(new Error('API Error'));

    render(<UserList />);

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
});

// ============================================================================
// 3. TESTING CUSTOM HOOKS
// ============================================================================

import { renderHook, act } from '@testing-library/react';

describe('useLocalStorage', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should initialize with default value', () => {
    const { result } = renderHook(() => useLocalStorage('key', 'default'));

    expect(result.current[0]).toBe('default');
  });

  it('should persist to localStorage', () => {
    const { result } = renderHook(() => useLocalStorage('key', 'initial'));

    act(() => {
      result.current[1]('updated');
    });

    expect(localStorage.getItem('key')).toBe(JSON.stringify('updated'));
    expect(result.current[0]).toBe('updated');
  });

  it('should load from localStorage on init', () => {
    localStorage.setItem('key', JSON.stringify('stored'));

    const { result } = renderHook(() => useLocalStorage('key', 'default'));

    expect(result.current[0]).toBe('stored');
  });
});

// ============================================================================
// 4. SNAPSHOT TESTING
// ============================================================================

describe('UserCard', () => {
  it('should match snapshot', () => {
    const { container } = render(
      <UserCard id={1} name="John Doe" email="john@example.com" />
    );

    expect(container.firstChild).toMatchSnapshot();
  });

  // Update snapshots with: jest -u
});

// ============================================================================
// 5. TESTING ACCESSIBILITY (A11y)
// ============================================================================

import { axe, toHaveNoViolations } from 'jest-axe';
expect.extend(toHaveNoViolations);

describe('Accessibility', () => {
  it('should have no accessibility violations', async () => {
    const { container } = render(<LoginForm onSubmit={jest.fn()} />);

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should be keyboard navigable', async () => {
    render(<LoginForm onSubmit={jest.fn()} />);

    // Tab through form
    await userEvent.tab();
    expect(screen.getByLabelText('Email')).toHaveFocus();

    await userEvent.tab();
    expect(screen.getByLabelText('Password')).toHaveFocus();

    await userEvent.tab();
    expect(screen.getByRole('button')).toHaveFocus();
  });
});

// ============================================================================
// 6. STYLING WITH TAILWIND CSS
// ============================================================================

// Component with Tailwind
const Button: React.FC<React.ButtonHTMLAttributes<HTMLButtonElement>> = ({
  children,
  className = '',
  ...props
}) => {
  const baseStyles = 'px-4 py-2 rounded font-medium transition-colors';
  const variants = {
    primary: 'bg-blue-500 text-white hover:bg-blue-600',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
    danger: 'bg-red-500 text-white hover:bg-red-600',
  };

  const variant = props.disabled ? 'secondary' : 'primary';

  return (
    <button
      className={\`\${baseStyles} \${variants[variant]} \${className}\`}
      {...props}
    >
      {children}
    </button>
  );
};

const Card: React.FC<{ children: React.ReactNode; title?: string }> = ({
  children,
  title,
}) => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {title && <h2 className="text-2xl font-bold mb-4">{title}</h2>}
      {children}
    </div>
  );
};

// ============================================================================
// 7. STYLED COMPONENTS (CSS-IN-JS)
// ============================================================================

import styled from 'styled-components';

interface StyledButtonProps {
  variant?: 'primary' | 'secondary';
  size?: 'small' | 'medium' | 'large';
}

const StyledButton = styled.button<StyledButtonProps>\`
  padding: \${(props) =>
    props.size === 'small'
      ? '0.5rem 1rem'
      : props.size === 'large'
      ? '1rem 2rem'
      : '0.75rem 1.5rem'};
  
  background-color: \${(props) =>
    props.variant === 'secondary' ? '#e0e0e0' : '#007bff'};
  
  color: \${(props) => (props.variant === 'secondary' ? '#000' : '#fff')};
  
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  transition: background-color 0.3s;

  &:hover {
    background-color: \${(props) =>
      props.variant === 'secondary' ? '#d0d0d0' : '#0056b3'};
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
\`;

// ============================================================================
// 8. PERFORMANCE MONITORING
// ============================================================================

import { onLCP, onFID, onCLS, onINP } from 'web-vitals';

// Measure Core Web Vitals
onLCP((metric) => {
  console.log('LCP:', metric.value); // Largest Contentful Paint
  // Send to analytics
});

onFID((metric) => {
  console.log('FID:', metric.value); // First Input Delay
});

onCLS((metric) => {
  console.log('CLS:', metric.value); // Cumulative Layout Shift
});

onINP((metric) => {
  console.log('INP:', metric.value); // Interaction to Next Paint
});

// Performance profiling
const useTiming = (name: string): (() => void) => {
  const startTime = React.useRef<number>(performance.now());

  const end = (): void => {
    const duration = performance.now() - startTime.current;
    console.log(\`\${name} took \${duration.toFixed(2)}ms\`);
  };

  return end;
};

const HeavyComponent: React.FC = () => {
  const endTiming = useTiming('HeavyComponent render');

  React.useEffect(() => {
    return endTiming;
  }, [endTiming]);

  return <div>Heavy content</div>;
};

// ============================================================================
// 9. CI/CD WITH GITHUB ACTIONS
// ============================================================================

const GITHUB_ACTIONS_CONFIG = `
name: Test and Build

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm run test
      
      - name: Build
        run: npm run build
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run lint
`;

// ============================================================================
// 10. PERFORMANCE OPTIMIZATION
// ============================================================================

// Image optimization
const OptimizedImage: React.FC<{ src: string; alt: string }> = ({
  src,
  alt,
}) => {
  return (
    <img
      src={src}
      alt={alt}
      loading="lazy"
      decoding="async"
      srcSet={src.replace('.jpg', '-small.jpg') + ' 480w, ' + src + ' 1200w'}
      sizes="(max-width: 480px) 480px, 1200px"
    />
  );
};

// Bundle size analyzer
const BUNDLE_ANALYZER = `
// Install: npm install --save-dev @next/bundle-analyzer
// Add to next.config.js:

const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

module.exports = withBundleAnalyzer({
  // config
});

// Run: ANALYZE=true npm run build
`;

// ============================================================================
// INTERVIEW QUESTIONS - TESTING & PRODUCTION
// ============================================================================

/*
Q1: What's the difference between unit, integration, and e2e tests?
A: Unit: Test individual functions/components in isolation
   Integration: Test multiple components working together
   E2E: Test full user workflows (Cypress, Playwright)
   Coverage: Aim for 80% with focus on critical paths

Q2: How to test async operations in React?
A: Use waitFor() to wait for async updates
   Use act() to wrap state updates
   Mock fetch/axios with jest.mock()
   Test: loading, success, error states

Q3: What's the difference between fireEvent and userEvent?
A: fireEvent: Fires DOM events directly (low-level)
   userEvent: Simulates user interactions (high-level, preferred)
   userEvent: Better testing, more realistic, catches more bugs
   Use: userEvent for new tests, fireEvent only when needed

Q4: How to mock API calls in tests?
A: Use jest.mock() for modules
   Use fetch-mock or MSW (Mock Service Worker)
   Mock before render: jest.mock('axios')
   Test both success and error cases

Q5: What's accessibility testing and how to do it?
A: Ensure app works for all users (screen readers, keyboard navigation)
   Tools: jest-axe, Lighthouse, Pa11y
   Check: ARIA labels, semantic HTML, keyboard navigation
   Test: Color contrast, focus indicators, logical tab order

Q6: How to measure and improve performance?
A: Use React DevTools Profiler
   Measure Core Web Vitals (LCP, FID, CLS, INP)
   Tools: Lighthouse, WebPageTest
   Optimize: Code splitting, lazy loading, memoization

Q7: What's the difference between Tailwind CSS and Styled Components?
A: Tailwind: Utility-first, pre-defined classes, smaller CSS
   Styled: Runtime CSS-in-JS, component-scoped, CSS in JS
   Tailwind: Better performance, easier learning curve
   Styled: Better for dynamic styles, CSS features

Q8: How to optimize bundle size?
A: Analyze bundle: webpack-bundle-analyzer
   Tree-shaking: Remove unused code
   Code splitting: Split into smaller chunks
   Lazy load: Import components/libraries on demand
   Minify & compress: Gzip compression

Q9: What's the purpose of CI/CD pipelines?
A: Continuous Integration: Auto test on every push
   Continuous Deployment: Auto deploy on merge
   Benefits: Catch bugs early, faster releases, consistent environment
   Tools: GitHub Actions, GitLab CI, Jenkins

Q10: How to handle secrets in CI/CD?
A: Never commit secrets to git
   Use environment variables/secrets management
   GitHub: Settings > Secrets and variables > Actions
   Never log secrets in build output
   Rotate secrets regularly
*/

export {};
"""

print("React Testing & Styling guide created")
print("Topics covered:")
print("- Unit testing with Jest and React Testing Library")
print("- Testing user interactions")
print("- Mocking API calls and modules")
print("- Testing custom hooks")
print("- Accessibility testing (a11y)")
print("- Snapshot testing")
print("- Tailwind CSS styling")
print("- Styled Components (CSS-in-JS)")
print("- Performance monitoring with Web Vitals")
print("- CI/CD with GitHub Actions")
print("- 10 testing and production interview questions")
