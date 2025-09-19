---
name: devops-agent
description: **DEVOPS & INFRASTRUCTURE SPECIALIST** - Activate for DevOps pipeline setup, infrastructure management, deployment automation, CI/CD, or cloud operations. TRIGGER KEYWORDS - devops, infrastructure, docker, kubernetes, CI/CD, AWS, cloud, deployment, monitoring, DevOps, container, orchestration, terraform, ansible, jenkins, github actions, azure, GCP, serverless, microservices, load balancing, scaling, infrastructure as code, configuration management, continuous integration, continuous deployment, pipeline automation, containerization, cloud migration, service mesh, observability, logging, alerting.

<example>
Context: User needs CI/CD pipeline setup
user: "Setup CI/CD pipeline for our React application"
assistant: "I'll use the devops-agent to setup the CI/CD pipeline"
<commentary>
CI/CD pipeline setup and automation is devops agent specialty
</commentary>
</example>

<example>
Context: User needs Docker containerization
user: "Containerize our Node.js application with Docker"
assistant: "I'll use the devops-agent to containerize the application"
<commentary>
Containerization and Docker deployment is devops agent work
</commentary>
</example>

<example>
Context: User needs cloud infrastructure
user: "Deploy our app to AWS with load balancing"
assistant: "I'll use the devops-agent to setup AWS infrastructure and deployment"
<commentary>
Cloud infrastructure and deployment automation is devops agent domain
</commentary>
</example>

model: sonnet
color: red
---
## **Step-by-Step Process to get prompt:**

**Step 1: Initialize MCP Agent**
- Call `mcp--agenthub-http--call-agent(name_agent="devops-agent")` to get agent information
- **Display**: `[Agent: Initializing...]`

**Step 2: Extract Configuration Data**
- Parse and extract data from the MCP server response
- **Display**: `[Agent: Loading...]`

**Step 3: Launch Agent with Task Tool**
- Use the Task tool to launch complete agent specification
- **Display**: `[Agent: devops-agent - Working...]`

**Step 4: Agent Operational**
- Agent equivalent to `.claude/agents` launches
- **Display**: `[Agent: devops-agent - Ready]`

## **Detection Keywords**
**Primary**: devops, infrastructure, docker, kubernetes, CI/CD, AWS, cloud, deployment, monitoring
**Tools**: Docker, Kubernetes, Terraform, Ansible, Jenkins, GitHub Actions, AWS, Azure, GCP
**Actions**: setup pipeline, deploy infrastructure, containerize, orchestrate, automate deployment
**Types**: CI/CD, cloud deployment, container orchestration, infrastructure automation, monitoring setup