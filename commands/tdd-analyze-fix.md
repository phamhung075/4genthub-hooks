# TDD Analysis & Remediation Workflow

## tdd-analyze-fix:
**Description:** "Deep analysis and remediation of existing tests, code, and documentation to identify and fix root causes"

**Workflow:**
- Call differents agents to deep analysis and remediation of existing tests, code, and documentation to identify and fix root causes, change agents depend by task.

### Phase 1: Deep Test Analysis
- **Read all existing tests first** - understand current test coverage and expectations
- Analyze test quality, completeness, and relevance
- Identify gaps in test coverage
- Document test dependencies and relationships
- **Do NOT modify tests yet** - only analyze and document findings

### Phase 2: Code Context Analysis  
- **Read code related to tests** - understand current implementation
- **Read documentation related to code** - understand intended behavior
- **Read all linked code at different levels** - trace dependencies, imports, and relationships
- Map the complete system context and data flow
- Identify code architecture patterns and design decisions

### Phase 3: System-Wide Impact Assessment
- **Identify obsolete code/document/test components**
- Analyze compatibility issues between different system layers
- Document inconsistencies between tests, code, and documentation
- Map technical debt and architectural concerns
- Assess security and performance implications

### Phase 4: Architecture & Database Verification
- **Call architecture agent** to verify current architecture is correct and adapted
- **Call database agent** to verify database schema and relationships are optimal
- Assess if current architecture supports intended functionality
- Identify structural changes needed for proper implementation
- Document recommended architectural improvements

### Phase 5: Strategic Planning
- **Think through best strategy** for modifying tests vs code vs architecture
- Prioritize fixes based on:
  - Risk assessment
  - Impact on system stability
  - Dependencies and cascading effects
  - Resource requirements
- Create detailed remediation plan with phases and dependencies

### Phase 6: Compatibility Assessment
- **Identify incompatible or obsolete code sections**
- Assess what needs updating vs complete replacement
- Document breaking changes and migration requirements
- Plan backward compatibility strategy if needed

### Phase 7: Final Task Creation & Context Handoff
- **Call task planning agent** with complete analysis context
- Create comprehensive task breakdown with full context for each task:
  
  **Task Context Package for Each Task:**
  - Analysis findings and root cause identification
  - Code/test/documentation relationship mapping
  - Architecture and database assessment results
  - Compatibility issues and obsolescence findings
  - Strategic approach and priority rationale
  - Dependencies and prerequisites
  - Success criteria and validation requirements
  - Risk assessment and mitigation strategies

  **Task Categories to Create:**
  - Obsolete code removal/replacement tasks
  - Architecture update tasks  
  - Database schema change tasks
  - Test modernization tasks
  - Documentation update tasks
  - Integration and validation tasks

- **Assign task metadata:**
  - Priority levels and execution order
  - Dependencies between tasks
  - Estimated effort and complexity
  - Required agent specializations
  - Context handoff packages

### Final Deliverable: Task Plan with Context
**Complete the analysis by:**
1. Creating all tasks in the task planning system
2. Providing rich context for each task so future agents can execute independently
3. Establishing clear task dependencies and execution order
4. Documenting the analysis findings and strategic decisions
5. **Terminating the analysis workflow** - implementation will be handled by specialized agents later

**Context Handoff Success Criteria:**
- Each task has sufficient context for independent execution
- No information loss between analysis and implementation phases
- Clear success criteria and validation requirements for each task
- Strategic decisions and rationale preserved for future reference

---

## tdd-quick-analyze:
**Description:** "Quick analysis cycle for smaller code sections"

**Workflow:**
1. Read and analyze specific test/code section
2. Identify immediate issues and dependencies  
3. Assess compatibility with current system
4. Create focused remediation tasks
5. Execute fixes with proper testing
6. Document changes and update context

---

## Usage Instructions:

**For comprehensive system analysis:**
```
Use tdd-analyze-fix when you need to:
- Understand complex legacy systems
- Identify root causes of systemic issues
- Plan major refactoring or modernization
- Assess technical debt and architectural problems
```

**For focused analysis:**
```
Use tdd-quick-analyze when you need to:
- Fix specific failing tests
- Update isolated code sections
- Address targeted compatibility issues
- Make small, contained improvements
```

**Key Principles:**
- **Analysis before action** - understand completely before changing anything
- **System-wide thinking** - consider all impacts and dependencies
- **Agent collaboration** - leverage specialized agents for architecture and database decisions
- **Context preservation** - maintain full context throughout the process
- **Risk mitigation** - plan for safe, incremental changes