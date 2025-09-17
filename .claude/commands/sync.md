================================================================================
                    PROJECT SYNCHRONIZATION PROTOCOL - DECISION TREE
================================================================================

OBJECTIVE
---------
Synchronize project documentation, architecture, and context layers to maintain consistency between codebase, git repository, and agenthub system. Ensure all documentation reflects current state and all context layers contain accurate project information.

KEY REQUIREMENTS
----------------
- Document Location: All documentation in ai_docs/ with proper subfolders
- PRD Location: ai_docs/architecture-design/PRD.md
- Architecture: ai_docs/architecture-design/Architecture_Technique.md
- Context Hierarchy: Global → Project → Branch → Task (inheritance flows downward)
- Git Integration: Project and branch names must match actual git repository
- No Duplicates: Check for existing documents before creating new ones
- Clean Updates: Update existing documents, don't create new versions

ENTRY POINT
-----------
READ PRD and Architecture
START → Call master-orchestrator-agent or documentation-agent
Or use MCP tools directly: mcp__agenthub_http__manage_context

SYNCHRONIZATION DECISION TREE
------------------------------
Start Synchronization Protocol
    ↓
Check Current Git State
    ↓
Git Info Available? → NO → Stop - Get Git Info First
    ↓ YES
Phase 1: Documentation Sync
    ↓
Documentation Updated? → NO → Stop - Create Todo List
    ↓ YES
Phase 2: Project/Branch Sync
    ↓
Names Match Git? → NO → Stop - Create Todo List
    ↓ YES
Phase 3: Context Layer Sync
    ↓
All Contexts Updated? → NO → Stop - Create Todo List
    ↓ YES
Phase 4: Verification
    ↓
All Synced? → NO → Return to Failed Phase
    ↓ YES
Complete Synchronization

ERROR FLOW:
Stop → Document Issues → Create Fix Plan → Apply Updates → Verify → Return to Failed Phase

SYNCHRONIZATION EXECUTION FLOW
===============================

PHASE 1: DOCUMENTATION SYNCHRONIZATION
---------------------------------------
IF synchronizing documentation:
    CHECK existing PRD.md:
        IF exists:
            - UPDATE with current project state
            - PRESERVE existing structure
            - ADD new features/changes
        ELSE:
            - GENERATE comprehensive PRD.md
            - INCLUDE all current features
            - SAVE to ai_docs/architecture-design/PRD.md
    
    CHECK existing Architecture_Technique.md:
        IF exists:
            - UPDATE with current architecture
            - REFLECT actual implementation
            - DOCUMENT technology stack changes
        ELSE:
            - GENERATE detailed architecture document
            - INCLUDE DDD patterns used
            - SAVE to ai_docs/architecture-design/Architecture_Technique.md
    
    IF any_error:
        STOP → CREATE todo_list → FIX → RETRY
    ELSE:
        PROCEED to Phase 2

PHASE 2: PROJECT AND BRANCH SYNCHRONIZATION
--------------------------------------------
IF synchronizing project/branch:
    GET current git info:
        - PROJECT_NAME from git repo name
        - BRANCH_NAME from current git branch
    
    CHECK agenthub project:
        - CALL mcp__agenthub_http__manage_project(
            action="list",
            user_id=user_id
          )
        - FIND project matching git repo name
        
        IF not_found:
            - CREATE project:
              mcp__agenthub_http__manage_project(
                action="create",
                name=git_repo_name,
                user_id=user_id
              )
        ELSE IF name_mismatch:
            - UPDATE project name to match git
    
    CHECK agenthub branch:
        - CALL mcp__agenthub_http__manage_git_branch(
            action="list",
            project_id=project_id,
            user_id=user_id
          )
        - FIND branch matching current git branch
        
        IF not_found:
            - CREATE branch:
              mcp__agenthub_http__manage_git_branch(
                action="create",
                project_id=project_id,
                git_branch_name=git_branch_name,
                user_id=user_id
              )
        ELSE IF name_mismatch:
            - UPDATE branch name to match git
    
    IF any_error:
        STOP → CREATE todo_list → FIX → RETRY
    ELSE:
        PROCEED to Phase 3

PHASE 3: CONTEXT LAYER SYNCHRONIZATION
---------------------------------------
IF synchronizing contexts:
    UPDATE Global Context:
        - General project guidelines
        - Cross-project standards
        - User preferences
        - System-wide configurations
        
        CALL mcp__agenthub_http__manage_context(
            action="update",
            level="global",
            context_id="global",
            user_id=user_id,
            data={
                "standards": {...},
                "preferences": {...},
                "guidelines": {...}
            }
        )
    
    UPDATE Project Context:
        - Project-specific information
        - Technology stack (from Architecture_Technique.md)
        - Team preferences
        - Project workflow
        
        CALL mcp__agenthub_http__manage_context(
            action="update",
            level="project",
            context_id=project_id,
            project_id=project_id,
            user_id=user_id,
            data={
                "technology_stack": {...},
                "team_preferences": {...},
                "project_workflow": {...},
                "local_standards": {...}
            }
        )
    
    UPDATE Branch Context:
        - Current development focus
        - Branch-specific decisions
        - Active features
        - Technical debt items
        
        CALL mcp__agenthub_http__manage_context(
            action="update",
            level="branch",
            context_id=branch_id,
            git_branch_id=branch_id,
            project_id=project_id,
            user_id=user_id,
            data={
                "current_focus": "...",
                "active_features": [...],
                "technical_decisions": {...},
                "debt_items": [...]
            }
        )
    
    IF any_error:
        STOP → CREATE todo_list → FIX → RETRY
    ELSE:
        PROCEED to Phase 4

PHASE 4: VERIFICATION AND VALIDATION
-------------------------------------
IF verifying synchronization:
    VERIFY Documentation:
        - CHECK PRD.md exists and is current
        - CHECK Architecture_Technique.md reflects actual system
        - CONFIRM both documents in correct locations
    
    VERIFY Project/Branch:
        - CONFIRM project name matches git repo
        - CONFIRM branch name matches git branch
        - CHECK both are active in system
    
    VERIFY Context Layers:
        - TEST context inheritance (global → project → branch)
        - CONFIRM all layers have data
        - CHECK data consistency across layers
    
    IF all_verified:
        - DOCUMENT sync completion
        - UPDATE sync timestamp in global context
        - REPORT success
    ELSE:
        - IDENTIFY failed components
        - RETURN to appropriate phase
        - RETRY synchronization

ERROR HANDLING PROTOCOL
========================

ON ERROR:
---------
1. STOP current synchronization phase
2. IDENTIFY specific failure point
3. CREATE todo list with error details
4. DETERMINE root cause:
   - Missing permissions?
   - Invalid data format?
   - Network/connection issue?
   - Data conflict?
5. APPLY appropriate fix
6. RETRY from failure point
7. CONTINUE with remaining phases

TODO LIST CREATION
------------------
WHEN creating todo after sync error:
1. SPECIFY which phase failed
2. INCLUDE exact error message
3. PROVIDE data that was being synced
4. SUGGEST resolution approach
5. MARK priority based on impact

SUCCESS CRITERIA
================

ALL PHASES MUST COMPLETE:
-------------------------
✓ PRD.md generated/updated with current state
✓ Architecture_Technique.md reflects actual architecture
✓ Project name matches git repository name
✓ Branch name matches current git branch
✓ Global context contains system standards
✓ Project context has technology and workflow data
✓ Branch context reflects current development
✓ All contexts show proper inheritance
✓ Verification confirms all synced correctly

OUTPUT LOCATIONS
================

Files and Directories:
----------------------
- PRD: ai_docs/architecture-design/PRD.md
- Architecture: ai_docs/architecture-design/Architecture_Technique.md
- Issues Log: ai_docs/issues/sync-issues-{date}.md
- Context Data: Stored in agenthub database (all 4 layers)

CONTEXT DATA STRUCTURE
======================

Global Context:
---------------
{
    "standards": { coding, documentation, testing },
    "preferences": { user settings, defaults },
    "guidelines": { best practices, rules },
    "sync_history": { last_sync, sync_count }
}

Project Context (Database Model):
---------------------------------
{
    "technology_stack": { frontend, backend, database },
    "team_preferences": { review process, conventions },
    "project_workflow": { phases, gates, approvals },
    "local_standards": { naming, structure, patterns },
    "project_settings": { build configs, deployment settings },
    "technical_specifications": { API specs, schemas },
    "delegation_rules": { project-specific rules }
}

Note: Additional fields like project_info, core_features go to local_standards._custom

Branch Context (Database Model):
--------------------------------
{
    "data": { general branch data },
    "branch_info": { feature name, type, status, parent branch },
    "branch_workflow": { implementation status, dependencies },
    "feature_flags": { feature toggles and configuration },
    "discovered_patterns": { patterns found during development },
    "branch_decisions": { technical decisions for this feature }
}

SYNCHRONIZATION NOTES
=====================

Best Practices:
---------------
- ALWAYS check for existing documents before creating
- PRESERVE existing content when updating
- MAINTAIN consistent formatting across documents
- USE proper markdown structure in all documents
- FOLLOW DDD patterns in architecture documentation
- ENSURE context data is JSON-serializable
- VALIDATE all data before updating contexts

Common Issues:
--------------
- Git branch name contains special characters
- Project already exists with different name
- Context update fails due to large data size
- Documentation file permissions issues
- Network timeout during context updates

Resolution Strategies:
----------------------
- Sanitize git branch names for agenthub
- Use unique identifiers to prevent duplicates
- Split large context updates into chunks
- Check file permissions before writing
- Implement retry logic for network operations

================================================================================
                                    END
================================================================================