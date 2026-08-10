# Full-Stack Interview Prep Guide
### Python · FastAPI · JavaScript · TypeScript · React · Node.js · PostgreSQL

---

## How to use this guide

| Time you have | What to do |
|---|---|
| **1 day** | Read every "Recap" section + the ⚡ **Rapid-fire** answers. Do the 5 challenges marked ★. |
| **3 days** | Day 1: JS/TS/React. Day 2: Python/FastAPI/Node. Day 3: Postgres + all coding challenges + system design. |
| **1 week** | Above, but write out every coding challenge yourself *before* reading the solution, and say the Q&A answers out loud. |

**The single highest-leverage habit:** for every answer, add a sentence of *tradeoff* ("I'd use X here, but if the team needed Y, I'd switch because…"). Interviewers hire for judgement, not recall.

---

# 1. JavaScript

## 1.1 Recap

### Types & coercion
Seven primitives: `string`, `number`, `bigint`, `boolean`, `undefined`, `symbol`, `null`. Everything else is an object (including arrays and functions).

- `==` coerces, `===` doesn't. Use `===` always, with one idiomatic exception: `x == null` checks for `null` *or* `undefined` in one shot.
- `NaN !== NaN`. Use `Number.isNaN(x)`.
- Falsy values, memorised: `false, 0, -0, 0n, "", null, undefined, NaN`. **Everything else is truthy** — including `[]`, `{}`, and `"0"`.

### `var` / `let` / `const`
- `var`: function-scoped, hoisted and initialised to `undefined`.
- `let` / `const`: block-scoped, hoisted but in the **Temporal Dead Zone** until the declaration line — touching them early throws `ReferenceError`.
- `const` freezes the *binding*, not the value. `const a = []; a.push(1)` is legal.

### Closures
A function plus the lexical environment it captured. The classic bug:

```js
for (var i = 0; i < 3; i++) setTimeout(() => console.log(i));   // 3 3 3
for (let i = 0; i < 3; i++) setTimeout(() => console.log(i));   // 0 1 2
```
`var` has one binding shared by all three callbacks; `let` creates a fresh binding per iteration.

### `this`
Resolution order, highest precedence first:
1. `new Foo()` → the new object.
2. `fn.call/apply/bind(obj)` → `obj`.
3. `obj.fn()` → `obj` (the *call site* decides, not where the function was written).
4. Plain `fn()` → `undefined` in strict mode / modules, `globalThis` in sloppy mode.

**Arrow functions have no `this`.** They inherit it lexically, which is exactly why they're right for callbacks and wrong for object methods and prototype methods.

### Prototypes
Every object has a hidden `[[Prototype]]` link. Property lookup walks that chain until it hits `null`. `class` is syntax sugar over this — `class` methods land on `Foo.prototype`, shared by all instances.

### The event loop
One thread. The loop:
1. Run the current synchronous stack to completion.
2. Drain the **microtask queue** completely (promise callbacks, `queueMicrotask`, `MutationObserver`).
3. Run **one macrotask** (timers, I/O, events).
4. Repeat.

Microtasks always beat macrotasks. That's why:

```js
console.log('A');
setTimeout(() => console.log('B'));
Promise.resolve().then(() => console.log('C'));
console.log('D');
// A D C B
```

### Promises & async/await
- A promise is a value with three states: pending → fulfilled | rejected. Settling is one-way and permanent.
- `async` functions always return a promise; `await` unwraps one and pauses the function (not the thread).
- Combinators: `all` (fail fast), `allSettled` (never rejects), `race` (first to settle, win *or* lose), `any` (first to fulfil).
- **Sequential vs parallel** — the most common real-world mistake:

```js
// 2 seconds — you serialised independent work
const a = await fetchA();
const b = await fetchB();

// 1 second — kick both off, then wait
const [a, b] = await Promise.all([fetchA(), fetchB()]);
```

### Modules
ESM (`import`/`export`) is static, hoisted, tree-shakeable, and async. CJS (`require`/`module.exports`) is dynamic and synchronous. ESM imports are *live bindings* — the importer sees later mutations of an exported `let`.

### Things you'll be asked to write from memory
```js
// Debounce — fire once, after the noise stops
function debounce(fn, ms) {
  let t;
  return function (...args) {
    clearTimeout(t);
    t = setTimeout(() => fn.apply(this, args), ms);
  };
}

// Throttle — at most once per window
function throttle(fn, ms) {
  let last = 0;
  return function (...args) {
    const now = Date.now();
    if (now - last >= ms) { last = now; fn.apply(this, args); }
  };
}

// Deep clone (modern, handles cycles & Dates & Maps)
const copy = structuredClone(obj);
```

---

## 1.2 Interview questions & answers

**Q: Explain hoisting.**
Declarations are registered before any code runs. `var` and `function` declarations are initialised early (`undefined` and the full function respectively), so calling a function declaration before its line works. `let`, `const`, and `class` are hoisted but uninitialised — the TDZ — so accessing them early throws. Function *expressions* assigned to `const` follow the `const` rules, not the function rules.

**Q: What's the difference between `null` and `undefined`?**
`undefined` means "the language hasn't given this a value" — an unassigned variable, a missing argument, a missing property. `null` means "a human deliberately set this to empty." Practically: I let the runtime produce `undefined` and I produce `null` when I mean intentional absence. Note `typeof null === "object"` is a famous bug preserved for backwards compatibility.

**Q: Explain event delegation.**
Instead of attaching a listener to 500 rows, attach one to the container and use `event.target.closest('.row')` to figure out which one was hit. It relies on bubbling. Benefits: less memory, and it works for elements added to the DOM after the listener was attached.

**Q: `.call` vs `.apply` vs `.bind`?**
`call` and `apply` invoke immediately with an explicit `this`, differing only in whether args are spread or passed as an array. `bind` returns a *new* function with `this` permanently fixed; it doesn't invoke.

**Q: What is a memory leak in JS and how do you find one?**
Common causes: listeners never removed, timers never cleared, closures holding large objects, unbounded caches/maps, detached DOM nodes still referenced. I'd take heap snapshots in DevTools before and after repeating the suspect action and look at the retained-size delta and the retainer path. `WeakMap`/`WeakRef` help when a cache shouldn't keep keys alive.

**Q: What does `Object.freeze` do — and what's the catch?**
It makes an object's own properties non-writable and non-configurable. It's **shallow**: nested objects are still mutable. Deep freezing requires recursion.

**Q: Explain currying and why you'd use it.**
Turning `f(a, b, c)` into `f(a)(b)(c)`. Useful for partial application — `const log = level => msg => console.log(level, msg)` lets you pre-bind configuration and pass around a specialised function. React devs meet it constantly in HOCs and middleware.

### ⚡ Rapid-fire
- **`map` vs `forEach`?** `map` returns a new array; `forEach` returns `undefined` and exists for side effects.
- **`slice` vs `splice`?** `slice` is pure and returns a copy; `splice` mutates in place.
- **`for...in` vs `for...of`?** `in` iterates enumerable keys including inherited ones; `of` iterates values of iterables. Never use `for...in` on arrays.
- **What is the TDZ?** The region between the top of a block and a `let`/`const` declaration where the binding exists but touching it throws.
- **Shallow vs deep copy?** `{...obj}` and `Object.assign` copy one level; nested references are shared. Use `structuredClone`.
- **Optional chaining / nullish coalescing?** `a?.b` short-circuits to `undefined` if `a` is nullish. `a ?? b` falls back only on `null`/`undefined` — unlike `||`, which also fires on `0` and `""`.
- **Generators?** Functions that pause at `yield` and can be resumed, producing lazy sequences.

---
# 2. TypeScript

## 2.1 Recap

### The mental model
TypeScript is a **structural**, erased type system. Structural = compatibility is decided by shape, not by name. Erased = types vanish at runtime, so they cannot validate data arriving from the network. That last point is the source of most production TS bugs: `response.json() as User` is a lie you told the compiler.

### Core types worth knowing cold
- `any` — turns checking off and infects everything it touches. `unknown` — the safe top type; you must narrow before use. Prefer `unknown`.
- `never` — the empty type. Returned by functions that always throw, and used for exhaustiveness checks.
- `void` — no useful return value.
- Literal types (`"GET" | "POST"`) plus unions give you cheap enums without the runtime cost.
- Tuples: `[string, number]`. Readonly: `readonly string[]` / `as const`.

### Interface vs type alias
`interface` can be re-opened (declaration merging) and is idiomatic for object/class contracts. `type` can express unions, intersections, conditionals, and mapped types. Practical rule: **`interface` for public object shapes, `type` for everything else.** They're interchangeable for plain objects.

### Narrowing
The compiler follows control flow. The tools:
```ts
typeof x === "string"          // primitives
x instanceof Error             // classes
"role" in user                 // property presence
Array.isArray(x)
if (!x) return;                // truthiness / null guard

// Discriminated union — the workhorse pattern
type Result =
  | { status: "ok"; data: string }
  | { status: "error"; message: string };

function handle(r: Result) {
  switch (r.status) {
    case "ok":    return r.data;      // narrowed
    case "error": return r.message;
    default:      return assertNever(r);
  }
}
function assertNever(x: never): never { throw new Error(`Unhandled: ${JSON.stringify(x)}`); }
```
That `assertNever` is worth showing in an interview: add a third variant to the union and the code fails to **compile** rather than silently falling through.

### Type guards
```ts
function isUser(v: unknown): v is User {
  return typeof v === "object" && v !== null && "id" in v;
}
```
For real boundaries (HTTP responses, `localStorage`, env vars) use **Zod** and derive the type from the schema, so validation and type stay in sync:
```ts
const User = z.object({ id: z.string(), age: z.number().int().positive() });
type User = z.infer<typeof User>;
const user = User.parse(await res.json());   // throws on bad data
```

### Generics
```ts
function first<T>(arr: T[]): T | undefined { return arr[0]; }

// Constrained generic + keyof — the classic interview question
function pluck<T, K extends keyof T>(obj: T, key: K): T[K] { return obj[key]; }
```

### Utility types (know what each does)
`Partial<T>`, `Required<T>`, `Readonly<T>`, `Pick<T, K>`, `Omit<T, K>`, `Record<K, V>`, `Exclude<T, U>`, `Extract<T, U>`, `NonNullable<T>`, `ReturnType<F>`, `Parameters<F>`, `Awaited<T>`.

Implement two of them from scratch — this is a frequent whiteboard ask:
```ts
type MyPartial<T> = { [K in keyof T]?: T[K] };
type MyPick<T, K extends keyof T> = { [P in K]: T[P] };
type MyOmit<T, K extends keyof T> = MyPick<T, Exclude<keyof T, K>>;
```

### Compiler flags that matter
`strict: true` (turns on the rest), `noUncheckedIndexedAccess` (makes `arr[i]` return `T | undefined` — closer to the truth), `exactOptionalPropertyTypes`, `noImplicitOverride`.

## 2.2 Interview questions & answers

**Q: `unknown` vs `any` vs `never`?**
`any` disables checking — assignable both ways, and errors leak downstream. `unknown` accepts anything but permits nothing until you narrow, so it's the correct type for parsed JSON or caught errors. `never` is the type with no values; it appears in impossible branches and is how exhaustiveness checking works.

**Q: What are declaration merging and module augmentation?**
Two `interface` declarations with the same name in the same scope merge into one. Module augmentation extends someone else's types — e.g. adding `user` to Express's `Request`:
```ts
declare global { namespace Express { interface Request { user?: User } } }
```

**Q: Explain `as const`.**
It freezes inference to the narrowest literal types and marks everything `readonly`. `const ROLES = ["admin","user"] as const` gives `readonly ["admin","user"]`, so `type Role = typeof ROLES[number]` is `"admin" | "user"` — one source of truth for both the runtime array and the type.

**Q: Enum or union of literals?**
Union of string literals, almost always: zero runtime output, better narrowing, and it JSON-serialises naturally. TS `enum` emits real JS objects, and numeric enums are not type-safe (any number was historically assignable). `const enum` is inlined but breaks under isolated-module builds.

**Q: Covariance/contravariance in one breath?**
Return types are covariant (a function returning `Dog` fits where one returning `Animal` is expected). Parameters are properly contravariant, but TS checks method parameters bivariantly for historical convenience — `strictFunctionTypes` fixes this for function-type properties, not for methods.

**Q: How do you type an API client?**
Define the response shapes, validate at the boundary with Zod, and use generics so the caller gets a precise type:
```ts
async function get<T>(url: string, schema: z.ZodType<T>): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new HttpError(res.status);
  return schema.parse(await res.json());
}
```

---

# 3. React

## 3.1 Recap

### Rendering model
React builds a virtual tree, diffs it against the previous one, and applies the minimum set of DOM mutations. A component re-renders when its state changes, its parent re-renders, or its context value changes. **Re-render ≠ DOM update** — a re-render that produces identical output costs only the diff.

Reconciliation heuristics: different element type → throw the subtree away and rebuild; same type → update props in place; lists are matched by `key`. Using array index as a key breaks whenever the list reorders or items are inserted at the front — state gets attached to the wrong row.

### Hooks — the rules and the reasons
Call hooks unconditionally at the top level of a component or another hook. React tracks them by call order in a linked list, so a conditional hook shifts the indices and corrupts state.

- **`useState`** — use the updater form when the next value depends on the previous: `setCount(c => c + 1)`. State updates are asynchronous and batched (React 18 batches inside promises and native handlers too).
- **`useEffect`** — for *synchronising with something outside React*: subscriptions, timers, imperative DOM APIs, analytics. It is **not** the right tool for deriving data from props (compute it during render) or for handling user events (do it in the handler). Always return a cleanup function for anything subscribable. In StrictMode dev, effects run twice deliberately to surface missing cleanup.
- **`useLayoutEffect`** — same, but fires synchronously after DOM mutation, before paint. For measuring layout to avoid a visible flicker. Blocks paint, so use sparingly.
- **`useMemo` / `useCallback`** — caching by reference. Justified when the computation is genuinely expensive, or when the value is a dependency of a memoised child or another hook. Sprinkling them everywhere adds allocation and comparison cost for nothing.
- **`useRef`** — mutable box that survives renders and does *not* trigger one. DOM handles, previous values, timer IDs, "has this already run" flags.
- **`useReducer`** — when the next state depends on several fields or transitions follow rules. Easier to test: it's a pure function.
- **`useContext`** — reads the nearest provider. Every consumer re-renders when the provider's value changes, so memoise the value object and split contexts by update frequency.

### Derived state
```jsx
// ❌ two sources of truth, one render behind
const [full, setFull] = useState('');
useEffect(() => setFull(`${first} ${last}`), [first, last]);

// ✅
const full = `${first} ${last}`;
```

### Data fetching in an effect — the correct shape
```jsx
useEffect(() => {
  const ctrl = new AbortController();
  let alive = true;
  (async () => {
    try {
      const res = await fetch(`/api/users/${id}`, { signal: ctrl.signal });
      if (!res.ok) throw new Error(res.statusText);
      const data = await res.json();
      if (alive) setUser(data);
    } catch (e) {
      if (e.name !== 'AbortError' && alive) setError(e);
    }
  })();
  return () => { alive = false; ctrl.abort(); };
}, [id]);
```
The cleanup is what prevents the race where a slow request for `id=1` resolves after a fast one for `id=2`. In production I'd reach for React Query / SWR, which give caching, deduplication, retries, and stale-while-revalidate for free.

### Performance toolkit, in order of what to try first
1. Fix the obvious: keys, unnecessary state, state living too high in the tree.
2. Move state **down** into the smallest component that needs it, or pass children as props so the expensive subtree isn't re-created.
3. `React.memo` + stable props (`useCallback`/`useMemo`).
4. Virtualise long lists (`react-window`).
5. `useDeferredValue` / `useTransition` to keep typing responsive while an expensive list filters.
6. Code-split with `lazy` + `Suspense`.

### Modern APIs
- **Error boundaries** — class components (or `react-error-boundary`) catching render-phase errors. They don't catch errors in event handlers or async code.
- **Portals** — render into a different DOM node while keeping React tree context. Modals, tooltips.
- **Server Components** (React 19 / Next App Router) — run on the server, ship zero JS, can `await` data directly, cannot use state or effects. `"use client"` marks the boundary where interactivity begins.
- **`useSyncExternalStore`** — the correct way to subscribe to an external store without tearing during concurrent rendering.

## 3.2 Interview questions & answers

**Q: Why do we need `key`, and why is index a bad one?**
Keys tell the reconciler which element in the new list corresponds to which in the old one. With index keys, inserting at the front shifts every index, so React thinks every item changed — it reuses the wrong component instances, and any internal state (an input's text, a checkbox) sticks to the wrong row. Use a stable ID from your data.

**Q: Controlled vs uncontrolled components?**
Controlled: React state is the single source of truth, value flows down and `onChange` flows up. Predictable, easy to validate, easy to reset. Uncontrolled: the DOM holds the value and you read it with a ref — less code and fewer renders for large forms. Libraries like React Hook Form deliberately use uncontrolled inputs for performance.

**Q: `useMemo` vs `useCallback`?**
`useCallback(fn, deps)` is exactly `useMemo(() => fn, deps)`. One memoises a value, the other a function reference. Both are about *referential stability* far more often than raw computation cost.

**Q: What actually changed in React 18/19?**
Concurrent rendering: React can start rendering, pause, and abandon work. Automatic batching everywhere. `useTransition`/`useDeferredValue` to mark updates as non-urgent. Streaming SSR with `Suspense`. React 19 adds Actions, `useOptimistic`, `use()`, and the ref-as-prop simplification.

**Q: How would you share state across a deep tree?**
Start with prop drilling — it's fine for two or three levels and it's explicit. Then Context for low-frequency values (theme, current user, locale). For high-frequency or complex client state, an external store (Zustand, Redux Toolkit) that supports selector-based subscriptions, because Context re-renders every consumer. And keep **server state** separate in React Query — most "global state" is actually cached server data.

**Q: When does a `useEffect` become the wrong tool?**
When it transforms props into state, when it responds to a user event (put that logic in the handler), when it fetches data that a framework loader or React Query should own, and when it fires a chain of effects updating each other. My check: "am I synchronising with a system outside React?" If no, it shouldn't be an effect.

**Q: How do you test a React component?**
React Testing Library, querying the way a user would (`getByRole`, `getByLabelText`) rather than by test IDs where possible, and asserting on behaviour rather than internals. MSW to mock at the network layer so the component isn't coupled to the fetch implementation. `userEvent` over `fireEvent` for realistic interaction.

---
# 4. Node.js

## 4.1 Recap

### Architecture
Single-threaded JS execution on V8, with libuv providing an event loop and a **thread pool (default 4)** for filesystem work, DNS, and crypto. Network I/O doesn't use the pool — it uses the OS's async primitives (epoll/kqueue/IOCP). So Node is excellent at I/O concurrency and terrible at CPU-bound work, because one long synchronous function blocks *every* request.

### Event loop phases (in order, per tick)
`timers` → `pending callbacks` → `idle/prepare` → **`poll`** (waits for I/O) → `check` (`setImmediate`) → `close callbacks`.

Between every phase and every callback, Node drains `process.nextTick` first, then the microtask (promise) queue. `nextTick` starving the loop is a real production hazard.

`setTimeout(fn, 0)` vs `setImmediate(fn)` at top level is non-deterministic; inside an I/O callback, `setImmediate` always wins because you're already past the poll phase.

### Handling CPU-bound work
1. `worker_threads` for CPU work inside the process (sharing memory via `SharedArrayBuffer` when useful).
2. `child_process` / a separate service for heavy or untrusted work.
3. A job queue (BullMQ + Redis) for anything slow — the right answer in most system design rounds.
4. `cluster` or a process manager to use all cores; in containers, usually one process per container and let the orchestrator scale.

### Streams
Four kinds: Readable, Writable, Duplex, Transform. Streams keep memory flat and constant regardless of file size, and backpressure is handled for you if you use `pipeline`:
```js
const { pipeline } = require('node:stream/promises');
await pipeline(
  fs.createReadStream('big.csv'),
  csvParser(),
  transformRows(),
  fs.createWriteStream('out.csv')
);
```
Use `pipeline`, not `.pipe()` — `.pipe()` doesn't clean up on error and leaks file descriptors.

### Error handling
- Sync: `try/catch`. Async: `.catch()` or `try/catch` around `await`.
- An `EventEmitter` `'error'` event with no listener **crashes the process**.
- Wrap async Express handlers, or errors never reach your error middleware (Express 5 fixes this):
```js
const asyncH = fn => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);
```
- Handle `unhandledRejection` and `uncaughtException` by **logging and exiting**, letting the supervisor restart. The process state is unknown after an uncaught throw; continuing is how you get corrupted data.
- Graceful shutdown on `SIGTERM`: stop accepting connections, finish in-flight requests, close the DB pool, then exit.

### Security checklist for the interview
Helmet for headers, rate limiting, input validation (Zod/Joi) at the edge, parameterised SQL, `bcrypt`/`argon2` for passwords (never MD5/SHA), short-lived JWTs with refresh tokens in httpOnly cookies, CORS allow-list rather than `*`, secrets in env/a secret manager, `npm audit` in CI, and never `eval`/`child_process.exec` on user input.

## 4.2 Interview questions & answers

**Q: How is Node "non-blocking" if JavaScript is single-threaded?**
The JS you write runs on one thread, but I/O is delegated to the kernel or libuv's thread pool. Your callback is queued and runs when the loop reaches the right phase. So thousands of concurrent connections are cheap — as long as no callback hogs the CPU.

**Q: `process.nextTick` vs `Promise.then` vs `setImmediate`?**
`nextTick` callbacks run before promise microtasks, and both run before the loop advances a phase. `setImmediate` runs in the check phase, i.e. a full phase later. Recursive `nextTick` can starve I/O entirely; recursive `setImmediate` cannot.

**Q: Middleware in Express — how does it work?**
An ordered array of `(req, res, next)` functions. Each either responds or calls `next()`. Error middleware has four arguments `(err, req, res, next)` and must be registered last. Order matters: body parsing before routes, auth before protected routes, error handler at the end.

**Q: How do you scale a Node service?**
Horizontally: stateless processes behind a load balancer, sessions in Redis rather than memory, sticky-session-free design. Vertically per box: one process per core via cluster or the orchestrator. Then the usual: connection pooling, caching, moving slow work to queues, and CDN for static assets.

**Q: CommonJS vs ESM in Node?**
CJS is synchronous, dynamic, `__dirname` available, and can `require` at any point. ESM is async, statically analysable, top-level `await` works, and uses `import.meta.url` instead of `__dirname`. ESM can import CJS; CJS can only `import()` ESM dynamically. `"type": "module"` in package.json flips the default.

**Q: How do you debug a memory leak in production Node?**
Watch RSS and heap-used over time; a sawtooth that trends upward means retention. Take heap snapshots (`--inspect` + Chrome DevTools, or `v8.writeHeapSnapshot()`), diff two snapshots taken under the same load, and follow the retainer path. Usual suspects: module-level caches without eviction, listeners added per request, closures capturing request objects, and `global` arrays.

### ⚡ Rapid-fire
- **`npm ci` vs `npm install`?** `ci` deletes `node_modules` and installs exactly the lockfile — deterministic, for CI.
- **What's in `package-lock.json`?** The exact resolved tree with versions and integrity hashes.
- **`dependencies` vs `devDependencies`?** Runtime vs build/test only; the latter is excluded by `npm ci --omit=dev`.
- **Why not store sessions in process memory?** Any second instance breaks them, and a restart logs everyone out.

---

# 5. Python

## 5.1 Recap

### Data model
Everything is an object with an identity, a type, and a value. Names are *references*; assignment rebinds a name, it doesn't copy.

Mutable: `list`, `dict`, `set`, most custom classes. Immutable: `int`, `float`, `str`, `tuple`, `frozenset`, `bytes`.

**The mutable default argument trap** (asked constantly):
```python
def add(item, bucket=[]):        # ❌ the list is created once, at def time
    bucket.append(item); return bucket

def add(item, bucket=None):      # ✅
    bucket = [] if bucket is None else bucket
    bucket.append(item); return bucket
```

`is` compares identity, `==` compares value. Use `is` only for `None`, `True`, `False`.

### Comprehensions & generators
```python
squares  = [x*x for x in nums if x % 2 == 0]     # list, eager
lazy     = (x*x for x in nums)                    # generator, lazy, O(1) memory
by_id    = {u.id: u for u in users}
```
Generators are the answer to "how would you process a 50 GB file?" — you stream it line by line and never hold it in memory.

### Decorators
A decorator is a function taking a function and returning a replacement.
```python
import functools, time

def timed(fn):
    @functools.wraps(fn)                 # preserves __name__, __doc__, signature
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            print(f"{fn.__name__} took {time.perf_counter()-t0:.3f}s")
    return wrapper
```
Decorator *with arguments* = one more layer: `def retry(times): def deco(fn): def wrapper(...)`.

### Context managers
```python
from contextlib import contextmanager

@contextmanager
def transaction(conn):
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
```
The class form is `__enter__`/`__exit__`. Returning `True` from `__exit__` swallows the exception — rarely what you want.

### OOP
- `@classmethod` receives the class (alternative constructors); `@staticmethod` receives nothing (a namespaced function); `@property` makes a method look like an attribute.
- `__slots__` removes the per-instance `__dict__` — big memory saving for millions of small objects.
- MRO follows C3 linearisation; `super()` cooperates with it. `Foo.__mro__` shows the order.
- `dataclasses` for data containers (`frozen=True`, `slots=True` are worth knowing). Pydantic when you also need validation and parsing.
- ABCs and `Protocol` — `Protocol` gives structural typing (duck typing that the type checker understands) without inheritance.

### Concurrency — the crucial distinction
The **GIL** allows only one thread to execute Python bytecode at a time (free-threaded builds are experimental in 3.13+).

| Workload | Use | Why |
|---|---|---|
| I/O-bound (HTTP, DB, files) | `asyncio` or threads | The GIL is released during I/O waits |
| CPU-bound (parsing, math, images) | `multiprocessing` / `ProcessPoolExecutor` | Separate interpreters, real parallelism |
| Numeric | NumPy/pandas | The heavy loops are in C, which drops the GIL |

```python
import asyncio, httpx

async def fetch_all(urls):
    async with httpx.AsyncClient() as client:
        return await asyncio.gather(*(client.get(u) for u in urls))
```

### Memory & performance
Reference counting plus a generational cycle collector. Use `__slots__`, generators, `functools.lru_cache`, and the right data structure — `set`/`dict` lookup is O(1) versus O(n) for `list`, which is the single most common performance fix in interview code.

Profile before optimising: `cProfile` for functions, `line_profiler` for lines, `tracemalloc` for memory.

### Testing
`pytest` with fixtures for setup, `parametrize` for table-driven cases, `monkeypatch`/`unittest.mock` for boundaries, `pytest-cov` for coverage. Test behaviour, not implementation.

## 5.2 Interview questions & answers

**Q: What is the GIL and when does it hurt you?**
A mutex in CPython ensuring one thread runs bytecode at a time, which keeps reference counting safe. It hurts only CPU-bound multithreading — four threads doing maths run no faster than one. It's largely irrelevant for I/O, since the GIL is released while waiting on sockets or disk.

**Q: Shallow vs deep copy?**
`copy.copy` duplicates the outer container while sharing the nested objects; `copy.deepcopy` recursively duplicates everything and handles cycles. Slicing (`lst[:]`) and `dict(d)` are shallow.

**Q: `list` vs `tuple` vs `set` vs `dict` — when?**
`list` for ordered, mutable sequences. `tuple` for fixed heterogeneous records and as dict keys (hashable). `set` for membership tests and de-duplication, O(1). `dict` for keyed lookup, insertion-ordered since 3.7.

**Q: Explain `*args` and `**kwargs`, and the `/` and `*` in signatures.**
`*args` collects extra positionals into a tuple, `**kwargs` extra keywords into a dict. In a signature, `/` marks the end of positional-only parameters and `*` marks the start of keyword-only ones — useful for keeping an API stable while renaming internals.

**Q: Iterator vs iterable vs generator?**
An iterable implements `__iter__`. An iterator implements `__iter__` and `__next__` and is consumed once. A generator is an iterator produced by a function containing `yield` (or by a genexp) — it holds its own suspended stack frame.

**Q: How does exception handling work — and what should you never do?**
`try/except/else/finally`; `else` runs when no exception fired, `finally` always. Catch specific exceptions, use `raise ... from e` to preserve the cause, and never write a bare `except:` (it swallows `KeyboardInterrupt` and `SystemExit`). Define a small hierarchy of domain exceptions rather than raising `Exception`.

**Q: `@staticmethod` vs `@classmethod` vs plain function?**
`classmethod` when you need the class — usually alternative constructors like `User.from_row(row)`, and it respects subclassing. `staticmethod` when the function is logically grouped with the class but needs neither `self` nor `cls`. If it needs neither *and* isn't conceptually part of the class, a module-level function is cleaner.

**Q: What does `if __name__ == "__main__":` do?**
`__name__` is `"__main__"` only when the file is run directly, not when imported. It keeps script side effects from firing on import — and it's required for `multiprocessing` on Windows/macOS spawn.

---
# 6. FastAPI

## 6.1 Recap

### Why it exists
An ASGI framework built on Starlette (routing, middleware) and Pydantic (validation/serialisation). One type annotation gives you parsing, validation, error responses, and OpenAPI docs simultaneously.

### The core loop
```python
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(title="API", version="1.0")

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class UserOut(BaseModel):
    id: int
    email: EmailStr
    model_config = {"from_attributes": True}   # read from ORM objects

@app.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    if await get_by_email(db, payload.email):
        raise HTTPException(409, "Email already registered")
    return await create(db, payload)
```
Note the **separate input and output models**. That's the answer to "how do you avoid leaking password hashes?" — the response model defines exactly what goes out, and anything not on it is dropped.

### Parameter sources
Path params from the route, query params from remaining scalars with defaults, body from Pydantic models, plus `Header`, `Cookie`, `Form`, `File`, `Depends`. FastAPI infers the source from the type and where the name appears.

### Dependency injection
```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session          # code after yield runs on the way out (teardown)

async def current_user(token: str = Depends(oauth2_scheme),
                       db: AsyncSession = Depends(get_db)) -> User:
    ...  # decode JWT, load user, or raise 401
```
Dependencies are cached per request by default (`use_cache=True`), nest arbitrarily, work at router and app level, and are trivially overridable in tests:
```python
app.dependency_overrides[get_db] = lambda: test_session
```
That last line is the cleanest testing story of any Python framework — worth saying out loud.

### async vs def — the trap
- `async def` endpoints run on the event loop. **A blocking call inside one blocks the entire server.**
- Plain `def` endpoints are run in a thread pool automatically, which is the *safe* choice for synchronous libraries (psycopg2, requests, heavy CPU).
- So: async endpoint + async driver (`asyncpg`, `httpx`), or sync endpoint + sync driver. Never async endpoint + `time.sleep`/`requests`.

### Background work
`BackgroundTasks` for fire-and-forget after the response (emails, cache invalidation) — but it dies with the process, so anything that must not be lost goes to Celery/ARQ/Dramatiq with a real broker.

### Middleware, errors, lifespan
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await create_pool()      # startup
    yield
    await app.state.pool.close()              # shutdown

app = FastAPI(lifespan=lifespan)

@app.exception_handler(DomainError)
async def domain_error_handler(request, exc):
    return JSONResponse(status_code=422, content={"detail": str(exc)})
```
Add `CORSMiddleware` with an explicit origin allow-list, and a middleware that attaches a request ID for tracing.

### Pydantic v2 notes
`BaseModel` is compiled in Rust — roughly 5–50× faster than v1. `model_validate` / `model_dump` replace `parse_obj` / `dict`. `@field_validator` and `@model_validator` replace `@validator`/`@root_validator`. `BaseSettings` moved to `pydantic-settings` and is the idiomatic way to load config from env.

## 6.2 Interview questions & answers

**Q: How does FastAPI generate docs automatically?**
Type hints plus Pydantic models give it the full schema of every request and response, which it emits as an OpenAPI 3 document at `/openapi.json`, rendered by Swagger UI at `/docs` and ReDoc at `/redoc`. Because it's derived from the code that actually runs, it can't drift out of date.

**Q: WSGI vs ASGI?**
WSGI is synchronous and one-request-per-worker-thread (Flask, Django's classic path). ASGI is async and supports long-lived connections — WebSockets, SSE, HTTP/2 — with one worker handling many concurrent requests while they wait on I/O. FastAPI is ASGI, served by Uvicorn, usually under Gunicorn with Uvicorn workers in production.

**Q: How do you handle authentication?**
`OAuth2PasswordBearer` to extract the token, a `current_user` dependency to decode and verify the JWT and load the user, applied per-route or per-router via `dependencies=[Depends(require_admin)]`. Access tokens short-lived (~15 min), refresh tokens long-lived and revocable, passwords hashed with bcrypt/argon2 via passlib. For a browser client I'd put the refresh token in an httpOnly, Secure, SameSite cookie rather than localStorage.

**Q: How do you test it?**
`TestClient` (or `httpx.AsyncClient` with ASGI transport) plus `dependency_overrides` to swap the DB for a transactional test session that rolls back after each test. Factory fixtures for data. I mock external HTTP, never my own database — I want the real query planner in the loop.

**Q: N+1 queries in FastAPI + SQLAlchemy?**
It usually appears when a `response_model` serialises a relationship that was lazily loaded. Fix with eager loading — `selectinload` for collections, `joinedload` for many-to-one — and detect it by logging SQL in tests or asserting query counts.

**Q: How would you version an API?**
URL prefixes (`/v1`, `/v2`) via separate `APIRouter`s is the pragmatic default — visible, cacheable, easy to route at the gateway. Header-based versioning is cleaner in theory but harder to debug. Either way, additive changes shouldn't need a version bump; only breaking ones should.

---

# 7. PostgreSQL

## 7.1 Recap

### Schema design
Model in third normal form first, denormalise only where you've measured a problem. Pick the right types — `text` over `varchar(n)` unless the limit is a real business rule, `numeric` for money (never `float`), `timestamptz` **always** over `timestamp`, `uuid` when IDs must be generated client-side or must not be guessable, `jsonb` (never `json`) for genuinely schemaless data.

Constraints are cheap correctness: `NOT NULL`, `UNIQUE`, `CHECK`, and foreign keys with a deliberate `ON DELETE` action.

### Indexes
- **B-tree** (default): equality and range, `ORDER BY`, and the leading columns of a composite index. A composite index on `(a, b)` serves queries filtering on `a`, or `a` and `b` — but not `b` alone.
- **GIN**: `jsonb` containment, full-text search, array membership.
- **GiST**: geometric and range types.
- **BRIN**: huge, naturally-ordered tables (append-only time series) — tiny index, cheap.
- **Partial**: `CREATE INDEX ... WHERE deleted_at IS NULL` — smaller and faster when most queries share a filter.
- **Covering**: `INCLUDE (col)` enables index-only scans.

Indexes cost write throughput and disk. A wrapped column (`WHERE lower(email) = ...`) can't use a plain index — you need an expression index on `lower(email)`.

### Reading a query plan
```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;
```
Read it inside-out. What to look for: `Seq Scan` on a large table with a selective filter (missing index), a big gap between estimated and actual rows (stale statistics — `ANALYZE`), `Nested Loop` over many rows where a `Hash Join` would be better, and high `Buffers: read` meaning it went to disk rather than cache.

### Joins
`INNER` (matches only), `LEFT` (all of the left, NULLs on the right), `RIGHT`, `FULL`, `CROSS`. `LATERAL` lets the right side reference the left — the clean way to do "top 3 per group."

### Window functions — the most commonly tested "senior" SQL
```sql
SELECT
  department,
  name,
  salary,
  RANK()       OVER (PARTITION BY department ORDER BY salary DESC) AS rank,
  AVG(salary)  OVER (PARTITION BY department)                       AS dept_avg,
  salary - LAG(salary) OVER (PARTITION BY department ORDER BY hired) AS delta
FROM employees;
```
`ROW_NUMBER` always distinct; `RANK` leaves gaps after ties; `DENSE_RANK` doesn't. Window functions run *after* `WHERE`, which is why you must wrap them in a CTE or subquery to filter on the result.

### CTEs and recursion
```sql
WITH RECURSIVE tree AS (
  SELECT id, parent_id, name, 1 AS depth FROM categories WHERE parent_id IS NULL
  UNION ALL
  SELECT c.id, c.parent_id, c.name, t.depth + 1
  FROM categories c JOIN tree t ON c.parent_id = t.id
)
SELECT * FROM tree ORDER BY depth;
```

### Transactions & isolation
ACID. Postgres uses **MVCC**: readers never block writers and writers never block readers, because each transaction sees a snapshot.

| Level | Prevents | Postgres note |
|---|---|---|
| Read Committed | dirty reads | **default**; each statement gets a fresh snapshot |
| Repeatable Read | + non-repeatable reads | snapshot fixed at transaction start; may raise serialisation errors |
| Serializable | + phantoms / write skew | SSI; you must be prepared to retry |

Locking: `SELECT ... FOR UPDATE` to serialise access to a row (classic inventory decrement), `FOR UPDATE SKIP LOCKED` to build a job queue. Deadlocks are avoided by always acquiring locks in a consistent order.

### Performance beyond indexes
Connection pooling (PgBouncer — Postgres processes are expensive), `VACUUM`/autovacuum to reclaim dead tuples and prevent bloat, partitioning large tables by range, materialised views for expensive aggregates, and read replicas for reporting traffic.

## 7.2 Interview questions & answers

**Q: When does an index *not* help?**
Very small tables (a seq scan is cheaper), low-cardinality columns unless combined or partial, queries returning a large fraction of rows, functions applied to the column without a matching expression index, leading-wildcard `LIKE '%foo'` (use trigram/GIN), and `OR` conditions that can't be turned into a bitmap combination.

**Q: `DELETE` vs `TRUNCATE` vs `DROP`?**
`DELETE` is row-by-row, fires triggers, is transactional, and leaves dead tuples for vacuum. `TRUNCATE` deallocates whole pages — far faster, still transactional in Postgres, but takes an exclusive lock and skips row triggers. `DROP` removes the table itself.

**Q: `WHERE` vs `HAVING`?**
`WHERE` filters rows before grouping; `HAVING` filters groups after aggregation. Push everything you can into `WHERE` — it reduces the rows that must be aggregated.

**Q: How do you find and fix a slow query in production?**
Start with `pg_stat_statements` ordered by total time to find what actually costs the system (not just the slowest single call). Then `EXPLAIN (ANALYZE, BUFFERS)` that query. Typical fixes, roughly in order: add or fix an index, rewrite to avoid a function on an indexed column, replace a correlated subquery with a join or `LATERAL`, fix an N+1 in the application, `ANALYZE` for stale stats, or cache the result if it's read-heavy and tolerates staleness.

**Q: What is MVCC and what's the downside?**
Every write creates a new row version tagged with transaction IDs, so each transaction reads a consistent snapshot without read locks. The cost is dead tuples: tables and indexes bloat, and autovacuum has to keep up. Long-running transactions are the enemy — they hold back the vacuum horizon and bloat everything.

**Q: How do you handle schema migrations with zero downtime?**
Expand/contract. Add the new nullable column, backfill in batches, deploy code that writes both and reads the new one, then drop the old column in a later release. Add indexes `CONCURRENTLY`. Avoid rewriting large tables in a single lock-holding statement, and set a short `lock_timeout` so a blocked migration fails fast instead of queueing every query behind it.

**Q: `UNION` vs `UNION ALL`?**
`UNION` de-duplicates, which requires a sort or hash. `UNION ALL` just concatenates. Use `ALL` unless you actually need de-duplication — it's often a significant win.

### ⚡ Rapid-fire
- **Clustered index?** Postgres has none (unlike MySQL InnoDB); all indexes are secondary and point at a heap tuple.
- **`COALESCE`?** First non-null argument.
- **`DISTINCT ON`?** Postgres-specific — first row per group by the `ORDER BY`, a neat "latest per user."
- **`jsonb` vs `json`?** `jsonb` is parsed, binary, indexable, de-duplicates keys, loses key order. Use it.
- **`UPSERT`?** `INSERT ... ON CONFLICT (col) DO UPDATE SET ...`.
- **How do you paginate 10M rows?** Not `OFFSET` — it scans and discards. Keyset pagination: `WHERE (created_at, id) < ($1, $2) ORDER BY created_at DESC, id DESC LIMIT 20`.

---
# 8. Coding challenges with solutions

★ = do these first if you're short on time.

---

## JavaScript / TypeScript

### ★ C1. Implement `Promise.all`
*Tests: promises, closures, off-by-one counting.*

```js
function promiseAll(promises) {
  return new Promise((resolve, reject) => {
    const results = new Array(promises.length);
    let remaining = promises.length;
    if (remaining === 0) return resolve([]);

    promises.forEach((p, i) => {
      Promise.resolve(p).then(
        value => {
          results[i] = value;              // index, not push — order must be preserved
          if (--remaining === 0) resolve(results);
        },
        reject                              // first rejection wins; later ones are ignored
      );
    });
  });
}
```
**Talking points:** `Promise.resolve(p)` handles non-promise values. Writing by index preserves input order even though completion order varies. Once a promise settles, further `resolve`/`reject` calls are no-ops, so the fail-fast behaviour is free.

---

### ★ C2. Deep equality
```js
function deepEqual(a, b) {
  if (Object.is(a, b)) return true;                        // handles NaN, +0/-0
  if (typeof a !== 'object' || typeof b !== 'object' || a === null || b === null) return false;
  if (Array.isArray(a) !== Array.isArray(b)) return false;

  const ka = Object.keys(a), kb = Object.keys(b);
  if (ka.length !== kb.length) return false;
  return ka.every(k => Object.prototype.hasOwnProperty.call(b, k) && deepEqual(a[k], b[k]));
}
```
Mention the edge cases you *didn't* handle and would ask about: `Date`, `Map`/`Set`, `RegExp`, and circular references (solved with a `WeakMap` of visited pairs).

---

### C3. Flatten a nested array to depth `n`
```js
function flatten(arr, depth = 1) {
  return depth < 1
    ? arr.slice()
    : arr.reduce((acc, v) => acc.concat(Array.isArray(v) ? flatten(v, depth - 1) : v), []);
}

// Iterative — no stack overflow on deep input
function flattenDeep(arr) {
  const stack = [...arr], out = [];
  while (stack.length) {
    const v = stack.pop();
    Array.isArray(v) ? stack.push(...v) : out.push(v);
  }
  return out.reverse();
}
```

---

### C4. Retry with exponential backoff
```js
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function retry(fn, { attempts = 3, baseMs = 200, factor = 2, jitter = true } = {}) {
  let lastErr;
  for (let i = 0; i < attempts; i++) {
    try {
      return await fn();
    } catch (err) {
      lastErr = err;
      if (err.status && err.status < 500 && err.status !== 429) throw err;  // don't retry 4xx
      if (i === attempts - 1) break;
      const delay = baseMs * factor ** i * (jitter ? 0.5 + Math.random() : 1);
      await sleep(delay);
    }
  }
  throw lastErr;
}
```
**Why jitter:** without it, every client that failed at the same moment retries at the same moment — a thundering herd that keeps the service down.

---

### C5. Async task pool (limit concurrency to N)
*A very common senior-level question.*
```js
async function pool(tasks, limit = 5) {
  const results = new Array(tasks.length);
  let next = 0;

  async function worker() {
    while (next < tasks.length) {
      const i = next++;                      // claim an index atomically (single-threaded)
      results[i] = await tasks[i]();
    }
  }

  await Promise.all(Array.from({ length: Math.min(limit, tasks.length) }, worker));
  return results;
}
```
Compare with `Promise.all` (unbounded — will exhaust sockets or get you rate-limited on 10 000 URLs).

---

### C6. Memoize with a custom key
```js
function memoize(fn, keyFn = (...args) => JSON.stringify(args)) {
  const cache = new Map();
  return function (...args) {
    const key = keyFn(...args);
    if (cache.has(key)) return cache.get(key);
    const value = fn.apply(this, args);
    cache.set(key, value);
    return value;
  };
}
```
Say the caveats: unbounded growth (add an LRU), `JSON.stringify` is order-sensitive and fails on cycles, and for single object arguments a `WeakMap` avoids leaking.

---

### C7. Event emitter
```js
class EventEmitter {
  #listeners = new Map();

  on(event, cb) {
    if (!this.#listeners.has(event)) this.#listeners.set(event, new Set());
    this.#listeners.get(event).add(cb);
    return () => this.off(event, cb);        // return an unsubscribe fn — nice API touch
  }
  off(event, cb)  { this.#listeners.get(event)?.delete(cb); }
  once(event, cb) { const wrap = (...a) => { this.off(event, wrap); cb(...a); }; this.on(event, wrap); }
  emit(event, ...args) {
    // copy first: a listener may unsubscribe during emit
    [...(this.#listeners.get(event) ?? [])].forEach(cb => cb(...args));
  }
}
```

---

### C8. TypeScript type puzzles
```ts
// 1. DeepPartial
type DeepPartial<T> = T extends object ? { [K in keyof T]?: DeepPartial<T[K]> } : T;

// 2. Only the keys whose values are functions
type FunctionKeys<T> = { [K in keyof T]: T[K] extends (...a: any[]) => any ? K : never }[keyof T];

// 3. Make some keys optional, keep the rest required
type PartialBy<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

// 4. Typed event map — how you'd type the emitter above
type Events = { login: { userId: string }; logout: void };
declare function on<K extends keyof Events>(e: K, cb: (p: Events[K]) => void): void;
```

---

## React

### ★ C9. `useDebounce` and `useFetch`
```jsx
function useDebounce(value, delay = 300) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);          // the cleanup IS the debounce
  }, [value, delay]);
  return debounced;
}

function useFetch(url) {
  const [state, setState] = useState({ data: null, loading: true, error: null });

  useEffect(() => {
    if (!url) return;
    const ctrl = new AbortController();
    setState(s => ({ ...s, loading: true, error: null }));

    fetch(url, { signal: ctrl.signal })
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then(data => setState({ data, loading: false, error: null }))
      .catch(err => { if (err.name !== 'AbortError') setState({ data: null, loading: false, error: err }); });

    return () => ctrl.abort();
  }, [url]);

  return state;
}
```

### C10. Typeahead search — put it together
```jsx
function Search() {
  const [query, setQuery] = useState('');
  const debounced = useDebounce(query, 300);
  const { data, loading, error } = useFetch(
    debounced ? `/api/search?q=${encodeURIComponent(debounced)}` : null
  );

  return (
    <div>
      <label htmlFor="q">Search</label>
      <input id="q" value={query} onChange={e => setQuery(e.target.value)} />
      {loading && <Spinner />}
      {error && <p role="alert">{error.message}</p>}
      <ul>{data?.map(item => <li key={item.id}>{item.name}</li>)}</ul>
    </div>
  );
}
```
Points the interviewer is listening for: debounce to cut request volume, abort to kill races, a key from the data, an accessible label, and explicit loading/error states.

### C11. Why does this re-render, and how do you fix it?
```jsx
// ❌ every render creates new object and function identities,
//    so React.memo on Child never helps
function Parent({ items }) {
  const [n, setN] = useState(0);
  return <Child config={{ theme: 'dark' }} onSelect={id => console.log(id)} items={items} />;
}

// ✅
const CONFIG = { theme: 'dark' };                       // hoisted — truly constant
function Parent({ items }) {
  const [n, setN] = useState(0);
  const onSelect = useCallback(id => console.log(id), []);
  return <Child config={CONFIG} onSelect={onSelect} items={items} />;
}
const Child = React.memo(function Child({ config, onSelect, items }) { /* ... */ });
```

---

## Python

### ★ C12. Two sum, group anagrams, LRU cache
```python
def two_sum(nums: list[int], target: int) -> list[int]:
    seen = {}                                   # value -> index
    for i, n in enumerate(nums):
        if (want := target - n) in seen:        # O(1) lookup beats the O(n²) double loop
            return [seen[want], i]
        seen[n] = i
    return []


from collections import defaultdict
def group_anagrams(words: list[str]) -> list[list[str]]:
    groups = defaultdict(list)
    for w in words:
        groups[tuple(sorted(w))].append(w)      # or a 26-length count tuple for O(n·k)
    return list(groups.values())


from collections import OrderedDict
class LRUCache:
    def __init__(self, capacity: int):
        self.cap, self.data = capacity, OrderedDict()

    def get(self, key):
        if key not in self.data:
            return -1
        self.data.move_to_end(key)
        return self.data[key]

    def put(self, key, value):
        if key in self.data:
            self.data.move_to_end(key)
        self.data[key] = value
        if len(self.data) > self.cap:
            self.data.popitem(last=False)       # evict least-recently used
```
`OrderedDict` gives O(1) for both operations; mention that the "from scratch" version is a hash map plus a doubly linked list, which is what `OrderedDict` is internally.

---

### C13. Process a 50 GB file without loading it
```python
from collections import Counter

def top_ips(path: str, n: int = 10) -> list[tuple[str, int]]:
    counts = Counter()
    with open(path, encoding="utf-8") as f:
        for line in f:                          # lazy: one line in memory at a time
            if parts := line.split():
                counts[parts[0]] += 1
    return counts.most_common(n)
```
Follow-up: "what if it doesn't fit on one machine?" → shard by hashing the key, count per shard, merge the partial counters (map-reduce).

---

### C14. Rate limiter (sliding window)
```python
import time
from collections import deque

class RateLimiter:
    """Allow at most `limit` events per `window` seconds, per key."""
    def __init__(self, limit: int, window: float):
        self.limit, self.window = limit, window
        self._events: dict[str, deque[float]] = {}

    def allow(self, key: str) -> bool:
        now = time.monotonic()                          # monotonic: immune to clock changes
        q = self._events.setdefault(key, deque())
        while q and now - q[0] >= self.window:
            q.popleft()
        if len(q) >= self.limit:
            return False
        q.append(now)
        return True
```
Follow-up they will ask: "make it work across three servers." → Redis, using a sorted set per key (`ZREMRANGEBYSCORE` + `ZCARD` + `ZADD` in one Lua script for atomicity), or a token bucket with `INCR` + `EXPIRE`.

---

### C15. Retry decorator with backoff
```python
import functools, random, time

def retry(times=3, base=0.2, factor=2.0, exceptions=(Exception,)):
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    if attempt == times - 1:
                        raise
                    time.sleep(base * factor ** attempt * (0.5 + random.random()))
        return wrapper
    return deco
```

---

### C16. Async: fetch many URLs with bounded concurrency
```python
import asyncio, httpx

async def fetch_all(urls: list[str], concurrency: int = 10) -> list[str | Exception]:
    sem = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(timeout=10) as client:
        async def one(url: str):
            async with sem:                                  # bounds in-flight requests
                r = await client.get(url)
                r.raise_for_status()
                return r.text

        return await asyncio.gather(*(one(u) for u in urls), return_exceptions=True)
```
`return_exceptions=True` means one dead URL doesn't cancel the other 999 — the interviewer is checking whether you know that default.

---

## SQL

### ★ C17. Second-highest salary per department
```sql
-- Window function version — one pass, handles ties explicitly
SELECT department_id, employee_id, salary
FROM (
  SELECT department_id, employee_id, salary,
         DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rnk
  FROM employees
) ranked
WHERE rnk = 2;
```
Ask the clarifying question out loud: *"if two people tie for top, is the runner-up the third person or the tied one?"* — `DENSE_RANK` vs `RANK` vs `ROW_NUMBER` is exactly that choice.

### C18. Running total and month-over-month growth
```sql
SELECT
  month,
  revenue,
  SUM(revenue) OVER (ORDER BY month ROWS UNBOUNDED PRECEDING) AS running_total,
  ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
        / NULLIF(LAG(revenue) OVER (ORDER BY month), 0), 2)   AS mom_pct
FROM monthly_revenue
ORDER BY month;
```
`NULLIF(..., 0)` is the division-by-zero guard interviewers look for.

### C19. Users who ordered in every one of the last 3 months
```sql
SELECT u.id, u.email
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE o.created_at >= date_trunc('month', now()) - INTERVAL '3 months'
GROUP BY u.id, u.email
HAVING COUNT(DISTINCT date_trunc('month', o.created_at)) = 3;
```

### C20. Find duplicates and delete all but the newest
```sql
DELETE FROM contacts c
USING contacts newer
WHERE c.email = newer.email
  AND c.created_at < newer.created_at;

-- Prevent recurrence
CREATE UNIQUE INDEX CONCURRENTLY contacts_email_key ON contacts (lower(email));
```

### C21. Top 3 products per category (LATERAL)
```sql
SELECT c.name AS category, p.name, p.revenue
FROM categories c
CROSS JOIN LATERAL (
  SELECT name, revenue FROM products
  WHERE category_id = c.id
  ORDER BY revenue DESC
  LIMIT 3
) p;
```
With an index on `products (category_id, revenue DESC)` this beats the window-function version on wide tables, because it stops after 3 rows per category instead of ranking everything.

### C22. Safe inventory decrement (concurrency)
```sql
BEGIN;
SELECT stock FROM products WHERE id = 42 FOR UPDATE;   -- lock the row
UPDATE products SET stock = stock - 1 WHERE id = 42 AND stock > 0;
-- check rowcount in the app; 0 rows means it sold out under you
COMMIT;
```
Better still, one statement — atomic without an explicit lock:
```sql
UPDATE products SET stock = stock - 1 WHERE id = 42 AND stock > 0 RETURNING stock;
```

---

# 9. System design & integration questions

These come up in almost every full-stack loop. Answer with: **clarify → data model → API → scale → failure modes.**

**Q: Design a URL shortener.**
Clarify read/write ratio and whether links expire. Table `links(id bigserial, slug text unique, target text, user_id, created_at, expires_at)`. Slug = base62 of the ID (no collision check needed) or a random 7-char string with a unique constraint and retry. Redirect path is read-heavy → cache slug→target in Redis, serve `301`/`302` (302 if you need click analytics). Analytics writes go to a queue, not the request path. Scale reads with replicas and a CDN.

**Q: Design a "recent activity feed."**
Fan-out-on-read (query followees' posts at request time) is simple and fine until follower counts are large; fan-out-on-write (push into each follower's feed list) makes reads O(1) but writes expensive — hybrid: fan-out-on-write for normal users, fan-out-on-read for celebrities. Keyset pagination, never `OFFSET`.

**Q: A page takes 4 seconds to load. Walk me through the diagnosis.**
Split the time first — network waterfall in DevTools tells you whether it's TTFB (backend), payload size (bundle/images), or render (long tasks). Backend: APM traces → slow query or N+1 → `EXPLAIN`. Frontend: bundle analyzer, code splitting, image formats/sizing, and check for a render-blocking synchronous fetch waterfall (parent fetches, then child fetches). Fix the biggest slice first and measure again.

**Q: How do you keep a React frontend and a FastAPI backend type-safe together?**
FastAPI already publishes `/openapi.json`. Generate the TypeScript client from it in CI (`openapi-typescript` / `orval`) and fail the build when the generated types change without a corresponding frontend update. That way a renamed field is a compile error, not a production `undefined`.

**Q: How do you handle authentication end to end in this stack?**
Login hits FastAPI, which verifies the argon2 hash and returns a short-lived access JWT plus a refresh token set as an httpOnly, Secure, SameSite=Lax cookie. React holds the access token in memory only (not localStorage — XSS). An axios/fetch interceptor refreshes on 401 and retries once. Logout revokes the refresh token server-side via a denylist in Redis, because JWTs can't be un-issued.

---

# 10. Behavioural — prepare four stories

Use **STAR**: Situation, Task, Action, Result — with a number in the Result.

Have one story ready for each:
1. **A hard technical problem you solved.** The one where the diagnosis was the hard part, not the fix.
2. **A time you disagreed with someone.** They're testing whether you can hold a position *and* change your mind on evidence.
3. **Something you shipped that broke.** Own it plainly, then spend most of the story on what you changed so it couldn't recur.
4. **Something you improved that nobody asked you to.** Shows ownership.

**Questions worth asking them** (this is scored):
- What does the first 90 days look like for this role?
- How do changes reach production — who reviews, what's the test and deploy story?
- What's the biggest piece of technical debt the team is living with?
- How is success measured for this team in six months?

---

# 11. Final 30-minute checklist

- [ ] Event loop: microtasks vs macrotasks, and the Node phase order
- [ ] Closures, `this`, prototype chain
- [ ] `unknown` vs `any`; discriminated unions + exhaustiveness
- [ ] Why keys matter; when `useEffect` is the wrong tool
- [ ] React re-render causes and the fix order (state down → memo → virtualise)
- [ ] GIL: threads for I/O, processes for CPU
- [ ] Mutable default arguments; generators for large data
- [ ] FastAPI: `async def` + blocking call = server stalled; `Depends` + `dependency_overrides`
- [ ] Index types and when an index is useless
- [ ] `EXPLAIN ANALYZE` red flags; MVCC and vacuum
- [ ] Window functions; keyset pagination over `OFFSET`
- [ ] N+1 queries — how they appear in both SQLAlchemy and any ORM
- [ ] One story each for: hard bug, disagreement, outage, initiative

**On the day:** think out loud, state your assumptions before you code, name the brute force before optimising, and say the complexity of what you wrote. An interviewer who can follow your reasoning will forgive a syntax slip; one who can't, won't.

Good luck.
