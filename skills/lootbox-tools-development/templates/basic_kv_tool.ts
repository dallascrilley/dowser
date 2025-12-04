/**
 * Basic Key-Value Store Tool Template
 *
 * A simple in-memory key-value store demonstrating proper lootbox tool patterns.
 * Copy this template to .lootbox/tools/<your-tool-name>.ts and customize.
 */

// In-memory storage (replace with persistent storage as needed)
const store: Record<string, unknown> = {};

// ============================================================================
// GET - Retrieve a value by key
// ============================================================================

export interface GetArgs {
  key: string;
}

export interface GetResult {
  value: unknown;
  exists: boolean;
}

/**
 * Retrieves a value from the store by key
 * @param args.key - The key to look up
 * @returns The value and whether it exists
 */
export async function get(args: GetArgs): Promise<GetResult> {
  // Input validation
  if (!args.key || args.key.trim() === '') {
    throw new Error('Key is required and cannot be empty');
  }

  const value = store[args.key];
  return {
    value,
    exists: value !== undefined
  };
}

// ============================================================================
// SET - Store a value with a key
// ============================================================================

export interface SetArgs {
  key: string;
  value: unknown;
}

export interface SetResult {
  success: boolean;
  key: string;
  previousValue?: unknown;
}

/**
 * Stores a value in the store with the given key
 * @param args.key - The key to store under
 * @param args.value - The value to store
 * @returns Success status and previous value if overwritten
 */
export async function set(args: SetArgs): Promise<SetResult> {
  if (!args.key || args.key.trim() === '') {
    throw new Error('Key is required and cannot be empty');
  }

  const previousValue = store[args.key];
  store[args.key] = args.value;

  return {
    success: true,
    key: args.key,
    previousValue
  };
}

// ============================================================================
// DELETE - Remove a key from the store
// ============================================================================

export interface DeleteArgs {
  key: string;
}

export interface DeleteResult {
  success: boolean;
  existed: boolean;
}

/**
 * Deletes a key from the store
 * @param args.key - The key to delete
 * @returns Whether the operation succeeded and if the key existed
 */
export async function del(args: DeleteArgs): Promise<DeleteResult> {
  if (!args.key || args.key.trim() === '') {
    throw new Error('Key is required and cannot be empty');
  }

  const existed = args.key in store;
  delete store[args.key];

  return {
    success: true,
    existed
  };
}

// ============================================================================
// LIST - List all keys (with optional prefix filter)
// ============================================================================

export interface ListArgs {
  prefix?: string;
  limit?: number;
}

export interface ListResult {
  keys: string[];
  total: number;
}

/**
 * Lists all keys in the store
 * @param args.prefix - Optional prefix to filter keys
 * @param args.limit - Maximum number of keys to return
 * @returns List of matching keys
 */
export async function list(args: ListArgs): Promise<ListResult> {
  let keys = Object.keys(store);

  // Filter by prefix if provided
  if (args.prefix) {
    keys = keys.filter(k => k.startsWith(args.prefix!));
  }

  const total = keys.length;

  // Apply limit if provided
  if (args.limit && args.limit > 0) {
    keys = keys.slice(0, args.limit);
  }

  return {
    keys,
    total
  };
}
