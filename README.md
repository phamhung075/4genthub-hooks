# 🚀 4genthub-hooks

> **Intelligent Claude Code Hooks Client for 4agenthub MCP Server**
>
> A sophisticated hooks implementation that transforms Claude Code into an enterprise-grade AI agent orchestration system powered by the 4agenthub MCP server.

## 🌟 Overview

4genthub-hooks is a comprehensive **client-side implementation** that seamlessly integrates Claude Code with the [4agenthub MCP Server](http://localhost:8000) to create a complete enterprise AI orchestration platform:

- 🤖 **31+ Specialized AI Agents** - From coding to architecture, testing to documentation
- 📊 **Real-time Task Management** - Visual status tracking and progress monitoring
- 🔄 **Intelligent Session Management** - Automatic agent loading and context preservation
- 🎯 **Smart Tool Enforcement** - Dynamic permissions based on agent roles
- 📈 **Enterprise Workflow Orchestration** - Professional task delegation and coordination

## 🔗 How It Works Together

### The Complete System Architecture

**4agenthub** (MCP Server) + **4genthub-hooks** (Claude Code Client) = Enterprise AI Orchestration Platform

#### 🖥️ 4agenthub MCP Server (`http://localhost:8000`)
The **backend orchestration engine** that provides:
- **Agent Management** - 31+ specialized AI agents with distinct capabilities
- **Task Persistence** - Full context storage and retrieval across sessions
- **Project Organization** - Hierarchical structure (Global → Project → Branch → Task)
- **Secure API** - JWT authentication and enterprise-grade security
- **Real-time Coordination** - Multi-agent workflow management
- **Audit Trail** - Complete transparency and compliance tracking

#### 🔌 4genthub-hooks (Claude Code Client)
The **frontend integration layer** that provides:
- **Claude Code Integration** - Seamless hooks into Claude's workflow
- **Intelligent Routing** - Automatic agent selection based on request type
- **Dynamic Tool Enforcement** - Role-based permission system
- **Status Line Updates** - Real-time progress visualization
- **Session Management** - Context preservation and agent state
- **MCP Communication** - Efficient client-server interaction

#### 🚀 Together They Enable:
- **Claude Code** becomes an intelligent orchestrator instead of a single AI
- **Work Tracking** through persistent MCP tasks with full context
- **Parallel Execution** with multiple specialized agents working simultaneously
- **Enterprise Transparency** with complete audit trails and progress monitoring
- **Professional Workflows** with proper task delegation and quality assurance

## 🏗️ Technical Architecture

### Request Flow: Claude Code → Hooks → MCP Server → Specialized Agents

```
┌─────────────────────────────────────────────┐
│             Claude Code UI                  │
│          (User Interaction)                 │
└─────────────────┬───────────────────────────┘
                  │ User Request
                  ▼
┌─────────────────────────────────────────────┐
│        4genthub-hooks (CLIENT)              │
│  ┌─────────────────────────────────────┐    │
│  │  Session Hooks (Python)             │    │
│  │  • Auto-load master-orchestrator    │    │
│  │  • Analyze request complexity       │    │
│  │  • Route to appropriate agent       │    │
│  │  • Update status line in real-time  │    │
│  │  • Enforce tool permissions         │    │
│  └─────────────────────────────────────┘    │
└─────────────────┬───────────────────────────┘
                  │ MCP Protocol (HTTP + JWT)
                  ▼
┌─────────────────────────────────────────────┐
│       4agenthub MCP Server (BACKEND)        │
│         http://localhost:8000               │
│  ┌─────────────────────────────────────┐    │
│  │  Enterprise Orchestration Engine    │    │
│  │  • 31+ Specialized Agents           │    │
│  │  • Task & Subtask Management        │    │
│  │  │  • Project Organization          │    │
│  │  • Context Persistence Engine       │    │
│  │  • JWT Authentication & Security    │    │
│  └─────────────────────────────────────┘    │
└─────────────────┬───────────────────────────┘
                  │ Agent Coordination
                  ▼
┌─────────────────────────────────────────────┐
│          Specialized Agent Execution        │
│  ┌──────────┬──────────┬─────────────────┐  │
│  │ Coding   │ Testing  │ Documentation  │  │
│  │ Agent    │ Agent    │ Agent          │  │
│  └──────────┴──────────┴─────────────────┘  │
│  ┌──────────┬──────────┬─────────────────┐  │
│  │ Debug    │ Security │ Architecture   │  │
│  │ Agent    │ Agent    │ Agent          │  │
│  └──────────┴──────────┴─────────────────┘  │
│              [+ 25 more agents]             │
└─────────────────────────────────────────────┘
```

### Data Flow:
1. **User** submits request via Claude Code
2. **4genthub-hooks** intercepts and analyzes request
3. **Hooks** create MCP task with full context on **4agenthub server**
4. **Master orchestrator** delegates to appropriate specialized agent
5. **Specialized agent** executes work and reports back
6. **Results** flow back through MCP to Claude Code UI

## 💎 Value Proposition

### Why Use 4agenthub + 4genthub-hooks?

#### 🏢 **Enterprise-Grade AI Orchestration**
Transform Claude Code from a single AI assistant into a **coordinated team of 31+ specialized agents** with:
- **Persistent Memory**: All work tracked and stored across sessions
- **Professional Workflows**: Task delegation, progress tracking, and quality assurance
- **Audit Trails**: Complete transparency for compliance and team coordination
- **Parallel Execution**: Multiple agents working simultaneously on different aspects

#### 🎯 **Intelligent Work Distribution**
- **Auto-routing**: Requests automatically routed to the most suitable specialist
- **Context Preservation**: Full project context maintained across all agents
- **Quality Assurance**: Built-in review processes and error handling
- **Scalable Architecture**: Handle complex, multi-phase projects efficiently

#### 📊 **Real-Time Visibility**
- **Status Dashboard**: Live progress tracking in Claude Code status line
- **Task Management**: Full MCP task hierarchy with subtasks and dependencies
- **Performance Monitoring**: Response times, completion rates, and bottlenecks
- **Team Coordination**: Multiple developers can see project status and progress

#### 🔒 **Enterprise Security & Compliance**
- **JWT Authentication**: Secure token-based access control
- **Role-Based Permissions**: Dynamic tool restrictions based on agent roles
- **Activity Logging**: Complete audit trail of all actions and decisions
- **Data Isolation**: User-specific contexts and secure data handling

## 🚀 Quick Start

### Prerequisites

**Two-Component Setup Required:**

1. **4agenthub MCP Server** (Backend)
   - Enterprise orchestration engine
   - Account at [https://www.4genthub.com](https://www.4genthub.com)

2. **4genthub-hooks** (Frontend Client)
   - Claude Code integration layer
   - Python 3.12+ required
   - This repository

3. **Claude Code** (latest version)

### Installation Steps

#### Step 1: Setup 4agenthub MCP Server (Backend)
```bash
# 1. Create 4agenthub account and get JWT token
# Visit: https://www.4genthub.com
# → Create account → Generate API token

# 2. Verify MCP server is running
curl http://localhost:8000/mcp/health
# Should return: {"status": "healthy", "server": "4agenthub"}
```

#### Step 2: Setup 4genthub-hooks Client (Frontend)
```bash
# 1. Clone this repository (client implementation)
git clone https://github.com/yourusername/4genthub-hooks.git
cd 4genthub-hooks

# 2. Configure MCP connection with your JWT token
nano .mcp.json
# Replace Bearer token with your 4agenthub JWT from Step 1

# 3. Test connection to 4agenthub server
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:8000/mcp/health
```

#### Step 3: Launch Integrated System
```bash
# Open in Claude Code (hooks will auto-activate)
claude-code .

# System will automatically:
# ✅ Connect to 4agenthub MCP server
# ✅ Load master-orchestrator-agent
# ✅ Enable real-time status tracking
# ✅ Activate all 31+ specialized agents
```

### Verification

After setup, you should see:
```
🎯 master-orchestrator | 🔄 Ready for requests [0▶ 0⏸ 0⚠] | 📊 Branch: main | ⚡ Fast
```

**Test the integration:**
```
User: "Create a simple hello world function"
Expected: Auto-delegation to coding-agent with MCP task tracking
```

## ⚙️ Configuration

### MCP Server Configuration (`.mcp.json`)

The project connects to multiple MCP servers:

- **agenthub_http** - Main 4agenthub orchestration server
- **sequential-thinking** - Chain-of-thought reasoning
- **shadcn-ui-server** - UI component management
- **browsermcp** - Browser automation capabilities

### Hooks Configuration (`.claude/settings.json`)

The hooks system includes:

| Hook | Purpose |
|------|---------|
| **SessionStart** | Initializes agent context and loads capabilities |
| **UserPromptSubmit** | Analyzes requests and determines agent routing |
| **PreToolUse** | Validates tool permissions and tracks usage |
| **PostToolUse** | Updates task progress and handles results |
| **Notification** | Sends alerts for important events |
| **Stop** | Cleanup and context preservation |
| **SubagentStop** | Handles sub-agent completion |
| **PreCompact** | Optimizes context before compression |

## 🤖 Available Agents

### Development & Coding
- `coding-agent` - Implementation and feature development
- `debugger-agent` - Bug fixing and troubleshooting
- `code-reviewer-agent` - Code quality and review
- `prototyping-agent` - Rapid prototyping and POCs

### Testing & QA
- `test-orchestrator-agent` - Comprehensive test management
- `uat-coordinator-agent` - User acceptance testing
- `performance-load-tester-agent` - Performance and load testing

### Architecture & Design
- `system-architect-agent` - System design and architecture
- `design-system-agent` - Design system and UI patterns
- `ui-specialist-agent` - UI/UX design and frontend
- `core-concept-agent` - Core concepts and fundamentals

### [+ 20 more specialized agents...]

## 📊 Status Line Features

The intelligent status line provides real-time visibility:

```
🎯 master-orchestrator | 🔄 Implementing auth system [2▶ 3⏸ 1⚠] | 📊 Branch: feature/auth | ⚡ Fast
```

- **Current Agent** - Shows active agent role
- **Active Task** - Current work in progress
- **Task Counts** - `[in-progress▶ pending⏸ blocked⚠]`
- **Branch Context** - Active git branch
- **Performance** - Response time indicators

## 🔧 Key Features

### 1. Automatic Agent Loading
```python
# Automatically loads master-orchestrator on session start
# No manual initialization required
```

### 2. Dynamic Tool Permissions
```python
# Each agent has specific tool access
# Master Orchestrator: Task, Read, MCP management tools
# Coding Agent: Read, Write, Edit, Bash, Grep
# Documentation Agent: Read, Write, Edit, WebFetch
```

### 3. Intelligent Task Routing
```python
# Analyzes user requests and routes to appropriate agents
# Complex tasks → Create MCP task → Delegate to specialist
# Simple tasks → Handle directly (< 1% of cases)
```

### 4. Context Persistence
```python
# All work tracked in MCP tasks
# Context preserved across sessions
# Full audit trail and history
```

## 📝 Usage Examples with MCP Flow

### Starting a New Feature
```
User: "Implement user authentication with JWT"

🔄 4genthub-hooks Flow:
1. Session hook auto-loads master-orchestrator-agent
2. Request analysis → Complex task detected
3. Creates MCP task on 4agenthub server:
   POST /api/v2/tasks {
     title: "Implement JWT authentication",
     assignees: "coding-agent",
     details: "Full requirements and context..."
   }
4. Delegates to coding-agent with task_id only
5. Status line updates: "🔄 Implementing JWT auth [1▶ 0⏸ 0⚠]"
6. coding-agent fetches context from MCP server
7. Implementation proceeds with real-time progress updates
8. Task completion stored in MCP with full audit trail
```

### Debugging an Issue
```
User: "Fix the login bug where users get stuck"

🔄 MCP Server Interaction:
1. 4genthub-hooks creates debug task on 4agenthub
2. Master orchestrator analyzes and delegates to debugger-agent
3. debugger-agent queries MCP for related context:
   - Previous login implementations
   - Related bug reports
   - Test case history
4. Root cause analysis performed and logged in MCP
5. Fix implementation tracked as subtasks
6. Verification and testing logged with results
7. Complete solution stored with troubleshooting notes
```

### Parallel Development
```
User: "Build complete CRUD for products"

🔄 Enterprise Orchestration:
1. Master orchestrator creates parent task in MCP
2. Spawns parallel subtasks on 4agenthub server:
   - Backend API → coding-agent
   - Frontend UI → ui-specialist-agent
   - Tests → test-orchestrator-agent
   - Documentation → documentation-agent
3. Status line shows: "🔄 Building CRUD [4▶ 0⏸ 0⚠]"
4. Each agent fetches context from MCP independently
5. Progress tracked in real-time across all parallel streams
6. Results coordinated through MCP task dependencies
7. Integrated solution delivered with full audit trail
```

### Real-Time Status Line Examples
```
# Single agent working
🎯 coding-agent | 🔄 Implementing JWT auth [1▶ 0⏸ 0⚠] | 📊 Branch: feature/auth | ⚡ Fast

# Parallel development
🎯 master-orchestrator | 🔄 Building CRUD system [4▶ 2⏸ 0⚠] | 📊 Branch: feature/products | ⚡ Fast

# Blocked task requiring attention
🎯 master-orchestrator | ⚠️ Database migration [0▶ 3⏸ 1⚠] | 📊 Branch: hotfix/db | 🐌 Blocked
```

## 🛠️ Development

### Project Structure
```
4genthub-hooks/
├── .claude/
│   ├── hooks/           # Python hook implementations
│   ├── status_lines/    # Status line renderers
│   ├── output-styles/   # Output formatting
│   └── settings.json    # Claude Code configuration
├── ai_docs/             # AI knowledge base
├── logs/                # Session and debug logs
├── .mcp.json           # MCP server connections
├── CLAUDE.md           # Agent instructions
└── README.md           # This file
```

### Adding Custom Hooks
```python
# .claude/hooks/custom_hook.py
import json
import sys

def process_hook(data):
    # Your hook logic here
    return {"success": True}

if __name__ == "__main__":
    data = json.loads(sys.stdin.read())
    result = process_hook(data)
    print(json.dumps(result))
```

### Testing Hooks
```bash
# Run hook tests
cd .claude/hooks/tests
python -m pytest test_*.py
```

## 🔐 Security

- **JWT Authentication** - Secure token-based access to 4agenthub
- **Tool Permission Enforcement** - Dynamic restrictions based on agent roles
- **Audit Logging** - Complete activity tracking
- **Context Isolation** - User-specific data separation

## 📚 Documentation

- **CLAUDE.md** - Complete agent system instructions
- **CLAUDE.local.md** - Local project-specific rules
- **ai_docs/** - Knowledge base for AI agents
- **CHANGELOG.md** - Version history and updates

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **4agenthub Team** - For the powerful MCP orchestration server
- **Anthropic** - For Claude and Claude Code
- **MCP Protocol** - For enabling agent communication standards

## 🔗 Links

- [4agenthub Website](https://www.4genthub.com)
- [4agenthub API Documentation](https://api.4genthub.com/docs)
- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [MCP Protocol Specification](https://modelcontextprotocol.io)

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/4genthub-hooks/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/4genthub-hooks/discussions)
- **4agenthub Website**: [https://www.4genthub.com](https://www.4genthub.com)
- **4agenthub API Server**: http://localhost:8000

---

<div align="center">
Built with ❤️ for intelligent AI orchestration
</div>