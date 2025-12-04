# Lootbox Tool Interface Specification

Complete reference for defining tool interfaces in lootbox.

## Required Format for Tool Functions

Every tool function must follow this pattern:

```typescript
// 1. Define Args interface (parameters)
export interface GetArgs {
  key: string;
  defaultValue?: unknown;  // Optional parameters with ?
}

// 2. Define Result interface (return value)
export interface GetResult {
  value: unknown;
  exists: boolean;
}

// 3. Export async function with standard signature
export async function get(args: GetArgs): Promise<GetResult> {
  // Implementation
  return {
    value: data,
    exists: true,
  };
}
```

## Required Properties

| Property | Type | Description |
|----------|------|-------------|
| Function name | string | Exported function name (becomes tool method name) |
| Arguments | Interface | Named `<FunctionName>Args`, single parameter object |
| Return type | Interface | Named `<FunctionName>Result`, always async |
| async | keyword | All functions must be async |
| Export | keyword | Function must be `export` for discovery |

## Interface Naming Conventions

- **Arguments**: `<FunctionName>Args` (e.g., `GetArgs`, `CreateUserArgs`, `ProcessBatchArgs`)
- **Results**: `<FunctionName>Result` (e.g., `GetResult`, `CreateUserResult`, `ProcessBatchResult`)
- Both must be `export interface`
- Function name matches base name exactly (case-sensitive)

## Property Definitions

### Required Properties

Properties without `?` are required:

```typescript
export interface CreateArgs {
  name: string;        // Required: must provide
  email: string;       // Required: must provide
}
```

**Usage:**
```typescript
// ✅ Valid
await tools.user.create({ name: "Alice", email: "alice@example.com" });

// ❌ Invalid - missing required field
await tools.user.create({ name: "Alice" });  // ERROR
```

### Optional Properties

Use `?` to make properties optional:

```typescript
export interface CreateArgs {
  name: string;        // Required
  email: string;       // Required
  age?: number;        // Optional
  tags?: string[];     // Optional
}
```

**Usage:**
```typescript
// ✅ Valid - all variations
await tools.user.create({ name: "Alice", email: "alice@example.com" });
await tools.user.create({ name: "Alice", email: "alice@example.com", age: 30 });
await tools.user.create({ name: "Alice", email: "alice@example.com", age: 30, tags: ["admin"] });
```

## Type System

### Scalar Types

```typescript
export interface Args {
  count: number;           // Any number
  name: string;            // Any string
  isActive: boolean;       // true or false
  timestamp: number;       // Unix timestamp
}
```

### Complex Types

```typescript
export interface Args {
  // Array of scalars
  tags: string[];

  // Array of objects
  items: Array<{ id: string; value: number }>;

  // Object with known properties
  config: {
    timeout: number;
    retries: number;
  };

  // Unknown/dynamic data
  metadata: unknown;

  // Union types (one of several options)
  method: "GET" | "POST" | "PUT" | "DELETE";
}
```

### Special Type: `unknown`

Use `unknown` for flexible data that can be any type:

```typescript
export interface SetArgs {
  key: string;
  value: unknown;      // Can be string, number, object, array, etc.
}
```

This allows maximum flexibility while maintaining type safety in the wrapper.

## Result Interface Best Practices

Result interfaces should clearly communicate:

1. **Success/failure status** (if relevant)
2. **Primary data** (the result of the operation)
3. **Metadata** (timing, caching status, etc.)

### Pattern 1: Simple Success Result

```typescript
export interface AddResult {
  result: number;      // Primary result
  operation: string;   // Metadata
}
```

### Pattern 2: Success/Failure with Data

```typescript
export interface QueryResult {
  success: boolean;
  data?: unknown;      // Optional if success=true
  error?: string;      // Optional if success=false
}
```

### Pattern 3: Complex with Metadata

```typescript
export interface ProcessResult {
  success: boolean;
  itemsProcessed: number;
  itemsFailed: number;
  failures: Array<{ id: string; error: string }>;
  executionMs: number;
}
```

## Complete Example: User Management Tool

```typescript
// ===== Interfaces =====

export interface GetUserArgs {
  userId: string;
}

export interface GetUserResult {
  user?: {
    id: string;
    name: string;
    email: string;
    createdAt: number;
  };
  exists: boolean;
}

export interface CreateUserArgs {
  name: string;
  email: string;
  role?: "user" | "admin";
}

export interface CreateUserResult {
  success: boolean;
  userId?: string;
  error?: string;
}

export interface ListUsersArgs {
  limit?: number;
  offset?: number;
}

export interface ListUsersResult {
  users: Array<{
    id: string;
    name: string;
    email: string;
  }>;
  total: number;
  limit: number;
  offset: number;
}

export interface UpdateUserArgs {
  userId: string;
  updates: {
    name?: string;
    email?: string;
    role?: "user" | "admin";
  };
}

export interface UpdateUserResult {
  success: boolean;
  user?: {
    id: string;
    name: string;
    email: string;
  };
  error?: string;
}

export interface DeleteUserArgs {
  userId: string;
}

export interface DeleteUserResult {
  success: boolean;
  deletedId?: string;
  error?: string;
}

// ===== Functions =====

export async function getUser(args: GetUserArgs): Promise<GetUserResult> {
  const user = await loadUser(args.userId);
  return {
    user: user || undefined,
    exists: !!user,
  };
}

export async function createUser(args: CreateUserArgs): Promise<CreateUserResult> {
  // Validate
  if (!args.name || args.name.trim() === "") {
    return { success: false, error: "Name is required" };
  }
  if (!args.email || !args.email.includes("@")) {
    return { success: false, error: "Valid email is required" };
  }

  // Create
  const userId = generateId();
  await saveUser({
    id: userId,
    name: args.name,
    email: args.email,
    role: args.role || "user",
    createdAt: Date.now(),
  });

  return { success: true, userId };
}

export async function listUsers(args: ListUsersArgs): Promise<ListUsersResult> {
  const limit = args.limit || 10;
  const offset = args.offset || 0;

  const allUsers = await loadAllUsers();
  const paginatedUsers = allUsers.slice(offset, offset + limit);

  return {
    users: paginatedUsers.map((u) => ({
      id: u.id,
      name: u.name,
      email: u.email,
    })),
    total: allUsers.length,
    limit,
    offset,
  };
}

export async function updateUser(args: UpdateUserArgs): Promise<UpdateUserResult> {
  const user = await loadUser(args.userId);
  if (!user) {
    return { success: false, error: "User not found" };
  }

  // Apply updates
  if (args.updates.name) user.name = args.updates.name;
  if (args.updates.email) user.email = args.updates.email;
  if (args.updates.role) user.role = args.updates.role;

  await saveUser(user);

  return {
    success: true,
    user: {
      id: user.id,
      name: user.name,
      email: user.email,
    },
  };
}

export async function deleteUser(args: DeleteUserArgs): Promise<DeleteUserResult> {
  const exists = await userExists(args.userId);
  if (!exists) {
    return { success: false, error: "User not found" };
  }

  await removeUser(args.userId);

  return { success: true, deletedId: args.userId };
}
```

## Common Type Patterns

### Pagination

```typescript
export interface ListArgs {
  limit?: number;    // Results per page (default 10)
  offset?: number;   // Starting position (default 0)
}

export interface ListResult {
  items: unknown[];
  total: number;
  limit: number;
  offset: number;
}
```

### Filtering

```typescript
export interface SearchArgs {
  query: string;
  filters?: {
    status?: "active" | "inactive";
    createdAfter?: number;
    createdBefore?: number;
  };
}
```

### Batch Operations

```typescript
export interface BatchProcessArgs {
  items: Array<{ id: string; data: unknown }>;
}

export interface BatchProcessResult {
  successful: Array<{ id: string; result: unknown }>;
  failed: Array<{ id: string; error: string }>;
}
```

### Error Responses

Choose ONE approach per tool:

**Approach 1: Throw Errors**
```typescript
export async function create(args: CreateArgs): Promise<CreateResult> {
  if (!args.name) throw new Error("Name required");
  // ...
  return { success: true };
}
```

**Approach 2: Return Errors in Result**
```typescript
export async function create(args: CreateArgs): Promise<CreateResult> {
  if (!args.name) {
    return { success: false, error: "Name required" };
  }
  // ...
  return { success: true };
}
```

## Validation Checklist

Before using your tool interfaces:

- [ ] All interfaces are `export interface`
- [ ] Args interface named `<FunctionName>Args`
- [ ] Result interface named `<FunctionName>Result`
- [ ] Function signature: `export async function <name>(args: <Name>Args): Promise<<Name>Result>`
- [ ] All required fields documented (no `?`)
- [ ] Optional fields marked with `?`
- [ ] Complex types clearly defined (objects, arrays, unions)
- [ ] Result interface includes meaningful fields (not empty)
- [ ] No multiple parameters (args must be single object)
- [ ] Result always wrapped in object (not primitive)

## Testing Interfaces

To verify interfaces work correctly:

```bash
# Extract type definitions
lootbox tools types mytool

# Test function call
lootbox exec 'await tools.mytool.myfunction({param: "value"})'

# Should show proper types with IDE autocomplete
```

## File Organization

Place all related interfaces and functions in one tool file:

```typescript
// .lootbox/tools/users.ts

// Interfaces (grouped by function)
export interface GetUserArgs { ... }
export interface GetUserResult { ... }

export interface CreateUserArgs { ... }
export interface CreateUserResult { ... }

// Functions
export async function getUser(args: GetUserArgs): Promise<GetUserResult> { }
export async function createUser(args: CreateUserArgs): Promise<CreateUserResult> { }
```

One file per namespace = easier to maintain and discover related functionality.
