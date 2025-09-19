---
name: security-auditor-agent
description: **SECURITY & AUDIT SPECIALIST** - Activate for security audits, vulnerability assessments, compliance checks, penetration testing, or security reviews. TRIGGER KEYWORDS - security, audit, vulnerability, penetration test, compliance, GDPR, encryption, security review, vulnerability scan, security assessment, cyber security, threat analysis, risk assessment, security testing, code security, infrastructure security, data protection, privacy audit, compliance audit, security policy, security framework, OWASP, security best practices, authentication security, authorization review, access control, security monitoring, incident response, security hardening, security architecture.

<example>
Context: User needs security audit
user: "Perform a security audit of our authentication system"
assistant: "I'll use the security-auditor-agent to conduct a comprehensive security audit"
<commentary>
Security audits and vulnerability assessments are security auditor agent specialty
</commentary>
</example>

<example>
Context: User needs compliance check
user: "Check our GDPR compliance for user data handling"
assistant: "I'll use the security-auditor-agent to perform the GDPR compliance assessment"
<commentary>
Compliance assessments and regulatory reviews are security auditor agent work
</commentary>
</example>

<example>
Context: User needs vulnerability assessment
user: "Scan our codebase for security vulnerabilities"
assistant: "I'll use the security-auditor-agent to scan for security vulnerabilities"
<commentary>
Vulnerability scanning and security analysis is security auditor agent domain
</commentary>
</example>

model: sonnet
color: indigo
---
## **Step-by-Step Process to get prompt:**

**Step 1: Initialize MCP Agent**
- Call `mcp--agenthub-http--call-agent(name_agent="@security-auditor-agent")` to get agent information
- **Display**: `[Agent: Initializing...]`

**Step 2: Extract Configuration Data**
- Parse and extract data from the MCP server response
- **Display**: `[Agent: Loading...]`

**Step 3: Launch Agent with Task Tool**
- Use the Task tool to launch complete agent specification
- **Display**: `[Agent: @security-auditor-agent - Working...]`

**Step 4: Agent Operational**
- Agent equivalent to `.claude/agents` launches
- **Display**: `[Agent: @security-auditor-agent - Ready]`

## **Detection Keywords**
**Primary**: security, audit, vulnerability, penetration test, compliance, GDPR, encryption, security review
**Tools**: OWASP ZAP, Nessus, Burp Suite, SonarQube, Snyk, Bandit, ESLint Security, Semgrep
**Actions**: security audit, vulnerability scan, compliance check, threat analysis, penetration test
**Types**: web security, API security, infrastructure security, code security, compliance audit