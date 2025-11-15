---
description: DDD complete MCP request flow (Tool→Controller→Facade→Service→Repo→ORM→DB)
---

# DDD Architecture Complete Flow

**Purpose**: Understand complete DDD request flow

## Architecture
**Flow**: MCP Tool → mcp_controllers → Facade → Use Case → Repository → ORM → DB
**Alternative**: API(frontend) → api_controllers → Facade → Use Case → Repository → ORM → DB
**Rule**: NO legacy patterns, NO fallbacks, NO migration

## Complete Flow Steps

| Step | Layer | Action |
|------|-------|--------|
| 0 | Fix | Check `backend.log` for errors → Fix root cause |
| 1 | MCP Tool | Initiate request (tool name + params) |
| 2 | HTTP | Convert to HTTP POST `/api/v1/mcp/tools/call` |
| 3 | Auth | JWT validation with Keycloak → Extract user_id |
| 4 | Route | Extract tool name → Route to controller |
| 5 | Controller | Validate input → Get operation → Execute → Format response |
| 6 | Facade | Coordinate services → Manage transactions → Convert entities to DTOs |
| 7 | Service | Implement business logic → Create entities → Validate rules → Call repo |
| 8 | Repository | Convert entities to ORM → Add user_id → Build SQL → Manage sessions |
| 9 | ORM | Map to DB tables → Handle relationships → Manage data types |
| 10 | Database | Execute SQL → Connection pooling → Row-level security |
| 11 | Response | DB → ORM → Repo → Service → Facade → Controller → Route → HTTP → MCP |
| 12 | Rebuild | `./docker-system/docker-menu.sh` option R |

## Key Principles

| Principle | Rule |
|-----------|------|
| Multi-Tenancy | Every request includes user_id, repos filter by user_id |
| Layer Separation | Single responsibility, no skipping, dependencies flow inward |
| Dependency Injection | Controllers get facades via factory, all deps injected |
| Transactions | Facades manage boundaries, auto-rollback on exception |
| DTO Pattern | Domain entities never leave domain layer |
| Factory Pattern | ValidationFactory, OperationFactory, ResponseFactory, FacadeFactory (singleton) |

## File Structure

| Layer | Path |
|-------|------|
| Interface | `/interface/` (mcp_controllers, api_controllers) |
| Application | `/application/` (facades, services, dtos, factories) |
| Domain | `/domain/` (entities, services, value_objects, events) |
| Infrastructure | `/infrastructure/` (repositories, database, orm_models) |

## Factory Pattern Issues

| Issue | Solution |
|-------|----------|
| Controller init | Use lazy loading: `self.facade = None`, create on demand |
| TokenFacadeFactory | Use `create_token_facade` not `create_facade` |
| GitBranchFacadeFactory | Use both `create_facade` and `create_git_branch_facade` |
| Repository | Use `Factory.create(user_id)` not `create_repository` |

## Strict DDD Rules
1. NO direct DB access outside repos
2. NO business logic in controllers/routes
3. NO domain entities exposed to API
4. NO cross-layer imports
5. NO legacy patterns/fallbacks
6. ALL routes use controllers
7. ALL controllers use facades
8. ALL facades use services
9. ALL services use repos
10. ALL repos filter by user_id

**Flow Details**: $ARGUMENTS
