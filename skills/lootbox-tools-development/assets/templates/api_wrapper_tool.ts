/**
 * API Wrapper Tool Template
 *
 * Use this template to wrap external APIs as lootbox tools.
 * Customize:
 * 1. Replace API_BASE_URL with actual API endpoint
 * 2. Add authentication headers if needed
 * 3. Customize request/response handling
 * 4. Add error handling for API-specific errors
 */

// ===== Configuration =====

const API_BASE_URL = "https://api.example.com";
const API_KEY = Deno.env.get("API_KEY") || "";
const REQUEST_TIMEOUT = 30000; // 30 seconds

// ===== Interfaces =====

export interface SearchArgs {
  query: string;
  limit?: number;
  offset?: number;
}

export interface SearchResult {
  items: Array<{
    id: string;
    title: string;
    description: string;
    url?: string;
  }>;
  total: number;
  limit: number;
  offset: number;
}

export interface GetItemArgs {
  itemId: string;
}

export interface GetItemResult {
  id: string;
  title: string;
  description: string;
  data: unknown;
  cached: boolean;
}

export interface CreateItemArgs {
  title: string;
  description: string;
  data?: unknown;
}

export interface CreateItemResult {
  success: boolean;
  itemId?: string;
  error?: string;
}

export interface UpdateItemArgs {
  itemId: string;
  title?: string;
  description?: string;
  data?: unknown;
}

export interface UpdateItemResult {
  success: boolean;
  itemId?: string;
  error?: string;
}

export interface DeleteItemArgs {
  itemId: string;
}

export interface DeleteItemResult {
  success: boolean;
  itemId?: string;
  error?: string;
}

// ===== Helper Functions =====

/**
 * Make authenticated API request
 */
async function apiRequest<T>(
  method: string,
  endpoint: string,
  body?: unknown
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const options: RequestInit = {
    method,
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${API_KEY}`,
    },
    signal: AbortSignal.timeout(REQUEST_TIMEOUT),
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(url, options);

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API error ${response.status}: ${error}`);
    }

    return await response.json() as T;
  } catch (error) {
    throw new Error(`API request failed: ${error.message}`);
  }
}

// ===== Simple Caching =====

interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

const cache = new Map<string, CacheEntry<unknown>>();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

function getCached<T>(key: string): T | null {
  const entry = cache.get(key) as CacheEntry<T> | undefined;
  if (!entry) return null;

  if (Date.now() - entry.timestamp > CACHE_TTL) {
    cache.delete(key);
    return null;
  }

  return entry.data;
}

function setCached<T>(key: string, data: T): void {
  cache.set(key, {
    data,
    timestamp: Date.now(),
  });
}

// ===== Exported Functions =====

/**
 * Search for items
 */
export async function search(args: SearchArgs): Promise<SearchResult> {
  if (!args.query || args.query.trim() === "") {
    throw new Error("Query is required");
  }

  const limit = args.limit || 10;
  const offset = args.offset || 0;

  try {
    const result = await apiRequest<SearchResult>(
      "GET",
      `/search?q=${encodeURIComponent(args.query)}&limit=${limit}&offset=${offset}`
    );

    return result;
  } catch (error) {
    throw new Error(`Search failed: ${error.message}`);
  }
}

/**
 * Get a single item (with caching)
 */
export async function getItem(args: GetItemArgs): Promise<GetItemResult> {
  if (!args.itemId || args.itemId.trim() === "") {
    throw new Error("Item ID is required");
  }

  // Check cache first
  const cached = getCached<GetItemResult>(`item:${args.itemId}`);
  if (cached) {
    return { ...cached, cached: true };
  }

  try {
    const item = await apiRequest<{
      id: string;
      title: string;
      description: string;
      data: unknown;
    }>("GET", `/items/${args.itemId}`);

    const result: GetItemResult = {
      ...item,
      cached: false,
    };

    setCached(`item:${args.itemId}`, result);
    return result;
  } catch (error) {
    throw new Error(`Failed to get item: ${error.message}`);
  }
}

/**
 * Create a new item
 */
export async function createItem(args: CreateItemArgs): Promise<CreateItemResult> {
  if (!args.title || args.title.trim() === "") {
    return { success: false, error: "Title is required" };
  }

  try {
    const response = await apiRequest<{ id: string }>(
      "POST",
      "/items",
      {
        title: args.title,
        description: args.description || "",
        data: args.data || {},
      }
    );

    return {
      success: true,
      itemId: response.id,
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
    };
  }
}

/**
 * Update an existing item
 */
export async function updateItem(args: UpdateItemArgs): Promise<UpdateItemResult> {
  if (!args.itemId || args.itemId.trim() === "") {
    return { success: false, error: "Item ID is required" };
  }

  const updates: Record<string, unknown> = {};
  if (args.title !== undefined) updates.title = args.title;
  if (args.description !== undefined) updates.description = args.description;
  if (args.data !== undefined) updates.data = args.data;

  if (Object.keys(updates).length === 0) {
    return { success: false, error: "No updates provided" };
  }

  try {
    await apiRequest<void>("PUT", `/items/${args.itemId}`, updates);

    // Invalidate cache
    cache.delete(`item:${args.itemId}`);

    return {
      success: true,
      itemId: args.itemId,
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
    };
  }
}

/**
 * Delete an item
 */
export async function deleteItem(args: DeleteItemArgs): Promise<DeleteItemResult> {
  if (!args.itemId || args.itemId.trim() === "") {
    return { success: false, error: "Item ID is required" };
  }

  try {
    await apiRequest<void>("DELETE", `/items/${args.itemId}`);

    // Invalidate cache
    cache.delete(`item:${args.itemId}`);

    return {
      success: true,
      itemId: args.itemId,
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
    };
  }
}
