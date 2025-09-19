================================================================================
                    MCP TOOL TESTING PROTOCOL - DECISION TREE
================================================================================

OBJECTIVE
---------
Continue fixing issues by having a coder agent correct code problems found during testing. Code corrections must respect tool descriptions and Domain-Driven Design (DDD) architectures.
The system follows strict Domain Driven Design layering with complete separation of concerns
All routes must follow this pattern: 
MCP Tool(mcp) → mcp_controllers → Facade → Use Case → Repository → ORM → Database
Route API(frontend) → api_controllers → Facade → Use Case → Repository → ORM → Database

KEY REQUIREMENTS
----------------
- View logs/backend.log for details (tail 200 lines each time)
- Development Environment: Use Keycloak for authentication and local PostgreSQL docker for database
- Authentication: Keycloak is the source of truth for user authentication
- Trust Model: Both frontend and backend trust the same Keycloak user identity
- Rebuild Process: Use docker-menu.sh option R for rebuild after each fix
- Database Schema: ORM model is the source of truth - update database tables to match ORM model definition
- Code Standards: No backward compatibility, no legacy code - maintain clean code, no migration mechanisms are allowed
- No hardcord 
- no change .env value

ENTRY POINT
-----------
START → Call test-orchestrator-agent

TESTING DECISION TREE
---------------------
If logs/backend.log shows no issues, find issues using the following testing flow:

Start Testing Protocol
    ↓
Initialize Test Agent
    ↓
Test Project Management
    ↓
Project Tests Pass? → NO → Stop - Create Todo List
    ↓ YES
Test Git Branch Management
    ↓
Branch Tests Pass? → NO → Stop - Create Todo List
    ↓ YES
Test Task Management - Branch 1
    ↓
Task Tests Pass? → NO → Stop - Create Todo List
    ↓ YES
Test Task Management - Branch 2
    ↓
Branch 2 Tests Pass? → NO → Stop - Create Todo List
    ↓ YES
Test Subtask Management
    ↓
Subtask Tests Pass? → NO → Stop - Create Todo List
    ↓ YES
Test Task Completion
    ↓
Completion Tests Pass? → NO → Stop - Create Todo List
    ↓ YES
Test Context Management
    ↓
Context Tests Pass? → NO → Stop - Create Todo List
    ↓ YES
Document All Issues
    ↓
Create Fix Prompts
    ↓
Update All Context Layers
    ↓
Complete Testing Protocol

ERROR FLOW:
Stop → Document Issues in MD → Create DDD-Compliant Fixes → Restart Backend → Verify in database(DATABASE_TYPE) → Return to Failed Test

TEST EXECUTION FLOW
===================

PHASE 1: PROJECT MANAGEMENT TESTS
----------------------------------
IF testing project management:
    - CREATE 2 projects
    - TEST get, list, update, health_check operations
    - SET project context
    
    IF any_error:
        STOP → CREATE todo_list → FIX → RESTART → RETEST
    ELSE:
        PROCEED to Phase 2

PHASE 2: GIT BRANCH MANAGEMENT TESTS
-------------------------------------
IF testing git branches:
    - CREATE 2 branches
    - TEST get, list, update, agent_assignment operations
    - SET branch context
    
    IF any_error:
        STOP → CREATE todo_list → FIX → RESTART → RETEST
    ELSE:
        PROCEED to Phase 3

PHASE 3: TASK MANAGEMENT TESTS
------------------------------
IF testing task management:
    BRANCH 1:
        - CREATE 5 tasks
        - TEST update, get, list, search, next operations
        - ADD random dependencies
        - ASSIGN agents
    
    BRANCH 2:
        - CREATE 2 tasks
        - TEST same operations as Branch 1
    
    IF any_error:
        STOP → CREATE todo_list → FIX → RESTART → RETEST
    ELSE:
        PROCEED to Phase 4

PHASE 4: SUBTASK MANAGEMENT TESTS
----------------------------------
IF testing subtasks:
    FOR each task in Branch 1:
        - CREATE 4 subtasks
        - FOLLOW TDD steps
        - TEST update, list, get, complete operations
    
    IF any_error:
        STOP → CREATE todo_list → FIX → RESTART → RETEST
    ELSE:
        PROCEED to Phase 5

PHASE 5: TASK COMPLETION TESTS
------------------------------
IF testing task completion:
    - SELECT 1 task from Branch 1
    - COMPLETE with full summary
    - VERIFY completion status
    
    IF any_error:
        STOP → CREATE todo_list → FIX → RESTART → RETEST
    ELSE:
        PROCEED to Phase 6

PHASE 6: CONTEXT MANAGEMENT TESTS
----------------------------------
IF testing context management:
    - VERIFY global context
    - VERIFY project context
    - VERIFY branch context  
    - VERIFY task context
    - TEST inheritance flow
    
    IF any_error:
        STOP → CREATE todo_list → FIX → RESTART → RETEST
    ELSE:
        PROCEED to Phase 7

PHASE 7: DOCUMENTATION & FIX GENERATION
----------------------------------------
IF all tests complete OR errors encountered:
    - DOCUMENT all issues in MD format
    - SAVE to ai_docs/issues/
    - CREATE detailed fix prompts
    - UPDATE all context layers

ERROR HANDLING LOOP
===================

ON ERROR:
---------
1. STOP current test immediately
2. CREATE todo list with specific error details
3. WRITE issue to ai_docs/issues/mcp-testing-issues-{date}.md
4. GENERATE fix prompt with DDD compliance requirements
5. APPLY fixes following Domain-Driven Design patterns
6. RESTART backend: docker-compose down && docker-compose up
7. VERIFY changes in Supabase dashboard
8. RETURN to failed test and continue from that point

TODO LIST REMAKE PROTOCOL
==========================

WHEN creating todo list after error:
------------------------------------
1. IDENTIFY specific failing operation
2. ANALYZE error with DDD compliance lens
3. CREATE fix prompt with implementation details
4. RESTART backend after applying fixes
5. VERIFY database changes in Supabase
6. RETEST from point of failure
7. CONTINUE with remaining test phases

SUCCESS CRITERIA
================

ALL PHASES MUST PASS:
---------------------
✓ Project Management (2 projects + operations)
✓ Git Branch Management (2 branches + operations) 
✓ Task Management (5+2 tasks + operations)
✓ Subtask Management (4 per task + operations)
✓ Task Completion (1 complete task)
✓ Context Management (all 4 layers)
✓ Issue Documentation (complete MD file)
✓ Context Updates (all layers updated)

OUTPUT LOCATIONS
================

Files and Directories:
----------------------
- Issues: ai_docs/issues/mcp-testing-issues-{date}.md
- Fix Prompts: Same MD file, section "Fix Prompts"
- Context Updates: All 4 context layers (global, project, branch, task)

ARCHITECTURE NOTES
==================

DDD Compliance:
---------------
- All fixes must follow Domain-Driven Design principles
- Clean Architecture: No backward compatibility or legacy code
- Database First: ORM model defines the database schema
- Authentication Flow: Keycloak → Frontend/Backend trust chain
- Development Workflow: Fix → Rebuild → Verify → Test → Continue

================================================================================
                                    END
================================================================================