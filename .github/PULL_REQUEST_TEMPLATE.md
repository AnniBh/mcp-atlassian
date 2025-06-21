## Summary
This PR introduces comprehensive logging for tool invocations in the Jira MCP server, with the goal of improving observability, debugging, and auditability.

## Key Changes

### 1. Tool Invocation Logging
- Added a new async function `log_tool_invocation` in `src/mcp_atlassian/utils/logging.py`.
- This function logs each tool invocation, including:
  - Timestamp (UTC ISO8601)
  - Tool name
  - User details (from Jira)
  - Response data
  - Execution time (ms)
- The log is sent as a POST request to an n8n workflow endpoint, configurable via the `N8N_LOG_ENDPOINT` environment variable.
- If the endpoint is not set, a warning is logged.

### 2. Integration in Jira MCP Server
- Updated `src/mcp_atlassian/servers/jira.py`:
  - Wrapped all tool endpoints to measure execution time and call `log_tool_invocation` after each tool completes (success or failure).
  - Ensured logging occurs in `finally` blocks for reliability.
  - Refactored endpoint logic to support this pattern.

### 3. Minor Documentation/Config Updates
- Updated `CONTRIBUTING.md` to use the correct fork/remote URLs for this repository.

## Motivation
- Enables external workflow automation and monitoring of tool usage.
- Provides detailed audit trails for each tool call, including user and timing information.
- Supports debugging and performance analysis.

## How to Use
- Set the `N8N_LOG_ENDPOINT` environment variable to your n8n workflow endpoint to enable logging.
- No breaking changes to existing tool APIs.

---

**Please review the changes and provide feedback.**

Closes # (if applicable)

---

Files changed:
- `src/mcp_atlassian/servers/jira.py`
- `src/mcp_atlassian/utils/logging.py`
- `CONTRIBUTING.md`

For more details, see the code diff in this PR.