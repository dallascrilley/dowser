---
name: backend-dev-guidelines-universal
description: >-
  Framework-agnostic backend architecture patterns - Layered design, error
  handling, testing strategies. Adapted for Express, NestJS, Fastify, Django,
  Go, or any backend framework.
when_to_use: >
  Use for framework-agnostic backend architecture, layered design patterns,
  error handling strategies, testing approaches, or

  building backends with Express, NestJS, Fastify, Django, FastAPI, Go, Spring
  Boot, or any backend framework.
version: 1.0.0
category: coding
---

# Backend Development Guidelines (Universal)

**Framework-Agnostic Patterns for Any Backend Stack**

This skill provides architecture patterns that work across frameworks: Express, NestJS, Fastify, Django, FastAPI, Go (Gin/Echo), Spring Boot, etc.

## Core Philosophy

1. **Layered Architecture** - Separation of concerns (Routes → Controllers → Services → Repositories)
2. **Ruthless Simplicity** - Start simple, add complexity only when needed
3. **Type Safety** - Use strong typing (TypeScript, Python type hints, Go types)
4. **Error Handling** - Consistent, structured error responses
5. **Testability** - Each layer independently testable

---

## Architecture Layers

### Layer 1: Routes (HTTP Layer)
**Purpose:** Map HTTP endpoints to controllers
**Responsibilities:**
- Define URL patterns
- HTTP method handlers (GET, POST, PUT, DELETE)
- Minimal logic (route registration only)

**Pattern (Framework Agnostic):**
```
Route Definition:
  Path: /api/resource
  Method: POST
  Handler: ResourceController.create
  Middleware: [auth, validation]
```

**Express Example:**
```typescript
router.post('/api/posts', authMiddleware, PostController.create);
```

**Django Example:**
```python
path('api/posts/', PostController.as_view(), name='create-post')
```

**Go (Gin) Example:**
```go
router.POST("/api/posts", authMiddleware, postController.Create)
```

---

### Layer 2: Controllers (Request/Response Layer)
**Purpose:** Handle HTTP requests and responses
**Responsibilities:**
- Parse request data (body, params, query)
- Call service layer
- Format responses
- Handle HTTP-specific errors (400, 401, 404, 500)

**Pattern (Pseudo-code):**
```
Controller.create(request):
  1. Extract data from request
  2. Validate input (basic HTTP validation)
  3. Call Service.create(data)
  4. Return formatted response with status code
  5. Catch errors and return appropriate HTTP status
```

**Key Principles:**
- Controllers should be thin (orchestration only)
- No business logic in controllers
- Return consistent response format:
  ```json
  {
    "success": true,
    "data": {},
    "error": null
  }
  ```

---

### Layer 3: Services (Business Logic Layer)
**Purpose:** Core business logic
**Responsibilities:**
- Business rule enforcement
- Data validation (business rules, not HTTP)
- Orchestrate multiple repositories
- Transaction management
- Complex calculations

**Pattern (Pseudo-code):**
```
Service.create(data):
  1. Validate business rules
  2. Transform data if needed
  3. Call Repository.create(data)
  4. Perform side effects (events, notifications)
  5. Return result
```

**Key Principles:**
- Services are framework-agnostic (no HTTP knowledge)
- Testable without HTTP layer
- Single Responsibility Principle
- Services can call other services
- Handle business errors (validation, conflicts)

---

### Layer 4: Repositories (Data Access Layer)
**Purpose:** Database/external data access
**Responsibilities:**
- CRUD operations
- Query construction
- Data mapping (DB ↔ Domain models)
- Connection management

**Pattern (Pseudo-code):**
```
Repository.create(data):
  1. Map domain model to DB model
  2. Execute database insert
  3. Return created entity
  4. Throw data errors (constraint violations)
```

**Key Principles:**
- Repositories know about database, not business logic
- Consistent method names: `create()`, `findById()`, `update()`, `delete()`
- Return domain models, not raw DB results
- Handle DB-specific errors

---

## Error Handling Strategy

### Error Types

1. **Validation Errors** (400)
   - Invalid input format
   - Missing required fields
   - Type mismatches

2. **Authentication Errors** (401)
   - Missing or invalid credentials
   - Expired tokens

3. **Authorization Errors** (403)
   - Insufficient permissions
   - Resource access denied

4. **Not Found Errors** (404)
   - Resource doesn't exist

5. **Conflict Errors** (409)
   - Duplicate keys
   - Business rule violations

6. **Server Errors** (500)
   - Unexpected failures
   - External service failures

### Error Structure (Universal)

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ],
    "timestamp": "2025-11-01T10:30:00Z"
  }
}
```

### Error Handling Pattern

**Layer-Specific Error Handling:**

**Repository Layer:**
```
Throws: DataError (DB constraint violations, connection errors)
Example: DuplicateKeyError, ForeignKeyViolationError
```

**Service Layer:**
```
Catches: DataError
Throws: BusinessError (business rule violations)
Example: InsufficientFundsError, InvalidStateTransitionError
```

**Controller Layer:**
```
Catches: BusinessError, DataError
Maps to: HTTP status codes
Returns: Formatted error response
```

---

## Validation Strategy

### Input Validation (Controllers)
- Basic type checking
- Required fields
- Format validation (email, URL, etc.)

**Tools by Framework:**
- TypeScript: Zod, Yup, Joi
- Python: Pydantic, Marshmallow
- Go: validator package
- Java: Bean Validation

### Business Validation (Services)
- Business rules
- Cross-field validation
- State transitions
- Authorization checks

---

## Testing Strategy

### Unit Tests (Services & Repositories)
```
Test Pyramid:
  60% - Service layer business logic
  30% - Integration tests (Service + Repository)
  10% - E2E tests (Full HTTP flow)
```

**Service Test Pattern:**
```
Given: Mock repository responses
When: Call service method
Then: Verify business logic output
```

**Repository Test Pattern:**
```
Given: Test database with fixtures
When: Call repository method
Then: Verify database state
```

### Integration Tests
```
Test: Full layer interaction
Setup: Test database
Execute: Controller → Service → Repository
Verify: Response and DB state
```

---

## Configuration Management

### Unified Config Pattern

**Principle:** Single source of truth for configuration

**Structure:**
```
Config:
  - Database (host, port, credentials)
  - Server (port, host, cors)
  - External Services (API keys, URLs)
  - Feature Flags
  - Environment (dev, staging, prod)
```

**Loading Strategy:**
1. Environment variables (highest priority)
2. Config files (.env, config.yaml)
3. Defaults (lowest priority)

**Best Practices:**
- Never hardcode secrets
- Use environment-specific configs
- Validate config on startup
- Type-safe config objects

---

## Dependency Injection

### Why?
- Testability (mock dependencies)
- Flexibility (swap implementations)
- Loose coupling

### Pattern (Constructor Injection):

**TypeScript:**
```typescript
class PostService {
  constructor(private postRepository: PostRepository) {}

  async create(data: CreatePostDTO) {
    return this.postRepository.create(data);
  }
}
```

**Python:**
```python
class PostService:
    def __init__(self, post_repository: PostRepository):
        self.post_repository = post_repository

    async def create(self, data: CreatePostDTO):
        return await self.post_repository.create(data)
```

**Go:**
```go
type PostService struct {
    postRepository PostRepository
}

func NewPostService(repo PostRepository) *PostService {
    return &PostService{postRepository: repo}
}
```

---

## API Response Standards

### Success Response
```json
{
  "success": true,
  "data": {
    "id": "123",
    "name": "Resource"
  },
  "meta": {
    "timestamp": "2025-11-01T10:30:00Z"
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": []
  }
}
```

### List Response
```json
{
  "success": true,
  "data": [],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "hasMore": true
  }
}
```

---

## File Organization

### Recommended Structure (Framework Agnostic)

```
src/
├── features/           # Feature-based organization
│   ├── posts/
│   │   ├── post.routes.ts          # Routes
│   │   ├── post.controller.ts      # Controller
│   │   ├── post.service.ts         # Business logic
│   │   ├── post.repository.ts      # Data access
│   │   ├── post.model.ts           # Domain model
│   │   ├── post.validation.ts      # Validation schemas
│   │   └── __tests__/
│   └── users/
│       └── ...
├── shared/             # Shared utilities
│   ├── middleware/
│   ├── errors/
│   ├── validation/
│   └── config/
└── server.ts           # Application entry point
```

---

## Quick Reference

### When to Use Each Layer

**Route:** HTTP endpoint definition only
**Controller:** HTTP request/response handling
**Service:** Business logic and orchestration
**Repository:** Database operations only

### Common Mistakes

❌ **DON'T:**
- Put business logic in controllers
- Make HTTP calls in services
- Put validation in repositories
- Skip error handling

✅ **DO:**
- Keep layers focused
- Use dependency injection
- Write tests for each layer
- Handle errors consistently
- Use type safety

---

## Adaptation Guide

This skill provides framework-agnostic patterns. To adapt to your stack:

1. **Map concepts to your framework:**
   - Routes → Your framework's routing mechanism
   - Controllers → Request handlers
   - Services → Business logic classes/functions
   - Repositories → Data access layer

2. **Use framework-specific features:**
   - Middleware → Framework's middleware system
   - Validation → Framework's validation library
   - DI → Framework's dependency injection (if available)

3. **Keep the principles:**
   - Layered architecture
   - Separation of concerns
   - Consistent error handling
   - Testability

---

## Example: Complete Feature Flow

**Create Post Feature (Pseudo-code)**

**1. Route:**
```
POST /api/posts
→ PostController.create
```

**2. Controller:**
```
PostController.create(request):
  data = request.body
  post = PostService.create(data)
  return Response(201, post)
```

**3. Service:**
```
PostService.create(data):
  validate(data)  # Business rules
  post = PostRepository.create(data)
  emit_event("post.created", post)
  return post
```

**4. Repository:**
```
PostRepository.create(data):
  post = database.insert("posts", data)
  return post
```

---

## When to Use This Skill

✅ Designing API architecture
✅ Structuring backend services
✅ Refactoring monolithic code
✅ Planning error handling
✅ Setting up testing strategy
✅ Implementing new features

❌ Framework-specific implementation details
❌ Database schema design
❌ Frontend integration
❌ DevOps/deployment

---

## Related Patterns

- **Repository Pattern** - Data access abstraction
- **Dependency Injection** - Loose coupling
- **DTO (Data Transfer Objects)** - Request/response shapes
- **Service Layer Pattern** - Business logic encapsulation
- **Error Handling Middleware** - Centralized error processing

---

**Remember:** These patterns work for ANY backend framework. Adapt the examples to your specific tech stack while keeping the core principles.
