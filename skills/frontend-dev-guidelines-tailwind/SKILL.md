---
name: frontend-dev-guidelines-tailwind
description: >-
  React 18+ best practices with Tailwind CSS and Shadcn/ui patterns. Component
  architecture, performance optimization, type safety, and modern React
  patterns.
when_to_use: >
  Use for React 18+ development with Tailwind CSS and Shadcn/ui, component
  architecture patterns, performance optimization,

  type safety with TypeScript, modern React patterns, utility-first styling, or
  building accessible component-first applications.
version: 1.0.0
category: coding
---

# Frontend Development Guidelines (React + Tailwind/Shadcn)

**Modern React Development with Tailwind CSS and Shadcn/ui**

This skill provides patterns for building performant, type-safe React applications using Tailwind CSS for styling and Shadcn/ui for component primitives.

## Core Philosophy

1. **Component-First** - Everything is a component
2. **Type Safety** - TypeScript everywhere
3. **Performance** - Suspense, lazy loading, proper memoization
4. **Accessibility** - ARIA, semantic HTML, keyboard navigation
5. **Utility-First Styling** - Tailwind CSS approach
6. **Composition** - Shadcn/ui headless components

---

## React 18+ Patterns

### Component Structure

**Functional Components (Required):**
```typescript
import { FC } from 'react';

interface PostCardProps {
  title: string;
  content: string;
  author: string;
  onEdit?: () => void;
}

export const PostCard: FC<PostCardProps> = ({
  title,
  content,
  author,
  onEdit
}) => {
  return (
    <div className="rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
      <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
      <p className="mt-2 text-gray-700">{content}</p>
      <div className="mt-4 flex items-center justify-between">
        <span className="text-sm text-gray-500">By {author}</span>
        {onEdit && (
          <button
            onClick={onEdit}
            className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Edit
          </button>
        )}
      </div>
    </div>
  );
};
```

### Modern React Patterns

#### 1. Suspense for Data Fetching
```typescript
import { Suspense } from 'react';
import { PostList } from './PostList';
import { PostListSkeleton } from './PostListSkeleton';

export const PostsPage = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-8 text-3xl font-bold">Posts</h1>
      <Suspense fallback={<PostListSkeleton />}>
        <PostList />
      </Suspense>
    </div>
  );
};
```

#### 2. Error Boundaries
```typescript
import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="flex min-h-screen items-center justify-center">
            <div className="rounded-lg bg-red-50 p-6 text-center">
              <h2 className="text-xl font-semibold text-red-900">Something went wrong</h2>
              <p className="mt-2 text-red-700">{this.state.error?.message}</p>
            </div>
          </div>
        )
      );
    }

    return this.props.children;
  }
}
```

#### 3. Custom Hooks
```typescript
import { useState, useEffect } from 'react';

interface UseAsyncResult<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

export function useAsync<T>(
  asyncFn: () => Promise<T>,
  dependencies: any[] = []
): UseAsyncResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;

    setLoading(true);
    asyncFn()
      .then(result => {
        if (!cancelled) {
          setData(result);
          setError(null);
        }
      })
      .catch(err => {
        if (!cancelled) {
          setError(err);
          setData(null);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, dependencies);

  return { data, loading, error };
}
```

---

## Tailwind CSS Patterns

### Utility-First Styling

**Core Principles:**
- Use utility classes directly in JSX
- Create custom classes via `@apply` for repeated patterns
- Use Tailwind's theme for consistency

**Example Component:**
```typescript
export const Card: FC<{ children: ReactNode }> = ({ children }) => {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow">
      {children}
    </div>
  );
};
```

### Responsive Design
```typescript
export const ResponsiveGrid = () => {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {/* Grid items */}
    </div>
  );
};
```

### Dark Mode Support
```typescript
export const ThemeToggle = () => {
  return (
    <button className="rounded-lg bg-gray-100 p-2 dark:bg-gray-800">
      <span className="text-gray-900 dark:text-gray-100">Toggle Theme</span>
    </button>
  );
};
```

### cn() Helper (Tailwind + Class Variance Authority)
```typescript
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Usage
<div className={cn(
  "rounded-lg p-4",
  isActive && "bg-blue-100",
  isDisabled && "opacity-50 cursor-not-allowed"
)} />
```

---

## Shadcn/ui Integration

### Component Installation

```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add dialog
```

### Using Shadcn Components

**Button:**
```typescript
import { Button } from '@/components/ui/button';

export const Actions = () => {
  return (
    <div className="flex gap-2">
      <Button variant="default">Primary</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="outline">Outline</Button>
      <Button variant="ghost">Ghost</Button>
      <Button variant="destructive">Delete</Button>
    </div>
  );
};
```

**Card:**
```typescript
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';

export const PostCard = () => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Blog Post Title</CardTitle>
        <CardDescription>Published on Nov 1, 2025</CardDescription>
      </CardHeader>
      <CardContent>
        <p>Post content goes here...</p>
      </CardContent>
      <CardFooter className="flex justify-between">
        <Button variant="outline">Edit</Button>
        <Button>Publish</Button>
      </CardFooter>
    </Card>
  );
};
```

**Dialog:**
```typescript
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';

export const ConfirmDialog = () => {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button>Open Dialog</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Are you sure?</DialogTitle>
          <DialogDescription>
            This action cannot be undone.
          </DialogDescription>
        </DialogHeader>
        <div className="flex justify-end gap-2">
          <Button variant="outline">Cancel</Button>
          <Button variant="destructive">Confirm</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};
```

---

## State Management

### useState for Local State
```typescript
export const Counter = () => {
  const [count, setCount] = useState(0);

  return (
    <div className="flex items-center gap-4">
      <Button onClick={() => setCount(c => c - 1)}>-</Button>
      <span className="text-2xl font-bold">{count}</span>
      <Button onClick={() => setCount(c => c + 1)}>+</Button>
    </div>
  );
};
```

### Context for Shared State
```typescript
import { createContext, useContext, useState, ReactNode } from 'react';

interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider = ({ children }: { children: ReactNode }) => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const toggleTheme = () => {
    setTheme(t => t === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      <div className={theme}>
        {children}
      </div>
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
};
```

---

## Performance Optimization

### 1. Code Splitting
```typescript
import { lazy, Suspense } from 'react';

const HeavyComponent = lazy(() => import('./HeavyComponent'));

export const Page = () => {
  return (
    <Suspense fallback={<div className="animate-pulse">Loading...</div>}>
      <HeavyComponent />
    </Suspense>
  );
};
```

### 2. Memoization
```typescript
import { memo, useMemo, useCallback } from 'react';

// Memoize expensive computations
export const ExpensiveComponent = ({ data }: { data: number[] }) => {
  const processedData = useMemo(() => {
    return data.map(n => n * 2).filter(n => n > 10);
  }, [data]);

  return <div>{processedData.join(', ')}</div>;
};

// Memoize components
export const MemoizedCard = memo(PostCard);

// Memoize callbacks
export const Parent = () => {
  const handleClick = useCallback(() => {
    console.log('Clicked');
  }, []);

  return <MemoizedCard onEdit={handleClick} />;
};
```

### 3. Virtual Scrolling (Large Lists)
```typescript
import { useVirtualizer } from '@tanstack/react-virtual';

export const VirtualList = ({ items }: { items: any[] }) => {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
  });

  return (
    <div ref={parentRef} className="h-[400px] overflow-auto">
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
        {virtualizer.getVirtualItems().map(virtualItem => (
          <div
            key={virtualItem.index}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            {items[virtualItem.index].name}
          </div>
        ))}
      </div>
    </div>
  );
};
```

---

## Form Handling

### React Hook Form + Zod
```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';

const postSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  content: z.string().min(10, 'Content must be at least 10 characters'),
  tags: z.array(z.string()).optional(),
});

type PostFormData = z.infer<typeof postSchema>;

export const PostForm = () => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<PostFormData>({
    resolver: zodResolver(postSchema),
  });

  const onSubmit = async (data: PostFormData) => {
    await createPost(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700">
          Title
        </label>
        <input
          {...register('title')}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
        {errors.title && (
          <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
        )}
      </div>

      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </Button>
    </form>
  );
};
```

---

## File Organization

### Recommended Structure

```
src/
├── components/
│   ├── ui/                    # Shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── dialog.tsx
│   └── shared/                # Shared components
│       ├── Header.tsx
│       ├── Footer.tsx
│       └── Layout.tsx
├── features/                  # Feature-based organization
│   ├── posts/
│   │   ├── components/
│   │   │   ├── PostCard.tsx
│   │   │   ├── PostForm.tsx
│   │   │   └── PostList.tsx
│   │   ├── hooks/
│   │   │   └── usePosts.ts
│   │   └── types.ts
│   └── users/
│       └── ...
├── lib/                       # Utilities
│   ├── utils.ts               # cn() helper, etc.
│   ├── api.ts                 # API client
│   └── constants.ts
├── hooks/                     # Global hooks
│   ├── useAuth.ts
│   └── useTheme.ts
└── App.tsx
```

---

## Accessibility

### ARIA Labels
```typescript
<button
  aria-label="Close dialog"
  aria-describedby="dialog-description"
  onClick={onClose}
>
  <X className="h-4 w-4" />
</button>
```

### Keyboard Navigation
```typescript
const handleKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
  if (e.key === 'Escape') {
    onClose();
  }
  if (e.key === 'Enter') {
    onSubmit();
  }
};

<div
  role="dialog"
  tabIndex={-1}
  onKeyDown={handleKeyDown}
>
  {/* Dialog content */}
</div>
```

### Focus Management
```typescript
import { useEffect, useRef } from 'react';

export const Modal = ({ isOpen, onClose }: ModalProps) => {
  const closeButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (isOpen) {
      closeButtonRef.current?.focus();
    }
  }, [isOpen]);

  return (
    <div role="dialog" aria-modal="true">
      <button ref={closeButtonRef} onClick={onClose}>
        Close
      </button>
    </div>
  );
};
```

---

## TypeScript Best Practices

### Component Props
```typescript
// ✅ Good - Explicit prop types
interface ButtonProps {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  onClick?: () => void;
  children: ReactNode;
}

// ❌ Bad - Using 'any'
interface BadProps {
  data: any;
  onClick: any;
}
```

### Generic Components
```typescript
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => ReactNode;
  keyExtractor: (item: T) => string;
}

export function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
  return (
    <div className="space-y-2">
      {items.map(item => (
        <div key={keyExtractor(item)}>
          {renderItem(item)}
        </div>
      ))}
    </div>
  );
}
```

---

## Quick Reference

### When to Use

✅ Building React components
✅ Styling with Tailwind CSS
✅ Using Shadcn/ui components
✅ Performance optimization
✅ Form handling
✅ State management
✅ TypeScript type safety

### Common Patterns

**Loading States:**
```typescript
{loading ? <Skeleton /> : <Content />}
```

**Error States:**
```typescript
{error ? <ErrorMessage error={error} /> : <Content />}
```

**Conditional Rendering:**
```typescript
{isLoggedIn && <UserMenu />}
{posts.length > 0 ? <PostList /> : <EmptyState />}
```

**List Rendering:**
```typescript
{posts.map(post => (
  <PostCard key={post.id} {...post} />
))}
```

---

## Common Mistakes

❌ **DON'T:**
- Use class components (use functional components)
- Mutate state directly
- Forget keys in lists
- Skip accessibility attributes
- Use inline styles (use Tailwind classes)
- Ignore TypeScript errors

✅ **DO:**
- Use functional components with hooks
- Update state immutably
- Provide stable keys for lists
- Add ARIA labels and roles
- Use Tailwind utility classes
- Maintain strict type safety

---

## Related Tools

- **React 18+** - Modern React features
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **Shadcn/ui** - Headless component library
- **React Hook Form** - Form management
- **Zod** - Schema validation
- **TanStack Query** - Data fetching
- **TanStack Virtual** - Virtual scrolling

---

**Remember:** This skill focuses on React + Tailwind + Shadcn patterns. Adapt examples to your specific project structure and requirements.
