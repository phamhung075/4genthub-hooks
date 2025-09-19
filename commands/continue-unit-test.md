Unit Test Creation Following DDD Patterns

System Architecture Overview
The system follows strict Domain Driven Design layering with complete separation of concerns
All routes must follow this pattern
MCP Tool(mcp) → mcp_controllers → Facade → Use Case → Repository → ORM → Database
Route API(frontend) → api_controllers → Facade → Use Case → Repository → ORM → Database
No legacy patterns or fallback or migration mechanisms are allowed

Architecture Context Review

Step 0a Review Architecture Documentation
Read ai_docs/architecture-design/Architecture_Technique.md for technical architecture
Understand Domain Layer with rich entities value objects and business logic
Review Application Layer with use cases facades DTOs and event handlers
Check Infrastructure Layer with SQLite repositories caching database management
Study Interface Layer with MCP controllers and tool registration
Review Frontend Layer with React TypeScript Tailwind CSS application

Step 0b Review Product Requirements
Read ai_docs/architecture-design/PRD.md for product context
Understand 60 plus specialized AI agents across 15 categories
Review 4 tier context hierarchy Global Project Branch Task
Check core features agent orchestration context management
Study enterprise features multi tenant secure authentication audit trails

Step 0c Fix Errors First with Root Cause Analysis
Check agenthub_main/backend.log for errors appearing in log
Analyze error context not just error message
Identify root cause not just symptoms
Match error to project architecture context
Trace error through complete request flow
Understand why error occurs in this specific context
Fix root cause at appropriate layer
Verify fix resolves all related symptoms
Test fix doesn't break other components
Document root cause and solution pattern

Step 0d Check Coverage
Run coverage report to identify untested code
Focus on critical business logic first
Prioritize domain and application layers
Review agenthub_main/src/tests/ for existing tests

Step 1 Domain Layer Tests
Located in /src/tests/unit/task_management/domain/
Test domain entities without external dependencies
Test business rules and invariants
Test value objects and domain events
Mock all infrastructure concerns
Example TaskEntity tests validate business rules
Test entity creation validation state transitions

Step 2 Application Layer Tests
Located in /src/tests/unit/task_management/application/
Test facades with mocked services
Test application services with mocked repositories
Test DTOs and mapping logic
Test transaction boundaries
Example TaskApplicationFacade tests orchestration
Mock all domain services and infrastructure

Step 3 Infrastructure Layer Tests
Located in /src/tests/unit/task_management/infrastructure/
Test repository implementations with test database
Test ORM model mappings
Test database queries and filters
Test multi tenancy user_id filtering
Example SqlAlchemyTaskRepository tests persistence
Use in memory SQLite for isolation

Step 4 Interface Layer Tests
Located in /src/tests/unit/task_management/interface/
Test MCP controllers with mocked facades
Test API controllers with mocked facades
Test request validation and response formatting
Test authentication and authorization
Example TaskMCPController tests MCP operations
Mock facade layer completely

Current Test Organization Status

Domain Organization
All tests organized by domain task_management connection_management auth
Each domain has complete test coverage structure
No cross domain test dependencies

Layer Compliance
Tests follow 4 layer DDD structure strictly
Domain Application Infrastructure Interface
Each layer tested in isolation
Dependencies always mocked

Clean Structure
Eliminated non domain test directories
No server tools validation architecture directories
Only domain specific test organization
Proper separation of concerns

Documentation Updated
TEST CHANGELOG.md tracks all test changes
Comprehensive breakdown of test coverage
Clear test organization guidelines

Test Creation Guidelines

Unit Test Requirements
Each test file matches source file structure
Test file naming test_ClassName.py
Test class naming TestClassName
Test method naming test_method_name_scenario_expected

Mock Strategy
Domain tests mock nothing pure business logic
Application tests mock repositories and services
Infrastructure tests use test database
Interface tests mock facades and services

Test Data Patterns
Use factory pattern for test data creation
Create fixtures for common test scenarios
Use builders for complex entity construction
Maintain test data isolation

Assertion Patterns
Test behavior not implementation
Assert on public interface only
Verify state changes correctly
Check error conditions explicitly

Coverage Requirements
Minimum 80 percent coverage per file
100 percent coverage for domain logic
Critical paths must have full coverage
Edge cases and error paths tested

Test Execution Flow

Step 1 Identify Untested Code
Run pytest cov to generate coverage report
Review coverage gaps in critical areas
Prioritize based on business importance
Create test plan for missing coverage

Step 2 Create Test Structure
Create test file in correct location
Import necessary test utilities
Setup test fixtures and mocks
Define test class structure

Step 3 Write Test Cases
Test happy path scenarios first
Add edge case tests
Test error conditions
Test boundary values

Step 4 Verify Test Quality
Run tests in isolation
Check test independence
Verify mock usage correct
Ensure assertions meaningful

Step 5 Update Documentation
Update TEST CHANGELOG.md
Document test patterns used
Note any special test considerations
Track coverage improvements

Error Analysis Decision Framework

When Error Detected
Read complete error traceback not just error line
Identify which layer threw error Domain Application Infrastructure Interface
Check if error is symptom of deeper issue
Review recent changes that could cause error
Understand expected behavior vs actual behavior

Root Cause Analysis Process
Trace request flow from entry point to error
Check each layer transformation and validation
Identify where data becomes invalid or missing
Review business rules being violated
Check if dependencies properly injected
Verify multi tenancy context preserved
Confirm transaction boundaries correct

Context Matching
Match error to DDD architecture pattern
Identify if error violates architecture principles
Check if error indicates missing abstraction
Review if error shows layer responsibility issue
Confirm error handling at correct layer
Verify error not masking deeper problem

Fix Decision Tree
IF error in Domain Layer
   Fix business logic or validation rules
   Update domain services if needed
   Ensure entities maintain invariants
ELIF error in Application Layer
   Fix facade orchestration logic
   Correct service coordination
   Update DTO mappings
ELIF error in Infrastructure Layer
   Fix repository implementation
   Correct database queries
   Update ORM mappings
ELIF error in Interface Layer
   Fix controller validation
   Correct request handling
   Update response formatting
ELSE
   Trace through complete flow
   Identify layer boundary issue
   Fix at appropriate abstraction level

Verification Strategy
Test fix resolves original error
Verify no new errors introduced
Check all related features still work
Confirm fix follows DDD patterns
Validate fix maintains layer separation
Ensure fix preserves multi tenancy
Document fix pattern for future reference

Common Root Causes Not Symptoms

Symptom Missing user_id in query
Root Cause Repository not extending BaseRepository
Fix Ensure repository inherits filtering behavior

Symptom Facade not found error
Root Cause Factory not using singleton pattern
Fix Implement get_instance method correctly

Symptom Context not saving
Root Cause Wrong hierarchy level specified
Fix Match context level to entity type

Symptom Token validation failing
Root Cause Keycloak configuration mismatch
Fix Align backend and Keycloak settings

Symptom Transaction rollback unexpected
Root Cause Exception handling at wrong layer
Fix Move transaction management to facade

Common Test Patterns

Repository Test Pattern
Create in memory database
Setup test data
Execute repository method
Verify database state
Cleanup test data

Facade Test Pattern
Mock all dependencies
Setup expected behavior
Call facade method
Verify orchestration correct
Check response format

Controller Test Pattern
Mock facade layer
Create request object
Call controller method
Verify response structure
Check error handling

Service Test Pattern
Mock repository layer
Setup domain entities
Execute business logic
Verify state changes
Check business rules

Factory Pattern Issues
Test facade creation separately
Mock factory dependencies
Verify singleton behavior
Test context injection

Key Testing Principles

Isolation
Each test runs independently
No shared state between tests
Test database reset each test
Mocks reset between tests

Repeatability
Tests produce same results
No time dependent logic
No external dependencies
Deterministic test data

Clarity
Test names describe scenario
Clear arrange act assert structure
Meaningful assertion messages
Self documenting test code

Performance
Unit tests run under 1 second
Integration tests under 5 seconds
Mock expensive operations
Use test doubles effectively

Maintainability
Tests follow production patterns
Reusable test utilities
Clear test organization
Regular test refactoring

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

Action Required
Review architecture documentation first
Check backend.log for runtime errors
Identify code without unit test coverage
Implement comprehensive test suites
Follow established DDD patterns
Maintain 4 layer test structure
Update TEST CHANGELOG.md with changes

Conclusion
Tests ensure system reliability maintainability correctness scalability
Every component tested according to its layer responsibilities
No shortcuts or mixed concerns allowed in test organization
Architecture documentation provides complete context for test creation