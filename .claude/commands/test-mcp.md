**Test Plan for agenthub_http Tools Actions**
   $ARGUMENTS

**Test Checklist:**
☐ Test project management actions (create 2 projects, get, list, update, health checks, set project context)
☐ Test git branch management actions (create 2 branches, get, list, update, agent assignment, set branch context)  
☐ Test task management actions (create 5 tasks on first branch, 2 tasks on second branch, update, get, list, search, next, random dependencies to other tasks, assign agent)
☐ Test task management actions on first branch (update, get, list, search, next, random dependencies to other tasks, assign agent)
☐ Test subtask management actions (create 4 subtasks for each task on first branch, TDD steps, update, list, get, complete)
☐ Try to complete a task
☐ Verify context management is working on different layers
☐ Summarize all issues that appear during testing, write in .md file format in ai_docs folder
☐ For each issue, write detailed prompts per issue for fixes in new chat, write in same .md file
☐ Update global context

**Global Context:**

**1️⃣ Organization Settings**
- Company name and structure
- Team configuration (24/7 AI-powered operations)
- Communication protocols and collaboration tools
- Automation rules for tasks, code review, testing, deployment
- AI agent orchestration settings

**2️⃣ Security Policies**
- Data classification levels (public, internal, confidential, secret)
- Multi-factor authentication and RBAC
- AES-256 encryption at rest, TLS 1.3 in transit
- Compliance standards (GDPR, HIPAA, SOC2, ISO 27001)
- Vulnerability scanning and incident response SLAs

**3️⃣ Coding Standards**
- TypeScript: v5.x with strict mode, ESLint, Prettier
- Python: 3.11+ with PEP 8, Black formatter, type hints
- React: v18.x with hooks, Tailwind CSS
- 80% minimum test coverage, TDD preferred
- GitFlow workflow with 2-approval code reviews

**4️⃣ Workflow Templates**
- Feature Development: 2-week sprints with 7 phases
- Bug Fixing: Priority-based response times (1hr for critical)
- Release Management: Bi-weekly releases with blue-green deployment

**5️⃣ Delegation Rules**
- Task routing by expertise area
- 3-level escalation matrix
- Clear approval authority for different change types