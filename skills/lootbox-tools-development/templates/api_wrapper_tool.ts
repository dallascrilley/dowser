/**
 * API Wrapper Tool Template
 *
 * Demonstrates wrapping an external API with proper error handling,
 * caching, and type safety. Copy and customize for your API.
 */

// ============================================================================
// Configuration
// ============================================================================

// Replace with your API's base URL
const API_BASE_URL = 'https://api.example.com/v1';

// Cache configuration (5-minute TTL)
const CACHE_TTL = 5 * 60 * 1000;
let cache: Map<string, { data: unknown; timestamp: number }> = new Map();

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Get cached data if still valid
 */
function getCached<T>(key: string): T | null {
  const cached = cache.get(key);
  if (cached && (Date.now() - cached.timestamp) < CACHE_TTL) {
    return cached.data as T;
  }
  return null;
}

/**
 * Store data in cache
 */
function setCache(key: string, data: unknown): void {
  cache.set(key, { data, timestamp: Date.now() });
}

/**
 * Make authenticated API request
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  // Get API key from environment
  const apiKey = Deno.env.get('EXAMPLE_API_KEY');
  if (!apiKey) {
    throw new Error('EXAMPLE_API_KEY environment variable is not set');
  }

  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorBody}`);
  }

  return response.json() as Promise<T>;
}

// ============================================================================
// SEARCH - Search the API with caching
// ============================================================================

export interface SearchArgs {
  query: string;
  limit?: number;
  useCache?: boolean;
}

export interface SearchResult {
  results: Array<{
    id: string;
    title: string;
    description: string;
  }>;
  total: number;
  cached: boolean;
}

/**
 * Search the API with optional caching
 * @param args.query - Search query string
 * @param args.limit - Maximum results to return (default: 10)
 * @param args.useCache - Whether to use cached results (default: true)
 */
export async function search(args: SearchArgs): Promise<SearchResult> {
  // Input validation
  if (!args.query || args.query.trim() === '') {
    throw new Error('Query is required and cannot be empty');
  }

  const limit = args.limit ?? 10;
  const useCache = args.useCache ?? true;
  const cacheKey = `search:${args.query}:${limit}`;

  // Check cache first
  if (useCache) {
    const cached = getCached<SearchResult>(cacheKey);
    if (cached) {
      return { ...cached, cached: true };
    }
  }

  // Make API request
  const response = await apiRequest<{
    data: Array<{ id: string; title: string; description: string }>;
    meta: { total: number };
  }>(`/search?q=${encodeURIComponent(args.query)}&limit=${limit}`);

  const result: SearchResult = {
    results: response.data,
    total: response.meta.total,
    cached: false
  };

  // Cache the result
  setCache(cacheKey, result);

  return result;
}

// ============================================================================
// GET_ITEM - Get a single item by ID
// ============================================================================

export interface GetItemArgs {
  id: string;
}

export interface GetItemResult {
  item: {
    id: string;
    title: string;
    description: string;
    createdAt: string;
    updatedAt: string;
  } | null;
  found: boolean;
}

/**
 * Get a single item by ID
 * @param args.id - The item ID to retrieve
 */
export async function getItem(args: GetItemArgs): Promise<GetItemResult> {
  if (!args.id || args.id.trim() === '') {
    throw new Error('ID is required');
  }

  try {
    const item = await apiRequest<{
      id: string;
      title: string;
      description: string;
      createdAt: string;
      updatedAt: string;
    }>(`/items/${encodeURIComponent(args.id)}`);

    return { item, found: true };
  } catch (error) {
    // Handle 404 gracefully
    if (error instanceof Error && error.message.includes('404')) {
      return { item: null, found: false };
    }
    throw error;
  }
}

// ============================================================================
// CREATE_ITEM - Create a new item
// ============================================================================

export interface CreateItemArgs {
  title: string;
  description?: string;
}

export interface CreateItemResult {
  id: string;
  success: boolean;
}

/**
 * Create a new item
 * @param args.title - Item title (required)
 * @param args.description - Item description (optional)
 */
export async function createItem(args: CreateItemArgs): Promise<CreateItemResult> {
  if (!args.title || args.title.trim() === '') {
    throw new Error('Title is required');
  }

  const response = await apiRequest<{ id: string }>('/items', {
    method: 'POST',
    body: JSON.stringify({
      title: args.title,
      description: args.description ?? ''
    })
  });

  // Invalidate search cache since we added a new item
  cache.clear();

  return {
    id: response.id,
    success: true
  };
}

// ============================================================================
// CLEAR_CACHE - Clear the local cache
// ============================================================================

export interface ClearCacheArgs {
  prefix?: string;
}

export interface ClearCacheResult {
  cleared: number;
}

/**
 * Clear cached API responses
 * @param args.prefix - Only clear keys starting with this prefix
 */
export async function clearCache(args: ClearCacheArgs): Promise<ClearCacheResult> {
  if (args.prefix) {
    let cleared = 0;
    for (const key of cache.keys()) {
      if (key.startsWith(args.prefix)) {
        cache.delete(key);
        cleared++;
      }
    }
    return { cleared };
  }

  const cleared = cache.size;
  cache.clear();
  return { cleared };
}
