# Changelog

All notable changes to the agenthub AI Agent Orchestration Platform.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) | Versioning: [Semantic](https://semver.org/spec/v2.0.0.html)

## [Unreleased]

### Fixed
- **`docs_indexer.py` wrote `ai_docs/index.json` without a final newline, so the consuming repository's own `end-of-file-fixer` refused the commit that regenerated it** — `update_index()` ended at `json.dump(...)`, which writes no terminal newline, while the 4genthub repository's `pre-commit-hooks` v5.0.0 `end-of-file-fixer` requires one. The generator now writes the newline itself, so the hook passes over the output UNMODIFIED. Do not relax the hook to spare the generator.
  - Files: `hooks/utils/docs_indexer.py`
  - Reproduce: regenerate `ai_docs/index.json`, then run `end-of-file-fixer` over it — before this change the hook exits 1 with "files were modified by this hook" and rewrites the file; after, it exits 0 and modifies nothing.
  - Validated 2026-10-09, both sides in one sandbox: the pre-fix revision (`git show HEAD:hooks/utils/docs_indexer.py`) produces last byte `0x7d`, hook exit **1**, file **MODIFIED**; the fixed revision produces last byte `0x0a`, hook exit **0**, file **UNMODIFIED**. Harness and measurements: `FINDING-docs-indexer-final-newline-2026-10-09.md`, beside the 4genthub-min rig.
- **UserPromptSubmit hook rejected every project whose rules file is `AGENTS.md`** — `utils/config_validator.py` required `CLAUDE.md` by name, so renaming the project rules file made every prompt fail with a non-blocking hook error. The check now accepts either name and the error names both.
  - Files: `hooks/utils/config_validator.py`, `hooks/utils/find_project_root.py`, `hooks/utils/environment_detector.py`, `hooks/utils/mcp_task_interceptor.py`, `hooks/pre_tool_use.py`
  - Why either name: Claude Code, Codex and Gemini all read `AGENTS.md`, while projects created before the rename still carry `CLAUDE.md`. Requiring one name would break the other half.
  - Validated: the validator accepts a project with `AGENTS.md`, accepts one with `CLAUDE.md`, and reports both names when neither exists; the hook exits 0.

## Quick Setup
update token on .mcp.json

---
*For detailed version history, see git commits. This changelog focuses on major releases and breaking changes.*