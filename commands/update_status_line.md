---
description: Update session status line data with custom key-value pairs
---

# Update Status Line Data

**Purpose**: Upsert custom key-value pairs in session extras object

## Variables (from $ARGUMENTS)
Format: `session_id key value`

| Variable | Description |
|----------|-------------|
| session_id | Unique session identifier |
| key | Key name to upsert in extras |
| value | Value to set for key |

## Workflow
1. Parse `session_id key value` from $ARGUMENTS
2. Verify `.claude/data/sessions/{session_id}.json` exists
3. Load existing JSON
4. Initialize `extras` object if missing
5. Set `extras[key] = value`
6. Save updated JSON with proper formatting
7. Confirm success

## Report
- Session ID updated
- Key modified
- Previous value (if existed)
- New value set
- Full path to session file

## Example
```
/update_status_line 4c932bd7-ee06-46e3-b26b-f32f52cc0862 project myapp
/update_status_line 4c932bd7-ee06-46e3-b26b-f32f52cc0862 status debugging
```

**Arguments**: $ARGUMENTS
