# 🚀 4genthub-hooks

> **Intelligent Claude Code Hooks Client for 4agenthub Hosted Service**
>
> A sophisticated hooks implementation that transforms Claude Code into an enterprise-grade AI agent orchestration system powered by the **hosted** 4agenthub service.

---

## 📦 Git Submodule Setup

> **This `.claude` directory is managed as a Git submodule for easy version control and updates**

### Working with the Submodule

**Edit and Push Changes:**
```bash
cd .claude
# Make your changes to hooks/agents/commands
git add -A
git commit -m "feat: your changes"
git push origin working-structure
# Update parent repository
cd ..
git add .claude
git commit -m "chore: update .claude submodule"
```

**Pull Latest Updates:**
```bash
cd .claude
git pull origin working-structure
cd ..
git add .claude
git commit -m "chore: update .claude submodule to latest"
```

**Repository:** `git@github.com:phamhung075/4genthub-hooks.git`
**Branch:** `working-structure` (flat structure without nesting)

---

## 🎆 **QUICK START - HOSTED SERVICE**

**⚡ Get started in 3 minutes - no server setup required!**

1. **Create Account**: [Register at 4genthub.com](https://www.4genthub.com) → Verify email
2. **Get API Token**: Dashboard → API Tokens → Generate new token
3. **Configure Client**: Copy `.mcp.json.sample` to `.mcp.json` and add your token
4. **Start Coding**: Open in Claude Code - all 31+ agents ready instantly!

✅ **Fully Hosted** - No local server installation
✅ **Enterprise Security** - SOC2 compliant infrastructure
✅ **99.9% Uptime** - Global CDN with high availability
✅ **Auto-scaling** - Handles any workload automatically

---

## 🌟 Overview

> **⚡ HOSTED SERVICE - NO SERVER SETUP REQUIRED!**
> 4genthub is a **fully hosted SaaS platform** - just create an account, get your API token, and start developing. No local server installation, configuration, or maintenance needed.

4genthub-hooks is a comprehensive **client-side implementation** that seamlessly integrates Claude Code with the **hosted 4agenthub service** to create a complete enterprise AI orchestration platform:

- 🤖 **31+ Specialized AI Agents** - From coding to architecture, testing to documentation
- 📊 **Real-time Task Management** - Visual status tracking and progress monitoring
- 🔄 **Intelligent Session Management** - Automatic agent loading and context preservation
- 🎯 **Smart Tool Enforcement** - Dynamic permissions based on agent roles
- 📈 **Enterprise Workflow Orchestration** - Professional task delegation and coordination

## 🔗 How It Works Together

### The Complete System Architecture

**4agenthub** (Hosted Service) + **4genthub-hooks** (Claude Code Client) = Enterprise AI Orchestration Platform

#### 🖥️ 4agenthub Hosted Service (`https://api.4genthub.com`)
The **cloud-based orchestration engine** that provides:
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

## 🌐 4genthub Frontend Interface - Visual Dashboard

### Real-Time Visual Monitoring at 4genthub.com

The 4genthub platform provides a comprehensive **web frontend interface** that gives you visual access to everything happening behind the scenes with your AI agents:

#### 🎯 **Project Context Visualization**
- **Real-time project overview** - See all your projects, branches, and active work streams
- **Project context display** - Visual representation of project scope, goals, and current status
- **Multi-project dashboard** - Manage multiple projects from a unified interface
- **Project health monitoring** - Quick overview of project progress and any issues

#### 📊 **Task Management Dashboard**
- **Task hierarchy visualization** - See parent tasks, subtasks, and dependencies in an intuitive tree view
- **Progress tracking** - Real-time progress bars and completion percentages for all tasks
- **Task details view** - Full context, requirements, and implementation notes for each task
- **Dependency mapping** - Visual representation of task dependencies and workflow sequences
- **Status indicators** - Clear visual status (todo, in-progress, blocked, completed) for all work items

#### 🤖 **Agent Activity Monitoring**
- **Real-time agent status** - See which agents are currently active and what they're working on
- **Agent assignment tracking** - Visual overview of which agents are assigned to which tasks
- **Agent performance metrics** - Response times, completion rates, and efficiency indicators
- **Agent coordination view** - Monitor parallel agent work and coordination patterns

#### 🔄 **MCP Data Synchronization**
- **Instant synchronization** - All MCP task updates from AI agents are immediately reflected in the web interface
- **Bidirectional updates** - Changes made in the web interface are instantly available to AI agents
- **Real-time notifications** - Get notified when agents complete tasks, encounter blockers, or need attention
- **Live activity feed** - Stream of all agent activities and task updates in real-time

#### 🔍 **Audit Trail & History**
- **Complete audit trail** - Visual timeline of all actions, decisions, and changes
- **Task history tracking** - See the full lifecycle of every task from creation to completion
- **Agent decision logs** - Understand why agents made specific choices and recommendations
- **Progress timeline** - Visual representation of project progress over time

#### 📈 **Analytics & Insights**
- **Project analytics** - Completion rates, time tracking, and productivity metrics
- **Agent performance insights** - Which agents are most effective for different types of work
- **Bottleneck identification** - Visual identification of workflow bottlenecks and delays
- **Trend analysis** - Track improvements and patterns in your development workflow

### 🎯 **Dual Access Model: The Best of Both Worlds**

Users get **two complementary interfaces** to their AI orchestration system:

#### 🖥️ **Claude Code Integration (via 4genthub-hooks)**
- **Programmatic access** - Work directly with AI agents through natural language
- **Command-line efficiency** - Execute complex workflows through conversation
- **Context-aware assistance** - AI agents understand your codebase and current work
- **Seamless development flow** - No context switching - work where you code

#### 🌐 **Web Frontend Dashboard (at 4genthub.com)**
- **Visual monitoring** - See everything happening in your projects at a glance
- **Management interface** - Organize projects, assign agents, and manage workflows
- **Team collaboration** - Share project status and progress with team members
- **Strategic overview** - High-level view of all projects and their health

### 🔗 **Synchronized Experience**

Both interfaces work together seamlessly:
- **Work in Claude Code** → **See progress in web dashboard**
- **Assign tasks in web interface** → **Agents pick them up in Claude Code**
- **Agent updates from Claude** → **Instantly visible in web dashboard**
- **Project changes from web** → **Immediately available to Claude agents**

This dual-interface approach ensures you have both the **deep, context-aware assistance** of Claude Code and the **visual project management capabilities** of a modern web dashboard - all synchronized in real-time through the MCP system.

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
│      4agenthub Hosted Service (BACKEND)     │
│        https://api.4genthub.com             │
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
3. **Hooks** create MCP task with full context on **hosted 4agenthub service**
4. **Master orchestrator** delegates to appropriate specialized agent
5. **Specialized agent** executes work and reports back
6. **Results** flow back through hosted service to Claude Code UI

## 💎 Value Proposition

### Why Use 4agenthub + 4genthub-hooks?

#### 🏢 **Enterprise-Grade AI Orchestration (Fully Hosted)**
Transform Claude Code from a single AI assistant into a **coordinated team of 31+ specialized agents** with:
- **Persistent Memory**: All work tracked and stored in the cloud across sessions
- **Professional Workflows**: Task delegation, progress tracking, and quality assurance
- **Audit Trails**: Complete transparency for compliance and team coordination
- **Parallel Execution**: Multiple agents working simultaneously on different aspects
- **Zero Infrastructure**: No servers to maintain - fully managed cloud service

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

#### 🔒 **Enterprise Security & Compliance (Cloud-Native)**
- **JWT Authentication**: Secure token-based access control
- **Role-Based Permissions**: Dynamic tool restrictions based on agent roles
- **Activity Logging**: Complete audit trail of all actions and decisions
- **Data Isolation**: User-specific contexts and secure data handling
- **Enterprise Security**: SOC2 compliant hosted infrastructure
- **High Availability**: 99.9% uptime SLA with global CDN

## 🚀 Quick Start

### Prerequisites

**Simple Setup - No Local Server Required:**

1. **4genthub Account** (Primary Requirement)
   - Create account at [https://www.4genthub.com](https://www.4genthub.com)
   - Generate API token from your dashboard
   - **No server installation needed** - fully hosted service

2. **4genthub-hooks** (Claude Code Client)
   - Claude Code integration layer
   - **Python 3.12** required (exact version)
   - This repository

3. **Claude Code** (latest version)

4. **Supported Platforms**
   - ✅ **Linux** (Ubuntu, Debian, Fedora, etc.)
   - ✅ **macOS** (Intel & Apple Silicon)
   - ✅ **Windows** (via WSL - Windows Subsystem for Linux)

### Installation Steps

#### Step 1: Create 4genthub Account
```bash
# 1. Register at https://www.4genthub.com
# 2. Complete account verification
# 3. Navigate to Dashboard → API Tokens
# 4. Generate new API token and copy it
# 5. Ready to use - no server setup required!
```

#### Step 2: Install Python 3.12 (if needed)

**Linux:**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3.12 python3.12-venv

# Fedora
sudo dnf install python3.12

# Verify installation
python3.12 --version
```

**macOS:**
```bash
# Using Homebrew
brew install python@3.12

# Verify installation
python3.12 --version
```

**Windows (WSL):**
```bash
# First, ensure WSL is installed and running Ubuntu
# Then follow Linux instructions above
sudo apt update && sudo apt install python3.12 python3.12-venv
```

#### Step 3: Setup 4genthub-hooks Client
```bash
# 1. Clone this repository (client implementation)
git clone https://github.com/phamhung075/4genthub-hooks.git

# 2. Rename folder to your project name and set up your own git
cd 4genthub-hooks
rm -rf .git                          # Remove original git history
cd ..
mv 4genthub-hooks your-project-name  # Rename to your project
cd your-project-name
git init                              # Initialize your own git repository
git add .
git commit -m "Initial commit - 4genthub-hooks setup"

# 3. Configure connection with your API token
nano .mcp.json

# Update the configuration to include your token:
# {
#   "mcpServers": {
#     "agenthub_http": {
#       "type": "http",
#       "url": "http://localhost:8000/mcp",  # Or https://api.4genthub.com/mcp for hosted
#       "headers": {
#         "Accept": "application/json, text/event-stream",
#         "Authorization": "Bearer YOUR_API_TOKEN_HERE"  # Replace with your actual token
#       }
#     }
#   }
# }

# 4. Test connection to hosted service
curl -H "Authorization: Bearer YOUR_API_TOKEN" https://api.4genthub.com/mcp/health
```

#### Step 4: Launch Claude Code
```bash
# Open in Claude Code (hooks will auto-activate)
claude-code .

# System will automatically:
# ✅ Connect to hosted 4agenthub service
# ✅ Load master-orchestrator-agent
# ✅ Enable real-time status tracking
# ✅ Activate all 31+ specialized agents
```

### Verification

After setup, you should see:
```
🎯 Active: master-orchestrator-agent | 🔗 MCP: ✅ Connected | 🌿 main
```

**Test the integration:**
```
User: "Create a simple hello world function"
Expected: Auto-delegation to coding-agent with MCP task tracking
```

## ⚙️ Configuration

### Hosted Service Configuration (`.mcp.json`)

The project connects to multiple hosted services:

- **agenthub_http** - Main 4agenthub orchestration service (hosted at api.4genthub.com)
- **sequential-thinking** - Chain-of-thought reasoning
- **shadcn-ui-server** - UI component management
- **browsermcp** - Browser automation capabilities

**Example configuration:**
```json
{
  "mcpServers": {
    "agenthub_http": {
      "type": "http",
      "url": "https://api.4genthub.com/mcp",
      "headers": {
        "Accept": "application/json, text/event-stream",
        "Authorization": "Bearer YOUR_API_TOKEN_HERE"
      }
    }
  }
}
```

**Note**: If you're using a local development server, change the URL to `http://localhost:8000/mcp`

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
🎯 Active: master-orchestrator-agent | 🔗 MCP: ✅ Connected | 🌿 feature/auth
```

- **Current Agent** - Shows active agent role
- **MCP Connection** - Real-time connection status to 4genthub service
- **Git Branch** - Active git branch name

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
3. Creates MCP task on hosted 4agenthub service:
   POST https://api.4genthub.com/api/v2/tasks {
     title: "Implement JWT authentication",
     assignees: "coding-agent",
     details: "Full requirements and context..."
   }
4. Delegates to coding-agent with task_id only
5. coding-agent fetches context from hosted service
6. Implementation proceeds with real-time progress updates
7. Task completion stored in hosted service with full audit trail
```

### Debugging an Issue
```
User: "Fix the login bug where users get stuck"

🔄 Hosted Service Interaction:
1. 4genthub-hooks creates debug task on hosted 4agenthub service
2. Master orchestrator analyzes and delegates to debugger-agent
3. debugger-agent queries hosted service for related context:
   - Previous login implementations
   - Related bug reports
   - Test case history
4. Root cause analysis performed and logged in hosted service
5. Fix implementation tracked as subtasks
6. Verification and testing logged with results
7. Complete solution stored with troubleshooting notes
```

### Parallel Development
```
User: "Build complete CRUD for products"

🔄 Enterprise Orchestration:
1. Master orchestrator creates parent task in hosted service
2. Spawns parallel subtasks on hosted 4agenthub service:
   - Backend API → coding-agent
   - Frontend UI → ui-specialist-agent
   - Tests → test-orchestrator-agent
   - Documentation → documentation-agent
3. Each agent fetches context from hosted service independently
4. Progress tracked in real-time across all parallel streams
5. Results coordinated through hosted service task dependencies
6. Integrated solution delivered with full audit trail
```

### Real-Time Status Line

**Current Status Line Display:**
```
🎯 Active: master-orchestrator-agent | 🔗 MCP: ✅ Connected | 🌿 main
```

The status line shows:
- **Active Agent**: Currently loaded agent (e.g., master-orchestrator-agent)
- **MCP Connection**: Status of connection to 4genthub service (✅ Connected or ❌ Disconnected)
- **Git Branch**: Current git branch name

## 🔧 Troubleshooting

### Status Line Not Displaying

If you're not seeing the dynamic status line features described in this documentation, here are the most common causes and solutions:

#### 1. Status Line Display Issues

**The status line requires Claude Code to properly load and execute the Python script**
- Ensure **Python 3.12** is installed and accessible
- The status line updates when there are active MCP tasks
- Check that `.mcp.json` is properly configured with your API token
- The status line will show "JSON Error" if MCP connection fails

#### 2. How to Verify Status Line is Working

**Create a test task to verify functionality:**
- Create a task using MCP: Any request that creates a task (most complex requests)
- The status line should update to show agent and task information
- If you see `"[Agent] [Claude] 💭 JSON Error"` - check MCP connection
- Expected format: `🎯 Active: agent-name | 🔗 MCP: ✅ Connected | 🌿 main`

#### 3. Common Issues and Solutions

**No active tasks = minimal status line display**
- The fancy status line examples require active MCP tasks
- Simple requests that don't create tasks show basic status only
- Complex requests (implementing features, debugging, etc.) create tasks and show full status

**MCP not connected = error messages**
- Check `.mcp.json` configuration
- Verify your 4genthub API token is valid
- Test connection: `curl -H "Authorization: Bearer YOUR_API_TOKEN" https://api.4genthub.com/mcp/health`
- Ensure network connectivity to hosted service

**Python not found = status line won't load**
- Install Python 3.12 (exact version required)
- Verify with: `python3.12 --version`
- Ensure Python is in your system PATH

#### 4. Manual Testing Command

**Test the status line script directly:**
```bash
python3 ./.claude/status_lines/status_line_mcp.py
```

This command will test the status line functionality independently and show any errors in loading or MCP communication.

#### 5. Understanding Status Line Behavior

**The status line behavior varies based on your activity:**
- **No MCP tasks**: Shows basic agent name and ready status
- **Active tasks**: Shows detailed progress with counts and descriptions
- **Multiple parallel tasks**: Shows coordination and progress across all tasks
- **Blocked tasks**: Shows warning indicators and blocked status

**Note**: The sophisticated status line features demonstrated in this documentation require:
- Active MCP connection to 4genthub hosted service
- Tasks created through the MCP system
- Proper Python 3.12 installation
- Valid API token configuration

If you're just reading documentation or asking simple questions, you may not see the full status line features until you start working on complex tasks that trigger MCP task creation.

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

- **JWT Authentication** - Secure token-based access to hosted 4agenthub service
- **Tool Permission Enforcement** - Dynamic restrictions based on agent roles
- **Audit Logging** - Complete activity tracking in cloud
- **Context Isolation** - User-specific data separation in hosted environment

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

- **Issues**: [GitHub Issues](https://github.com/phamhung075/4genthub-hooks/issues)
- **Discussions**: [GitHub Discussions](https://github.com/phamhung075/4genthub-hooks/discussions)
- **4agenthub Website**: [https://www.4genthub.com](https://www.4genthub.com)
- **4agenthub Hosted API**: https://api.4genthub.com

---

<div align="center">
Built with ❤️ for intelligent AI orchestration
</div>