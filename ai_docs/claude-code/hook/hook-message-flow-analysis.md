# Hook System Message Flow Analysis

## Hook Execution Order

1. **session_start.py** - Runs when a Claude session starts
2. **user_prompt_submit.py** - Runs when user submits a prompt
3. **pre_tool_use.py** - Runs before any tool execution
4. **post_tool_use.py** - Runs after tool execution
5. **stop.py** - Runs when session ends

## Message Configuration Files

### 1. session_start_messages.yaml
- **Purpose**: Agent-specific initialization messages
- **When to use**: At session start when agent needs to be initialized
- **Contains**:
  - Agent-specific initialization messages for all 33 agents
  - Role descriptions for each agent
  - Default message template for unknown agents

### 2. session_messages.yaml
- **Purpose**: Session lifecycle messages
- **When to use**: During session state changes
- **Contains**:
  - Session start/resume/expire/end messages
  - File/folder tracking messages
  - Session data management messages

### 3. info_messages.yaml
- **Purpose**: General informational messages
- **When to use**: Throughout session for user feedback
- **Contains**:
  - Tool usage violations and available tools
  - File operation confirmations
  - Agent loading/switching messages
  - Task management messages

### 4. docs_messages.yaml
- **Purpose**: Documentation indexer messages
- **When to use**: When documentation is indexed/updated
- **Contains**:
  - Index generation messages
  - File/directory processing messages
  - Documentation update notifications

## Current Implementation Issues

### session_start.py
- **Issue**: Not loading session_start_messages.yaml
- **Missing**: ConfigurationLoader not initialized
- **Missing**: AgentMessageProvider not added to context providers

### Required Changes

1. **SessionStartHook class needs to**:
   - Initialize ConfigurationLoader with config directory
   - Add AgentMessageProvider to context providers
   - Display agent initialization message prominently

2. **Message Display Priority**:
   - Agent initialization message (FIRST - most important)
   - Session type indicator
   - Git status
   - MCP context
   - Development environment

## Correct Message Flow

### Session Start Flow
```
1. Session starts
2. Detect session type (principal/sub-agent)
3. Load session_start_messages.yaml
4. Display agent initialization message
   - For principal: master-orchestrator-agent message
   - For sub-agent: detected agent message
5. Display session context (git, MCP, etc.)
```

### User Prompt Submit Flow
```
1. User submits prompt
2. Validate prompt
3. Check for agent detection patterns
4. If agent call detected:
   - Load info_messages.yaml
   - Display agent_loaded message
5. Process prompt with context
```

### Pre-Tool Use Flow
```
1. Tool about to be used
2. Check agent permissions
3. If violation:
   - Load info_messages.yaml
   - Display role_violation message
   - Display available_tools
   - Display solution
4. If allowed, proceed
```

### Post-Tool Use Flow
```
1. Tool execution completed
2. Check if documentation updated
3. If docs updated:
   - Update index.json
   - Load docs_messages.yaml
   - Display index_update_complete message
```

## Implementation Priority

1. **HIGHEST**: Fix session_start.py to load and display agent initialization messages
2. **HIGH**: Ensure user_prompt_submit.py displays agent_loaded messages
3. **MEDIUM**: Update pre_tool_use.py to use info_messages.yaml for violations
4. **LOW**: Update post_tool_use.py to use docs_messages.yaml for index updates