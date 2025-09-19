# Complete Tools List

A comprehensive list of all available tools in TypeScript function signature format with their purposes.

## Core Development Tools

```typescript
Task(description: string, prompt: string, subagent_type: string): any
```
Launch specialized agents for complex tasks, multi-step operations, or when specific expertise is needed


```typescript
Bash(command: string, description?: string, run_in_background?: boolean, timeout?: number): any
```
Execute bash commands in a persistent shell session with optional timeout and background execution


```typescript
Glob(pattern: string, path?: string): any
```
Fast file pattern matching tool for finding files by name patterns in any codebase size


```typescript
Grep(pattern: string, path?: string, glob?: string, type?: string, output_mode?: string, -A?: number, -B?: number, -C?: number, -i?: boolean, -n?: boolean, multiline?: boolean, head_limit?: number): any
```
Powerful search tool built on ripgrep for searching file contents with regex support


```typescript
ExitPlanMode(plan: string): any
```
Exit plan mode after presenting implementation plan for coding tasks


## File Operations

```typescript
Read(file_path: string, limit?: number, offset?: number): any
```
Read files from the local filesystem including text, images, PDFs, and Jupyter notebooks


```typescript
Edit(file_path: string, old_string: string, new_string: string, replace_all?: boolean): any
```
Perform exact string replacements in files


```typescript
MultiEdit(file_path: string, edits: Array<{old_string: string, new_string: string, replace_all?: boolean}>): any
```
Make multiple edits to a single file in one operation


```typescript
Write(file_path: string, content: string): any
```
Write a file to the local filesystem, overwriting if it exists


```typescript
NotebookEdit(notebook_path: string, new_source: string, cell_id?: string, cell_type?: string, edit_mode?: string): any
```
Edit specific cells in Jupyter notebook files


## Web and Search Tools

```typescript
WebFetch(url: string, prompt: string): any
```
Fetch content from URLs and process with AI model for analysis


```typescript
WebSearch(query: string, allowed_domains?: string[], blocked_domains?: string[]): any
```
Search the web for current information beyond knowledge cutoff


## Task Management

```typescript
TodoWrite(todos: Array<{content: string, status: string, activeForm: string}>): any
```
Create and manage structured task lists for tracking progress and organizing complex tasks


## Process Management

```typescript
BashOutput(bash_id: string, filter?: string): any
```
Retrieve output from running or completed background bash shells


```typescript
KillBash(shell_id: string): any
```
Terminate a running background bash shell by its ID


## agenthub Project Management Tools

```typescript
mcp__agenthub_http__manage_task(action: string, git_branch_id?: string, title?: string, assignees?: string, ...various optional params): any
```
Complete task lifecycle management with CRUD operations, search, dependencies, and workflow management


```typescript
mcp__agenthub_http__manage_subtask(action: string, task_id?: string, subtask_id?: string, title?: string, ...various optional params): any
```
Manage subtasks within parent tasks for hierarchical task breakdown and progress tracking


```typescript
mcp__agenthub_http__manage_context(action: string, level?: string, context_id?: string, data?: string, ...various optional params): any
```
Manage hierarchical contexts across 4 tiers (Global → Project → Branch → Task) with inheritance


```typescript
mcp__agenthub_http__manage_project(action: string, project_id?: string, name?: string, description?: string, ...various optional params): any
```
Manage projects throughout lifecycle with health monitoring and resource management


```typescript
mcp__agenthub_http__manage_git_branch(action: string, project_id?: string, git_branch_id?: string, git_branch_name?: string, ...various optional params): any
```
Manage git branches with CRUD operations, agent assignments, and lifecycle management


```typescript
mcp__agenthub_http__manage_agent(action: string, project_id?: string, agent_id?: string, name?: string, ...various optional params): any
```
Manage agent registration, assignment, and lifecycle within projects (33 specialized agents)


```typescript
mcp__agenthub_http__call_agent(name_agent: string): any
```
Load and invoke specialized agents by name for task execution with vision insights


## Authentication Tools

```typescript
mcp__agenthub_http__validate_token(token: string): any
```
Validate an authentication token and get user information


```typescript
mcp__agenthub_http__get_rate_limit_status(token: string): any
```
Get rate limit status for a token


```typescript
mcp__agenthub_http__revoke_token(token: string): any
```
Revoke an authentication token


```typescript
mcp__agenthub_http__get_auth_status(): any
```
Get authentication system status and configuration


```typescript
mcp__agenthub_http__generate_token(): any
```
Generate secure authentication token (deprecated - use API at /api/v2/tokens)


```typescript
mcp__agenthub_http__manage_connection(include_details?: boolean, user_id?: string): any
```
Basic health check endpoint for system monitoring


## MCP Resource Tools

```typescript
ListMcpResourcesTool(server?: string): any
```
List available resources from configured MCP servers


```typescript
ReadMcpResourceTool(server: string, uri: string): any
```
Read specific resource from an MCP server by URI


## AI Thinking Tools

```typescript
mcp__sequential-thinking__sequentialthinking(thought: string, nextThoughtNeeded: boolean, thoughtNumber: number, totalThoughts: number, ...various optional params): any
```
Dynamic problem-solving through flexible thinking process with revision capabilities


## UI Component Tools

```typescript
mcp__shadcn-ui-server__list-components(): any
```
List available shadcn/ui components


```typescript
mcp__shadcn-ui-server__get-component-docs(component: string): any
```
Get documentation for specific shadcn/ui component


```typescript
mcp__shadcn-ui-server__install-component(component: string, runtime?: string): any
```
Install shadcn/ui component with specified package manager


```typescript
mcp__shadcn-ui-server__list-blocks(): any
```
List available shadcn/ui blocks


```typescript
mcp__shadcn-ui-server__get-block-docs(block: string): any
```
Get documentation for specific shadcn/ui block


```typescript
mcp__shadcn-ui-server__install-blocks(block: string, runtime?: string): any
```
Install shadcn/ui blocks with specified package manager


## IDE Integration Tools

```typescript
mcp__ide__getDiagnostics(uri?: string): any
```
Get language diagnostics from VS Code for files


```typescript
mcp__ide__executeCode(code: string): any
```
Execute Python code in Jupyter kernel for current notebook


## ElevenLabs Audio Tools

### Text-to-Speech

```typescript
mcp__ElevenLabs__text_to_speech(text: string, voice_name?: string, model_id?: string, ...various audio params): any
```
Convert text to speech with ElevenLabs API (costs may apply)


```typescript
mcp__ElevenLabs__text_to_voice(voice_description: string, text?: string, output_directory?: string): any
```
Create voice previews from text prompt (costs may apply)


```typescript
mcp__ElevenLabs__text_to_sound_effects(text: string, duration_seconds?: number, loop?: boolean, ...various params): any
```
Generate sound effects from text description with ElevenLabs API (costs may apply)


### Speech Processing

```typescript
mcp__ElevenLabs__speech_to_text(input_file_path: string, language_code?: string, diarize?: boolean, ...various params): any
```
Transcribe speech from audio file with ElevenLabs API (costs may apply)


```typescript
mcp__ElevenLabs__speech_to_speech(input_file_path: string, voice_name?: string, output_directory?: string): any
```
Transform audio from one voice to another (costs may apply)


### Voice Management

```typescript
mcp__ElevenLabs__search_voices(search?: string, sort?: string, sort_direction?: string): any
```
Search for voices in ElevenLabs voice library


```typescript
mcp__ElevenLabs__list_models(): any
```
List all available ElevenLabs models


```typescript
mcp__ElevenLabs__get_voice(voice_id: string): any
```
Get details of specific ElevenLabs voice


```typescript
mcp__ElevenLabs__voice_clone(name: string, files: string[], description?: string): any
```
Create instant voice clone using audio files (costs may apply)


```typescript
mcp__ElevenLabs__create_voice_from_preview(generated_voice_id: string, voice_name: string, voice_description: string): any
```
Add generated voice to library (costs may apply)


```typescript
mcp__ElevenLabs__search_voice_library(search?: string, page?: number, page_size?: number): any
```
Search entire ElevenLabs voice library


### Audio Processing

```typescript
mcp__ElevenLabs__isolate_audio(input_file_path: string, output_directory?: string): any
```
Isolate audio from file with ElevenLabs API (costs may apply)


```typescript
mcp__ElevenLabs__play_audio(input_file_path: string): any
```
Play audio file (WAV and MP3 formats)


### AI Agents

```typescript
mcp__ElevenLabs__create_agent(name: string, first_message: string, system_prompt: string, ...various params): any
```
Create conversational AI agent with ElevenLabs (costs may apply)


```typescript
mcp__ElevenLabs__add_knowledge_base_to_agent(agent_id: string, knowledge_base_name: string, url?: string, input_file_path?: string, text?: string): any
```
Add knowledge base to ElevenLabs agent (costs may apply)


```typescript
mcp__ElevenLabs__list_agents(): any
```
List all available ElevenLabs conversational AI agents


```typescript
mcp__ElevenLabs__get_agent(agent_id: string): any
```
Get details about specific ElevenLabs conversational AI agent


```typescript
mcp__ElevenLabs__get_conversation(conversation_id: string): any
```
Get conversation details and transcript from ElevenLabs agent


```typescript
mcp__ElevenLabs__list_conversations(agent_id?: string, cursor?: string, ...various filters): any
```
List agent conversations with metadata and filtering


### Phone and Communication

```typescript
mcp__ElevenLabs__make_outbound_call(agent_id: string, agent_phone_number_id: string, to_number: string): any
```
Make outbound call using ElevenLabs agent (costs may apply)


```typescript
mcp__ElevenLabs__list_phone_numbers(): any
```
List all phone numbers associated with ElevenLabs account


### Music and Audio Generation

```typescript
mcp__ElevenLabs__compose_music(prompt?: string, composition_plan?: object, music_length_ms?: number, output_directory?: string): any
```
Convert prompt to music with ElevenLabs (costs may apply)


```typescript
mcp__ElevenLabs__create_composition_plan(prompt: string, music_length_ms?: number, source_composition_plan?: object): any
```
Create composition plan for music generation


### Account Management

```typescript
mcp__ElevenLabs__check_subscription(): any
```
Check current ElevenLabs subscription status and usage


## Browser Automation Tools

### Navigation

```typescript
mcp__browsermcp__browser_navigate(url: string): any
```
Navigate browser to specified URL


```typescript
mcp__browsermcp__browser_go_back(): any
```
Navigate browser to previous page


```typescript
mcp__browsermcp__browser_go_forward(): any
```
Navigate browser to next page


### Page Interaction

```typescript
mcp__browsermcp__browser_snapshot(): any
```
Capture accessibility snapshot of current browser page


```typescript
mcp__browsermcp__browser_click(element: string, ref: string): any
```
Perform click on web page element


```typescript
mcp__browsermcp__browser_hover(element: string, ref: string): any
```
Hover over element on web page


```typescript
mcp__browsermcp__browser_type(element: string, ref: string, text: string, submit: boolean): any
```
Type text into editable web element


```typescript
mcp__browsermcp__browser_select_option(element: string, ref: string, values: string[]): any
```
Select option in dropdown element


```typescript
mcp__browsermcp__browser_press_key(key: string): any
```
Press keyboard key in browser


### Utilities

```typescript
mcp__browsermcp__browser_wait(time: number): any
```
Wait for specified time in seconds


```typescript
mcp__browsermcp__browser_get_console_logs(): any
```
Get console logs from browser


```typescript
mcp__browsermcp__browser_screenshot(): any
```
Take screenshot of current browser page

---

## Tool Categories Summary

- **Core Development**: 5 tools (Task, Bash, Glob, Grep, ExitPlanMode)
- **File Operations**: 5 tools (Read, Edit, MultiEdit, Write, NotebookEdit)
- **Web & Search**: 2 tools (WebFetch, WebSearch)
- **Task Management**: 1 tool (TodoWrite)
- **Process Management**: 2 tools (BashOutput, KillBash)
- **agenthub Project**: 7 tools (task, subtask, context, project, branch, agent management)
- **Authentication**: 6 tools (token validation, rate limiting, auth status)
- **MCP Resources**: 2 tools (list and read MCP resources)
- **AI Thinking**: 1 tool (sequential thinking)
- **UI Components**: 6 tools (shadcn/ui components and blocks)
- **IDE Integration**: 2 tools (diagnostics, code execution)
- **ElevenLabs Audio**: 26 tools (TTS, STT, voice management, AI agents, music)
- **Browser Automation**: 12 tools (navigation, interaction, utilities)

**Total: 77 tools available**