"""
MCP Post Action Hints Module

This module provides post-action hints for MCP tools to improve user experience.
"""

def generate_post_action_hints(tool_name: str, tool_input: dict, result: dict = None) -> str:
    """
    Generate helpful hints after a tool action is completed.

    Args:
        tool_name: Name of the MCP tool that was used
        tool_input: Input parameters passed to the tool
        result: Result returned by the tool (optional)

    Returns:
        String containing helpful hints for the user
    """
    if tool_name == "Read":
        return "💡 File read successfully. Consider using Edit if you need to make changes."
    elif tool_name == "Write":
        return "✅ File written successfully. Remember to test your changes."
    elif tool_name == "Edit":
        return "🔧 File edited successfully. Verify the changes meet your requirements."
    elif tool_name == "Bash":
        return "🖥️ Command executed. Check the output for any errors or warnings."
    else:
        return "✅ Operation completed successfully."