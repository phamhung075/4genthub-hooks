- function shell(args: { command: string[]; timeout_ms?: number; workdir?: string; with_escalated_permissions?: boolean; justification?: string; }): Promise<any>; — Runs a shell command and returns its output.


- function update_plan(args: { explanation?: string; plan: { status: "pending" | "in_progress" | "completed"; step: string; }[]; }): Promise<any>; — Updates the task plan with step statuses.


- function view_image(args: { path: string; }): Promise<any>; — Attaches a local image to the conversation context.


- function ElevenLabs__add_knowledge_base_to_agent(args: { agent_id: string; knowledge_base_name: string; url?: string; input_file_path?: string; text?: string; }): Promise<any>; — Adds a knowledge base to an ElevenLabs agent.


- function ElevenLabs__check_subscription(): Promise<any>; — Retrieves the current ElevenLabs subscription status.


- function ElevenLabs__compose_music(args: { prompt?: string; composition_plan?: string; music_length_ms?: string; output_directory?: string; }): Promise<any>; — Converts a prompt or plan into generated music.


- function ElevenLabs__create_agent(args: { name: string; first_message: string; system_prompt: string; voice_id?: string; language?: string; llm?: string; temperature?: number; max_tokens?: string; model_id?: string; asr_quality?: string; optimize_streaming_latency?: number; stability?: number; similarity_boost?: number; turn_timeout?: number; max_duration_seconds?: number; record_voice?: boolean; retention_days?: number; }): Promise<any>; — Creates a conversational ElevenLabs agent with custom configuration.


- function ElevenLabs__create_composition_plan(args: { prompt: string; music_length_ms?: string; source_composition_plan?: string; }): Promise<any>; — Generates a composition plan for ElevenLabs music creation.


- function ElevenLabs__create_voice_from_preview(args: { generated_voice_id: string; voice_name: string; voice_description: string; }): Promise<any>; — Saves a generated voice preview into the ElevenLabs voice library.


- function ElevenLabs__get_agent(args: { agent_id: string; }): Promise<any>; — Retrieves details about a specific ElevenLabs conversational agent.


- function ElevenLabs__get_conversation(args: { conversation_id: string; }): Promise<any>; — Fetches conversation metadata and full transcript from ElevenLabs.


- function ElevenLabs__get_voice(args: { voice_id: string; }): Promise<any>; — Obtains detailed information about a specific ElevenLabs voice.


- function ElevenLabs__isolate_audio(args: { input_file_path: string; output_directory?: string; }): Promise<any>; — Separates vocals or instruments from an audio file using ElevenLabs.


- function ElevenLabs__list_agents(): Promise<any>; — Lists all ElevenLabs conversational agents for the account.


- function ElevenLabs__list_conversations(args: { agent_id?: string; cursor?: string; call_start_before_unix?: string; call_start_after_unix?: string; page_size?: number; max_length?: number; }): Promise<any>; — Retrieves paginated ElevenLabs agent conversations.


- function ElevenLabs__list_models(): Promise<any>; — Returns the available ElevenLabs models for speech and agents.


- function ElevenLabs__list_phone_numbers(): Promise<any>; — Lists phone numbers associated with the ElevenLabs account.


- function ElevenLabs__make_outbound_call(args: { agent_id: string; agent_phone_number_id: string; to_number: string; }): Promise<any>; — Initiates an outbound phone call handled by an ElevenLabs agent.


- function ElevenLabs__play_audio(args: { input_file_path: string; }): Promise<any>; — Plays a local audio file via ElevenLabs tooling.


- function ElevenLabs__search_voice_library(args: { page?: number; page_size?: number; search?: string; }): Promise<any>; — Searches the shared ElevenLabs voice library.


- function ElevenLabs__search_voices(args: { search?: string; sort?: string; sort_direction?: string; }): Promise<any>; — Searches existing voices within the user’s ElevenLabs library.


- function ElevenLabs__speech_to_speech(args: { input_file_path: string; output_directory?: string; voice_name?: string; }): Promise<any>; — Transforms audio into another voice using ElevenLabs speech-to-speech.


- function ElevenLabs__speech_to_text(args: { input_file_path: string; language_code?: string; diarize?: boolean; output_directory?: string; save_transcript_to_file?: boolean; return_transcript_to_client_directly?: boolean; }): Promise<any>; — Transcribes audio to text with optional diarization via ElevenLabs.


- function ElevenLabs__text_to_sound_effects(args: { text: string; duration_seconds?: number; loop?: boolean; output_directory?: string; output_format?: string; }): Promise<any>; — Generates sound effects from text descriptions through ElevenLabs.


- function ElevenLabs__text_to_speech(args: { text: string; voice_id?: string; voice_name?: string; model_id?: string; stability?: number; similarity_boost?: number; style?: number; use_speaker_boost?: boolean; speed?: number; output_directory?: string; language?: string; output_format?: string; }): Promise<any>; — Converts text into speech audio using ElevenLabs voices.


- function ElevenLabs__text_to_voice(args: { voice_description: string; text?: string; output_directory?: string; }): Promise<any>; — Creates new voice previews from a description via ElevenLabs.


- function ElevenLabs__voice_clone(args: { name: string; files: string[]; description?: string; }): Promise<any>; — Clones a voice instantly by supplying audio samples to ElevenLabs.


- function agenthub_http__call_agent(args: { name_agent: string; }): Promise<any>; — Loads and invokes a specialized agent by name within the AgentHub system.


- function agenthub_http__generate_token(): Promise<any>; — Provides information about generating new authentication tokens (deprecated helper).


- function agenthub_http__get_auth_status(): Promise<any>; — Returns authentication system status and configuration from AgentHub.


- function agenthub_http__get_rate_limit_status(args: { token: string; }): Promise<any>; — Retrieves rate limit status for a specific AgentHub token.


- function agenthub_http__manage_agent(args: { action: string; project_id?: string; agent_id?: string; name?: string; call_agent?: string; git_branch_id?: string; user_id?: string; }): Promise<any>; — Manages agent registration, assignment, and lifecycle within AgentHub projects.


- function agenthub_http__manage_connection(args: { include_details?: boolean; user_id?: string; }): Promise<any>; — Performs a health check on the AgentHub connection system.


- function agenthub_http__manage_context(args: { action: string; level?: "global" | "project" | "branch" | "task"; context_id?: string; data?: string; delegate_to?: string; delegate_data?: string; delegation_reason?: string; category?: string; importance?: "low" | "medium" | "high" | "critical"; agent?: string; content?: string; project_id?: string; git_branch_id?: string; include_inherited?: string; propagate_changes?: string; force_refresh?: string; filters?: string; user_id?: string; }): Promise<any>; — Handles hierarchical context operations with inheritance across AgentHub levels.


- function agenthub_http__manage_git_branch(args: { action: string; project_id?: string; git_branch_id?: string; git_branch_name?: string; git_branch_description?: string; agent_id?: string; user_id?: string; }): Promise<any>; — Manages Git branch lifecycle and agent assignments within AgentHub.


- function agenthub_http__manage_project(args: { action: string; project_id?: string; name?: string; description?: string; force?: string; user_id?: string; }): Promise<any>; — Performs project-level operations such as creation, updates, and health checks in AgentHub.


- function agenthub_http__manage_subtask(args: { action: string; task_id?: string; subtask_id?: string; title?: string; description?: string; status?: string; priority?: string; assignees?: string; progress_notes?: string; progress_percentage?: number; blockers?: string; challenges_overcome?: string; completion_summary?: string; completion_quality?: string; deliverables?: string; impact_on_parent?: string; insights_found?: string; next_recommendations?: string; skills_learned?: string; testing_notes?: string; user_id?: string; }): Promise<any>; — Manages creation, updates, and completion of subtasks in AgentHub.


- function agenthub_http__manage_task(args: { action: string; git_branch_id?: string; title?: string; description?: string; status?: string; priority?: string; details?: string; estimated_effort?: string; assignees?: string; labels?: string; due_date?: string; dependencies?: string; task_id?: string; include_context?: boolean; completion_summary?: string; testing_notes?: string; limit?: number; offset?: number; query?: string; dependency_id?: string; context?: string; planning_context?: string; ai_requirements?: string; auto_create_tasks?: boolean; enable_ai_breakdown?: boolean; enable_auto_subtasks?: boolean; enable_smart_assignment?: boolean; analyze_complexity?: boolean; identify_risks?: boolean; suggest_optimizations?: boolean; force_full_generation?: boolean; user_id?: string; tag?: string; sort_by?: string; sort_order?: string; available_agents?: string; requirements?: string; }): Promise<any>; — Manages task lifecycles, AI planning, and dependencies within AgentHub.


- function agenthub_http__revoke_token(args: { token: string; }): Promise<any>; — Revokes an authentication token in the AgentHub system.


- function agenthub_http__validate_token(args: { token: string; }): Promise<any>; — Validates an authentication token and returns associated user information.


- function browsermcp__browser_click(args: { element: string; ref: string; }): Promise<any>; — Performs a click action on a web page element within the browser MCP.


- function browsermcp__browser_get_console_logs(): Promise<any>; — Retrieves console logs from the active browser MCP session.


- function browsermcp__browser_go_back(): Promise<any>; — Navigates the browser MCP session back one page in history.


- function browsermcp__browser_go_forward(): Promise<any>; — Moves the browser MCP session forward in history.


- function browsermcp__browser_hover(args: { element: string; ref: string; }): Promise<any>; — Hovers over a specified element within the browser MCP.


- function browsermcp__browser_navigate(args: { url: string; }): Promise<any>; — Navigates the browser MCP session to a specified URL.


- function browsermcp__browser_press_key(args: { key: string; }): Promise<any>; — Sends a key press event to the browser MCP session.


- function browsermcp__browser_screenshot(): Promise<any>; — Captures a screenshot of the current browser MCP page.


- function browsermcp__browser_select_option(args: { element: string; ref: string; values: string[]; }): Promise<any>; — Selects options in a dropdown within the browser MCP.


- function browsermcp__browser_snapshot(): Promise<any>; — Captures an accessibility snapshot of the current browser MCP page.


- function browsermcp__browser_type(args: { element: string; ref: string; text: string; submit: boolean; }): Promise<any>; — Types text into an editable element in the browser MCP session.


- function browsermcp__browser_wait(args: { time: number; }): Promise<any>; — Waits for a specified number of seconds in the browser MCP session.


- function sequentialthinking__sequentialthinking(args: { thought: string; thoughtNumber: number; totalThoughts: number; nextThoughtNeeded: boolean; isRevision?: boolean; revisesThought?: number; branchFromThought?: number; branchId?: string; needsMoreThoughts?: boolean; }): Promise<any>; — Facilitates reflective multi-step problem solving via sequential thinking.


- function shadcn-ui-server__get-block-docs(args: { block: string; }): Promise<any>; — Retrieves documentation for a specified shadcn UI block.


- function shadcn-ui-server__get-component-docs(args: { component: string; }): Promise<any>; — Retrieves documentation for a specified shadcn UI component.


- function shadcn-ui-server__install-blocks(args: { block: string; runtime?: string; }): Promise<any>; — Installs a shadcn UI block using the specified runtime.


- function shadcn-ui-server__install-component(args: { component: string; runtime?: string; }): Promise<any>; — Installs a shadcn UI component using the specified runtime.


- function shadcn-ui-server__list-blocks(): Promise<any>; — Lists all available shadcn UI blocks.


- function shadcn-ui-server__list-components(): Promise<any>; — Lists all available shadcn UI components.
