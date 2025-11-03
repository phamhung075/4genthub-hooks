#!/usr/bin/env python3
"""
Simple Formatter - Token-optimized output formatting.

Provides compact single-line summaries instead of multi-line formatted sections.
Saves ~800 tokens (80% reduction from 1,000 to 200 tokens).

Formats context data into minimal, scannable output.
"""

from typing import Dict, Any, List


class SimpleFormatter:
    """Minimal formatting with inline data."""

    @staticmethod
    def format(context: Dict[str, Any]) -> str:
        """Format context data into compact output."""
        parts = []

        # Git context
        if context.get('git'):
            git = context['git']
            if git.get('summary_only'):
                branch = git.get('branch', 'unknown')
                changes = git.get('change_count', 0)
                parts.append(f"📁 Git: {branch} ({changes} changes)")
            else:
                # Fall back to verbose if full mode
                branch = git.get('branch', 'unknown')
                changes = git.get('changes', [])
                parts.append(f"📁 Git Status: Branch '{branch}' | {len(changes)} uncommitted changes")

        # MCP context
        if context.get('mcp'):
            mcp = context['mcp']
            status = mcp.get('status', 'unknown')

            if mcp.get('mode') == 'compact':
                if status == 'ready':
                    parts.append(f"🌐 MCP: Ready | 💡 Use /mcp_status for details")
                elif status == 'unavailable':
                    parts.append("🌐 MCP: Unavailable")
                else:
                    parts.append(f"🌐 MCP: {status}")
            else:
                # Full mode formatting
                if mcp.get('project'):
                    project = mcp['project'].get('name', 'unknown')
                    parts.append(f"🌐 MCP Server: Connected | Project '{project}'")
                else:
                    parts.append(f"🌐 MCP: {status}")

        # Environment context
        if context.get('environment'):
            env = context['environment']

            if env.get('compact_mode'):
                # Compact format
                tech_parts = []
                if env.get('frontend_exists'):
                    react_v = env.get('react_version', '?')
                    tech_parts.append(f"React {react_v}")
                if env.get('backend_exists'):
                    py_v = env.get('python_version', '?')
                    tech_parts.append(f"Python {py_v}")

                if tech_parts:
                    ports = f"Ports: {env.get('frontend_port', 3800)}, {env.get('backend_port', 8000)}"
                    parts.append(f"🔧 Dev: {' + '.join(tech_parts)} | {ports}")
                    parts.append("💡 Use /dev_env for full details")
            else:
                # Full mode formatting (multi-line)
                details = []
                if env.get('frontend_exists'):
                    details.append("📦 Frontend: React + TypeScript")
                if env.get('backend_exists'):
                    details.append(f"🐍 Backend: Python {env.get('python_version', '?')}")
                if details:
                    parts.extend(details)

        # Agent role (always show if present)
        if context.get('agent_role'):
            role = context['agent_role']
            parts.append(f"🤖 Agent: {role.get('name', 'unknown')}")

        # Session info (always show)
        if context.get('session'):
            session = context['session']
            session_id = session.get('id', 'unknown')[:8]
            parts.append(f"📝 Session: {session_id}...")

        # Join all parts with newlines
        if not parts:
            return "🚀 Session started\n"

        return "\n".join(parts) + "\n"

    @staticmethod
    def format_full(context: Dict[str, Any]) -> str:
        """Format context data into verbose multi-line output (original behavior)."""
        sections = []

        # Git Section
        if context.get('git'):
            git = context['git']
            git_lines = [
                "📁 Git Status:",
                f"   Branch: {git.get('branch', 'unknown')}",
            ]

            if git.get('changes'):
                git_lines.append(f"   ⚠️  {len(git['changes'])} uncommitted changes")
                # Show first 5 changes
                for change in git['changes'][:5]:
                    git_lines.append(f"      {change}")
                if len(git['changes']) > 5:
                    git_lines.append(f"      ... and {len(git['changes']) - 5} more")

            if git.get('recent_commits'):
                git_lines.append("\n   Recent commits:")
                for commit in git['recent_commits'][:5]:
                    git_lines.append(f"      {commit}")

            sections.append("\n".join(git_lines))

        # MCP Section
        if context.get('mcp'):
            mcp = context['mcp']
            mcp_lines = ["🌐 MCP Server:"]

            if mcp.get('status') == 'connected':
                if mcp.get('project'):
                    proj = mcp['project']
                    mcp_lines.extend([
                        f"   📁 Project: {proj.get('name', 'unknown')}",
                        f"   📝 ID: {proj.get('id', 'unknown')}"
                    ])

                if mcp.get('branch'):
                    branch = mcp['branch']
                    mcp_lines.extend([
                        f"   🌿 Branch: {branch.get('git_branch_name', 'unknown')}",
                        f"   📊 Progress: {branch.get('progress_percentage', 0)}%"
                    ])

                if mcp.get('active_tasks'):
                    tasks = mcp['active_tasks']
                    mcp_lines.append(f"   📋 {len(tasks)} active task(s)")
                    for task in tasks[:3]:
                        mcp_lines.append(f"      • {task.get('title', 'Untitled')}")
                else:
                    mcp_lines.append("   📋 No active tasks")
            else:
                mcp_lines.append(f"   Status: {mcp.get('status', 'unknown')}")

            sections.append("\n".join(mcp_lines))

        # Environment Section
        if context.get('environment'):
            env = context['environment']
            env_lines = ["🔧 Development Environment:"]

            if env.get('frontend_exists'):
                env_lines.extend([
                    "",
                    "📦 Frontend (agenthub-frontend/)",
                    f"   • Framework: React {env.get('react_version', '?')}",
                    "   • Build: Vite",
                    "   • UI: Tailwind CSS, shadcn/ui",
                    f"   • Port: {env.get('frontend_port', 3800)}"
                ])

            if env.get('backend_exists'):
                env_lines.extend([
                    "",
                    "🐍 Backend (agenthub_main/)",
                    "   • Framework: FastMCP + FastAPI",
                    "   • Architecture: DDD (Domain-Driven Design)",
                    f"   • Language: Python {env.get('python_version', '?')}",
                    "   • ORM: SQLAlchemy",
                    f"   • Port: {env.get('backend_port', 8000)}"
                ])

            env_lines.extend([
                "",
                "🐳 Infrastructure:",
                "   • Container: Docker + docker-compose",
                "   • Database: PostgreSQL (Docker)",
                "   • Auth: Keycloak"
            ])

            sections.append("\n".join(env_lines))

        # Join all sections
        return "\n\n".join(sections) + "\n" if sections else "🚀 Session started\n"
