1 - Need mcp-proxy.md working
2 - config (attention replace path-to-project and <YOUR_API_TOKEN_HERE>)

```
model = "gpt-5-codex"

[projects."/home/path-to-project/4genthub"]
trust_level = "trusted"

[mcp_servers."sequential-thinking"]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-sequential-thinking"]
env = {}

[mcp_servers.agenthub_http]
command = "mcp-proxy"  args = ["--headers", "Accept", "application/json, text/event-stream", "--headers", "Authorization", "Bearer <YOUR_API_TOKEN_HERE>", "--transport", "streamablehttp", "http://localhost:8000/mcp"]

[mcp_servers."shadcn-ui-server"]
command = "npx"
args = ["@heilgar/shadcn-ui-mcp-server"]

[mcp_servers.browsermcp]
command = "npx"
args = ["@browsermcp/mcp@latest"]

[mcp_servers.ElevenLabs]
command = "uvx"
args = ["elevenlabs-mcp"]
env = { ELEVENLABS_API_KEY = "sk_152e66d26b1eb6f1a1105474c07e962ee90b42ddf5532809" }

```

3 - Lauch codex
run codex

4 - Check connection
/mcp  
for view mcp connect

expect:

```
/mcp

🔌  MCP Tools

  • Server: ElevenLabs
    • Command: uvx elevenlabs-mcp
    • Tools: add_knowledge_base_to_agent, check_subscription, compose_music,
create_agent, create_composition_plan, create_voice_from_preview, get_agent,
get_conversation, get_voice, isolate_audio, list_agents, list_conversations,
list_models, list_phone_numbers, make_outbound_call, play_audio,
search_voice_library, search_voices, speech_to_speech, speech_to_text,
text_to_sound_effects, text_to_speech, text_to_voice, voice_clone

  • Server: browsermcp
    • Command: npx @browsermcp/mcp@latest
    • Tools: browser_click, browser_get_console_logs, browser_go_back,
browser_go_forward, browser_hover, browser_navigate, browser_press_key,
browser_screenshot, browser_select_option, browser_snapshot, browser_type,
browser_wait

  • Server: agenthub_http
    • Command: mcp-proxy --headers Accept application/
json, text/event-stream --headers Authorization Bearer
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmMGRlNGM1ZC0yYTk3LTQzMjQtYWJ
jZC05ZGFlMzkyMjc2MWUiLCJzY2vyBfVA... --transport streamablehttp http://localhost:8000/mcp
    • Tools: call_agent, generate_token, get_auth_status,
get_rate_limit_status, manage_agent, manage_connection, manage_context,
manage_git_branch, manage_project, manage_subtask, manage_task,
revoke_token, validate_token

  • Server: sequential-thinking
    • Command: npx -y @modelcontextprotocol/server-sequential-thinking
    • Tools: sequentialthinking

  • Server: shadcn-ui-server
    • Command: npx @heilgar/shadcn-ui-mcp-server
    • Tools: get-block-docs, get-component-docs, install-blocks, install-
component, list-blocks, list-components
```