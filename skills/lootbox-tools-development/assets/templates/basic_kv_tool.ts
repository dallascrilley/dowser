/**
 * Basic Key-Value Store Tool Template
 *
 * Copy this file to .lootbox/tools/kv.ts and customize:
 * 1. Replace loadData/saveData with your storage implementation
 * 2. Add validation as needed
 * 3. Extend with additional functions (delete, list, etc.)
 */

// ===== Interfaces =====

export interface GetArgs {
  key: string;
  defaultValue?: unknown;
}

export interface GetResult {
  value: unknown;
  exists: boolean;
}

export interface SetArgs {
  key: string;
  value: unknown;
  ttl?: number;  // Time-to-live in seconds (optional)
}

export interface SetResult {
  success: boolean;
  key: string;
  sizeByte: number;
}

export interface DeleteArgs {
  key: string;
}

export interface DeleteResult {
  success: boolean;
  deleted: boolean;
}

export interface ListArgs {
  pattern?: string;  // Optional glob pattern to filter keys
  limit?: number;    // Max results (default 100)
}

export interface ListResult {
  keys: string[];
  count: number;
}

// ===== Helper Functions =====

// Replace these with your actual storage implementation
let store: Record<string, { value: unknown; expires?: number }> = {};

async function loadData(): Promise<Record<string, { value: unknown; expires?: number }>> {
  // TODO: Load from file, database, or cache
  // Example: const data = await Deno.readTextFile('./store.json');
  // return JSON.parse(data);
  return store;
}

async function saveData(data: Record<string, { value: unknown; expires?: number }>): Promise<void> {
  // TODO: Save to file, database, or cache
  // Example: await Deno.writeTextFile('./store.json', JSON.stringify(data, null, 2));
  store = data;
}

// ===== Exported Functions =====

/**
 * Get a value from the store
 */
export async function get(args: GetArgs): Promise<GetResult> {
  if (!args.key || args.key.trim() === "") {
    throw new Error("Key is required");
  }

  const data = await loadData();
  const entry = data[args.key];

  // Check expiration
  if (entry && entry.expires && Date.now() > entry.expires) {
    delete data[args.key];
    await saveData(data);
    return {
      value: args.defaultValue || null,
      exists: false,
    };
  }

  const value = entry?.value;

  return {
    value: value !== undefined ? value : args.defaultValue,
    exists: value !== undefined,
  };
}

/**
 * Set a value in the store
 */
export async function set(args: SetArgs): Promise<SetResult> {
  if (!args.key || args.key.trim() === "") {
    throw new Error("Key is required");
  }

  const data = await loadData();
  const valueStr = JSON.stringify(args.value);
  const sizeByte = Buffer.byteLength(valueStr);

  data[args.key] = {
    value: args.value,
    expires: args.ttl ? Date.now() + args.ttl * 1000 : undefined,
  };

  await saveData(data);

  return {
    success: true,
    key: args.key,
    sizeByte,
  };
}

/**
 * Delete a value from the store
 */
export async function delete(args: DeleteArgs): Promise<DeleteResult> {
  if (!args.key || args.key.trim() === "") {
    throw new Error("Key is required");
  }

  const data = await loadData();
  const deleted = args.key in data;

  if (deleted) {
    delete data[args.key];
    await saveData(data);
  }

  return {
    success: true,
    deleted,
  };
}

/**
 * List all keys in the store
 */
export async function list(args: ListArgs): Promise<ListResult> {
  const data = await loadData();
  let keys = Object.keys(data);

  // Filter by pattern if provided
  if (args.pattern) {
    const regex = new RegExp(args.pattern);
    keys = keys.filter((k) => regex.test(k));
  }

  // Apply limit
  const limit = args.limit || 100;
  keys = keys.slice(0, limit);

  return {
    keys,
    count: keys.length,
  };
}

/**
 * Clear all data from the store
 */
export interface ClearResult {
  success: boolean;
  itemsCleared: number;
}

export async function clear(): Promise<ClearResult> {
  const data = await loadData();
  const itemsCleared = Object.keys(data).length;
  await saveData({});
  return {
    success: true,
    itemsCleared,
  };
}
