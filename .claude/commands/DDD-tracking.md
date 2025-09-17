DDD Architecture Complete MCP Request Flow

System Architecture Overview
The system follows strict Domain Driven Design layering with complete separation of concerns
All routes must follow this pattern: 
MCP Tool(mcp) → mcp_controllers → Facade → Use Case → Repository → ORM → Database
Route API(frontend) → api_controllers → Facade → Use Case → Repository → ORM → Database
No legacy patterns or fallback or migration mechanisms are allowed

Complete Detailed Request Flow

Step 0 Fix error
see agenthub_main/backend.log for fix error appear on log

Step 1 MCP Tool Call
The MCP tool initiates the request from Claude or other MCP clients
Tool name mcp__agenthub_http__manage_task
Parameters passed action create title New Task git_branch_id branch123
Tool sends HTTP POST request to backend server

Step 2 HTTP Transport
MCP tool call converts to HTTP request
Endpoint POST /api/v1/mcp/tools/call
Headers Authorization Bearer JWT_TOKEN Content Type application json
Request body contains tool name and arguments
Body structure name mcp__agenthub_http__manage_task arguments action create title New Task git_branch_id branch123

Step 3 Authentication Middleware
FastAPI middleware intercepts request before reaching route handler
<!--Extracts JWT token from Authorization header-->
Validates token with Keycloak if AUTH_ENABLED true
Decodes token to extract user identity user_id email roles
Creates User object from token claims
Injects authenticated user into request context via Depends get_current_user
Falls back to default user if AUTH_ENABLED false

Step 4 Route Handler
Route function receives authenticated request
Located in /src/fastmcp/server/routes/mcp_tool_routes.py
Function signature async def call_tool request ToolCallRequest current_user User db Session
Extracts tool name from request
Routes to appropriate controller based on tool name
Passes user_id and database session to controller

Step 5 Controller Layer
Controller receives request from route handler
Located in /src/fastmcp/task_management/interface/mcp_controllers/
Example TaskMCPController manages all task related MCP operations
Controller responsibilities
Validates input parameters using ValidationFactory
Determines operation type from action parameter
Gets appropriate operation handler from OperationFactory
Executes operation with user context
Formats response using ResponseFactory
Returns MCP formatted result

Step 6 Facade Layer
Controller gets facade via FacadeService which uses FacadeFactory
Located in /src/fastmcp/task_management/application/facades/
Example TaskApplicationFacade orchestrates task operations
Facade creation flow
Controller calls FacadeService.get_instance to get singleton service
FacadeService calls appropriate FacadeFactory.get_instance for singleton factory
Factory creates facade with proper dependency injection
Factory uses RepositoryProviderService to get repositories
RepositoryProviderService calls RepositoryFactory.create with user_id
Repositories are injected into services then into facades
Facade responsibilities
Gets created with user_id project_id git_branch_id context
Coordinates multiple services for complex operations
Manages database transactions
Calls domain services for business logic
Calls infrastructure services for technical operations
Converts domain entities to DTOs
Returns structured response

Step 7 Service Layer
Facade delegates business logic to services
Located in /src/fastmcp/task_management/domain/services/
Example TaskService implements task business rules
Service responsibilities
Implements core business logic
Creates domain entities
Validates business rules
Applies domain constraints
Calls repository for persistence
Does not know about HTTP or database details

Step 8 Repository Layer
Service calls repository for data persistence
Located in /src/fastmcp/task_management/infrastructure/repositories/
Example SqlAlchemyTaskRepository handles task persistence
Repository responsibilities
Implements repository interface from domain layer
Converts domain entities to ORM models
Adds user_id for multi tenancy filtering
Builds SQL queries using SQLAlchemy
Manages database sessions
Handles transactions
Returns domain entities not ORM models

Step 9 ORM Layer
Repository uses SQLAlchemy ORM for database operations
Located in /src/fastmcp/task_management/infrastructure/orm_models/
Example TaskORM maps to tasks table
ORM responsibilities
Defines database table structure
Maps Python objects to database rows
Handles relationships between tables
Manages data types and constraints
Provides query building capabilities

Step 10 Database Layer
ORM executes SQL queries on database
PostgreSQL in production SQLite in development
Example query INSERT INTO tasks id title user_id status created_at VALUES uuid New Task user123 pending 2025 09 05
Database operations
Connection pooling 50 base plus 100 overflow
Transaction management with auto commit or rollback
Row level security via user_id filtering
Query optimization and indexing

Step 11 Response Flow Back
Database returns result to ORM
ORM returns model to Repository
Repository converts ORM model to domain entity
Service returns domain entity to Facade
Facade converts entity to DTO
Controller formats DTO as MCP response
Route returns HTTP response to MCP tool
MCP tool returns result to user

Detailed Example Task Creation Flow

1 MCP Tool Call
mcp__agenthub_http__manage_task action create title Implement login feature git_branch_id abc123

2 HTTP Request
POST /api/v1/mcp/tools/call
Authorization Bearer [REDACTED]
Body name mcp__agenthub_http__manage_task arguments action create title Implement login feature git_branch_id abc123

3 Authentication
Token validated with Keycloak
User extracted id user789 email dev at example com

4 Route Handler
call_tool function in mcp_tool_routes.py
Receives ToolCallRequest User Session
Routes to task_controller

5 TaskMCPController
manage_task method called
ValidationFactory validates required fields
OperationFactory returns CreateTaskHandler
Handler executes with user context

6 TaskApplicationFacade
Created with user_id user789 git_branch_id abc123
Calls task_service.create_task
Calls context_service.create_context
Calls workflow_enhancer.enhance
Returns TaskDTO

7 TaskService
Creates Task entity with business rules
Sets status to PENDING
Validates title not empty
Validates user has permission
Calls repository.save

8 SqlAlchemyTaskRepository
Converts Task entity to TaskORM
Sets user_id to user789 for filtering
Begins database transaction
Executes session.add orm_task
Commits transaction
Returns saved Task entity

9 TaskORM
Maps to tasks table
Columns id title description status user_id created_at updated_at
Relationships to subtasks context dependencies

10 PostgreSQL Database
Executes INSERT INTO tasks
Assigns auto generated UUID
Sets created_at to current timestamp
Returns inserted row

11 Response Chain
Database returns row to ORM
ORM returns TaskORM to Repository
Repository returns Task entity to Service
Service returns Task to Facade
Facade returns TaskDTO to Controller
Controller returns MCP response
Route returns HTTP 200 with result

12 Rebuild server by use menu sh option R

Key Architecture Principles

Multi Tenancy
Every request includes user_id
Repositories filter all queries by user_id
No cross user data access possible
Row level security enforced

Layer Separation
Each layer has single responsibility
No layer skipping allowed
Dependencies only flow inward
Domain layer knows nothing about infrastructure

Dependency Injection
Controllers get facades via factory
Facades get services via injection
Services get repositories via injection
All dependencies injected not created

Transaction Management
Facades manage transaction boundaries
Auto rollback on any exception
Explicit commit only on success
Session per request pattern

DTO Pattern
Domain entities never leave domain layer
DTOs used for API communication
Mapping happens at facade layer
Prevents leaking domain complexity

Factory Pattern
ValidationFactory creates validators
OperationFactory creates handlers
ResponseFactory creates responses
FacadeFactory creates facades with context
Factory Singleton Pattern
All facade factories implement singleton pattern with get_instance method
Factories cache created instances for reuse
Factories use create_facade method to create instances
Repository factories use create classmethod not create_repository
RepositoryProviderService abstracts repository creation from facades

File Structure Organization

Interface Layer
/src/fastmcp/task_management/interface/
mcp_controllers contains MCP tool controllers
api_controllers contains REST API controllers
Each controller handles one domain area

Application Layer
/src/fastmcp/task_management/application/
facades contains application facades
services contains application services
dtos contains data transfer objects
factories contains facade factories

Domain Layer
/src/fastmcp/task_management/domain/
entities contains domain entities
services contains domain services
value_objects contains value objects
events contains domain events

Infrastructure Layer
/src/fastmcp/task_management/infrastructure/
repositories contains repository implementations
database contains database configuration
orm_models contains SQLAlchemy models

Testing Strategy

Unit Tests
Test each layer in isolation
Mock all dependencies
Focus on business logic
No database connections

Integration Tests
Test layer interactions
Use test database
Verify complete flow
Test transaction rollback

End to End Tests
Test from MCP tool to database
Include authentication
Verify multi tenancy
Check response format

Common Issues and Solutions

Authentication Failures
Check Keycloak is running
Verify JWT token not expired
Ensure realm configured correctly
Check client credentials

Database Connection Issues
Verify PostgreSQL running
Check connection string
Confirm user permissions
Monitor connection pool

Multi Tenancy Issues
Ensure user_id passed to repository
Check repository base class
Verify filtering applied
Test with multiple users

Performance Issues
Monitor slow queries
Check N plus 1 queries
Review connection pool size
Add database indexes

Factory Pattern Issues
Controller Initialization Errors
Controllers should not create facades at init time
Use lazy loading pattern self.facade = None
Create facade on demand in methods with user context
Token Facade Factory Issues  
FacadeService must call correct factory method
TokenFacadeFactory uses create_token_facade not create_facade
GitBranchFacadeFactory uses create_facade and create_git_branch_facade
Repository Factory Issues
ProjectRepositoryFactory.create not create_repository
GitBranchRepositoryFactory.create not create_repository
RepositoryProviderService handles repository creation abstraction
Always pass user_id to repository factories for authentication

Strict DDD Rules

1 NO direct database access outside repositories
2 NO business logic in controllers or routes
3 NO domain entities exposed to API
4 NO cross layer imports
5 NO legacy patterns or fallbacks
6 ALL routes must use controllers
7 ALL controllers must use facades
8 ALL facades must use services
9 ALL services must use repositories
10 ALL repositories must filter by user_id

Conclusion
This architecture ensures clear separation maintainability security scalability testability
Every request follows exact same pattern from MCP tool call through all layers to database and back
No shortcuts or exceptions allowed to maintain system integrity