# Changelog

All notable changes to the agenthub AI Agent Orchestration Platform.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) | Versioning: [Semantic](https://semver.org/spec/v2.0.0.html)

## [Unreleased]

### Fixed
- **UserPromptSubmit hook rejected every project whose rules file is `AGENTS.md`** — `utils/config_validator.py` required `CLAUDE.md` by name, so renaming the project rules file made every prompt fail with a non-blocking hook error. The check now accepts either name and the error names both.
  - Files: `hooks/utils/config_validator.py`, `hooks/utils/find_project_root.py`, `hooks/utils/environment_detector.py`, `hooks/utils/mcp_task_interceptor.py`, `hooks/pre_tool_use.py`
  - Why either name: Claude Code, Codex and Gemini all read `AGENTS.md`, while projects created before the rename still carry `CLAUDE.md`. Requiring one name would break the other half.
  - Validated: the validator accepts a project with `AGENTS.md`, accepts one with `CLAUDE.md`, and reports both names when neither exists; the hook exits 0.

## Quick Setup
update token on .mcp.json

---
*For detailed version history, see git commits. This changelog focuses on major releases and breaking changes.*