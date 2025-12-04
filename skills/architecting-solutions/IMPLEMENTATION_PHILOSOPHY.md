# Implementation Philosophy

Core implementation philosophy and guidelines for software development projects—a central reference for decision-making and development approach.

## Core Philosophy

Zen-like minimalism valuing simplicity and clarity:

- **Wabi-sabi philosophy**: Embrace simplicity and the essential
- **Occam's Razor**: Simple as possible, no simpler
- **Trust in emergence**: Complex systems from simple components
- **Present-moment focus**: Current needs, not future scenarios
- **Pragmatic trust**: Handle failures as they occur

Values clear documentation, readable code, and emergent architecture.

## Core Design Principles

### 1. Ruthless Simplicity

- Simple as possible, no simpler
- Every abstraction must justify itself
- Start minimal, grow as needed
- Don't build for hypothetical futures
- Regularly challenge complexity

### 2. Architectural Integrity with Minimal Implementation

- Preserve key patterns (MCP, SSE, separate I/O channels)
- Maintain benefits with simpler code
- Lightweight implementations, solid foundations
- Complete flows over perfect components

### 3. Library vs Custom Code

A judgment call evolving with requirements. No rigid rules—understand trade-offs and revisit as needed.

**Evolution:** Start simple → Switch when complex → Return to custom when outgrowing library

**Custom code when:** Need is simple, exact requirements, libraries need workarounds, unique domain problem

**Libraries when:** Solve complex problems, align well, battle-tested, complexity exceeds integration cost

**Making the call:** Alignment with needs? Fighting or working with library? Clean integration? Future requirements within capabilities? Problem complex enough for dependency?

**Stay flexible:** Minimal, isolated integration points. No shame switching approaches.

## Technical Implementation Guidelines

**API Layer:** Essential endpoints, minimal middleware, clear errors, consistent patterns

**Database:** Simple schema, TEXT/JSON fields to avoid early normalization, add indexes when needed

**MCP:** Streamlined client, use FastMCP when possible, core functionality, simple lifecycle, essential health checks

**SSE:** Basic connection management, simple subscriptions, direct delivery, minimal state

**Event System:** Simple pub/sub, direct delivery, clear minimal payloads, basic error handling

**LLM Integration:** Direct PydanticAI, minimal transformation, handle common errors, skip elaborate caching initially

**Message Routing:** Simplified queue-based processing, direct routing

## Development Approach

**Vertical Slices:** End-to-end functionality, core journeys first, data through all layers early

**Iterative:** 80/20 principle, one working > multiple partial, validate before enhancing, refactor as patterns emerge

**Testing:** Integration and e2e emphasis, manual testability, critical path first, unit tests for complex logic (60% unit, 30% integration, 10% e2e)

**Errors:** Handle common robustly, log detailed info, clear user messages, fail fast and visibly in development

## Decision-Making Framework

1. **Necessity**: Need this now?
2. **Simplicity**: Simplest solution?
3. **Directness**: More direct approach?
4. **Value**: Complexity adds proportional value?
5. **Maintenance**: Easy to understand and change?

## Areas to Embrace Complexity

1. Security fundamentals
2. Data integrity
3. Core user experience
4. Error visibility

## Areas to Aggressively Simplify

1. Internal abstractions
2. Generic "future-proof" code
3. Edge case handling
4. Framework usage
5. State management

## Practical Examples

### Good: Direct SSE Implementation

```python
class SseManager:
    def __init__(self):
        self.connections = {}

    async def add_connection(self, resource_id, user_id):
        connection_id = str(uuid.uuid4())
        queue = asyncio.Queue()
        self.connections[connection_id] = {
            "resource_id": resource_id,
            "user_id": user_id,
            "queue": queue
        }
        return queue, connection_id

    async def send_event(self, resource_id, event_type, data):
        for conn_id, conn in self.connections.items():
            if conn["resource_id"] == resource_id:
                await conn["queue"].put({
                    "event": event_type,
                    "data": data
                })
```

### Bad: Over-engineered SSE

```python
class ConnectionRegistry:
    def __init__(self, metrics_collector, cleanup_interval=60):
        self.connections_by_id = {}
        self.connections_by_resource = defaultdict(list)
        self.connections_by_user = defaultdict(list)
        self.metrics_collector = metrics_collector
        self.cleanup_task = asyncio.create_task(self._cleanup_loop(cleanup_interval))
    # [50+ more lines of complex indexing and state management]
```

### Good: Simple MCP Client

```python
class McpClient:
    def __init__(self, endpoint: str, service_name: str):
        self.endpoint = endpoint
        self.service_name = service_name
        self.client = None

    async def connect(self):
        if self.client is not None:
            return
        try:
            async with sse_client(self.endpoint) as (read_stream, write_stream):
                self.client = ClientSession(read_stream, write_stream)
                await self.client.initialize()
        except Exception as e:
            self.client = None
            raise RuntimeError(f"Failed to connect to {self.service_name}: {str(e)}")

    async def call_tool(self, name: str, arguments: dict):
        if not self.client:
            await self.connect()
        return await self.client.call_tool(name=name, arguments=arguments)
```

### Bad: Over-engineered MCP Client

```python
class EnhancedMcpClient:
    def __init__(self, endpoint, service_name, retry_strategy, health_check_interval):
        self.endpoint = endpoint
        self.service_name = service_name
        self.state = ConnectionState.DISCONNECTED
        self.retry_strategy = retry_strategy
        self.connection_attempts = 0
        self.last_error = None
        self.health_check_interval = health_check_interval
        # [50+ more lines of complex state tracking and retry logic]
```

## Remember

- Easier to add complexity later than remove it
- Code you don't write has no bugs
- Favor clarity over cleverness
- Best code is often simplest
