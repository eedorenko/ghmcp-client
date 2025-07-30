# GitHub MCP Client - AI Coding Agent Instructions

This document provides essential context and patterns for AI coding agents working with the GitHub MCP Client codebase.

## Project Overview

This is a Python client for interacting with GitHub's Model Context Protocol (MCP) server, specifically designed to integrate with GitHub Copilot's coding agents. The client enables AI-assisted pull request creation and GitHub automation through the official MCP Python SDK.

**Core Architecture:**
- **MCP Integration**: Uses official MCP Python SDK (`mcp>=1.12.2`) for protocol communication
- **Remote Server**: Connects to `api.githubcopilot.com/mcp/` (GitHub-hosted MCP server)
- **Authentication**: Bearer token authentication via `GITHUB_TOKEN` environment variable
- **Transport**: HTTP-based streamable transport for real-time communication

## Key Files and Patterns

### `github_mcp_client.py` - Main Client Implementation

**Core Class Pattern:**
```python
class GitHubMCPClient:
    def __init__(self, github_token: Optional[str] = None)
    async def connect_to_github_mcp_server(self) -> None
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]
    async def create_pull_request_with_copilot(self, ...) -> Dict[str, Any]
```

**Essential Patterns:**
- Always use async/await for MCP operations
- Handle authentication via environment variables with fallback
- Implement comprehensive error handling with structured responses
- Use MCP SDK's `http` transport from `mcp.client.stdio`
- Always call `close()` in finally blocks for cleanup

**Authentication Pattern:**
```python
github_token = github_token or os.getenv("GITHUB_TOKEN")
if not github_token:
    raise ValueError("GITHUB_TOKEN environment variable must be set")

headers = {"Authorization": f"Bearer {github_token}"}
```

**Error Handling Pattern:**
```python
try:
    # MCP operation
    result = await self.session.call_tool(tool_name, arguments)
    return {"success": True, "content": result.content, "structured": parsed_structured}
except Exception as e:
    error_msg = str(e)
    return {"success": False, "error": error_msg}
```

### `example.py` - Usage Examples

**Key Patterns:**
- Demonstrates proper client lifecycle (connect → use → close)
- Shows error handling with user-friendly suggestions
- Includes comprehensive logging and status reporting
- Uses constants for configuration (owner, repo, title, problem)

**Standard Usage Flow:**
1. Initialize client with token
2. Connect to MCP server
3. List available tools (optional)
4. Execute tool operations
5. Handle results with success/error checking
6. Always close connection in finally block

## Environment Setup Requirements

**Python Version:** `>=3.13`

**Required Environment Variables:**
```bash
GITHUB_TOKEN=your_github_token_here  # Required for authentication
```

**Dependencies:**
- `mcp>=1.12.2` - Official MCP Python SDK
- `python-dotenv==1.0.1` - Environment variable management

## Common Development Patterns

### 1. MCP Tool Execution Pattern
```python
async def execute_mcp_tool(self, tool_name: str, **kwargs):
    """Standard pattern for executing MCP tools with error handling."""
    try:
        result = await self.call_tool(tool_name, kwargs)
        if result.get("success"):
            return result
        else:
            # Handle MCP-level errors
            raise RuntimeError(f"Tool execution failed: {result.get('error')}")
    except Exception as e:
        # Handle connection/protocol errors
        raise
```

### 2. Client Lifecycle Management
```python
async def with_github_mcp_client():
    """Context manager pattern for proper resource management."""
    client = GitHubMCPClient()
    try:
        await client.connect_to_github_mcp_server()
        yield client
    finally:
        await client.close()
```

### 3. Result Processing Pattern
```python
def process_mcp_result(result: Dict[str, Any]) -> Any:
    """Standard pattern for processing MCP tool results."""
    if not result.get("success", False):
        raise RuntimeError(f"Operation failed: {result.get('error', 'Unknown error')}")
    
    # Extract content and structured data
    content = result.get("content", [])
    structured = result.get("structured")
    
    # Process based on content type
    for item in content:
        if item.get("type") == "text":
            print(f"Text: {item['text']}")
        elif item.get("type") == "resource":
            print(f"Resource: {item['resource']}")
    
    return structured
```

## GitHub Copilot Integration Specifics

### create_pull_request_with_copilot Tool

**Required Parameters:**
- `owner`: GitHub repository owner
- `repo`: Repository name
- `problem_statement`: Detailed description of the task
- `title`: Pull request title
- `base_ref`: Target branch (usually "main" or "master")

**Best Practices:**
- Provide detailed problem statements with clear requirements
- Include specific file names, frameworks, and implementation details
- Specify error handling and documentation requirements
- Use descriptive PR titles that clearly indicate the feature/fix

**Example Problem Statement Structure:**
```
Add a [specific feature] that [does what].

Requirements:
- Create/modify file [filename]
- Use [framework/library]
- Implement [specific functionality]
- Include [error handling/testing/docs]
- Follow [coding standards/patterns]
```

## Error Handling Guidelines

### Common Error Scenarios

1. **Authentication Errors (401)**
   - Check `GITHUB_TOKEN` environment variable
   - Verify token hasn't expired
   - Ensure token has required scopes (repo, write:repo)

2. **Repository Not Found (404)**
   - Verify owner/repo names are correct
   - Check repository exists and is accessible
   - Ensure token has access to private repositories if needed

3. **MCP Connection Errors**
   - Verify network connectivity to `api.githubcopilot.com`
   - Check for firewall/proxy issues
   - Ensure MCP SDK version compatibility

4. **Tool Execution Errors**
   - Validate all required parameters are provided
   - Check parameter types match expected formats
   - Review tool documentation for specific requirements

### Error Response Structure
```python
{
    "success": False,
    "error": "Detailed error message",
    "suggestions": ["Helpful suggestion 1", "Helpful suggestion 2"]
}
```

## Development Workflow

### Setting Up Development Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export GITHUB_TOKEN="your_token_here"

# Run example
python example.py

# Run interactive CLI
python -m github_mcp_client
```

### Testing Patterns
- Always test with actual GitHub repositories you have access to
- Use descriptive test problem statements
- Verify both success and error paths
- Test token expiration and invalid credentials

### Code Style Guidelines
- Use async/await for all MCP operations
- Implement comprehensive error handling
- Include detailed docstrings for public methods
- Follow Python type hints conventions
- Use meaningful variable names (especially for repo/owner parameters)

## Architecture Notes

- **Remote MCP Server**: This client connects to GitHub's hosted MCP server, not a local one
- **HTTP Transport**: Uses streamable HTTP transport for real-time communication
- **Stateless Operations**: Each tool call is independent; no session state maintained
- **Token-Based Auth**: All authentication happens via GitHub personal access tokens

## Troubleshooting

When working with this codebase, common issues include:
1. Missing or invalid `GITHUB_TOKEN` environment variable
2. Incorrect repository owner/name combinations
3. Network connectivity issues to GitHub's MCP server
4. MCP SDK version compatibility problems
5. Insufficient GitHub token permissions

Always check the error messages in the structured response format and provide user-friendly suggestions for resolution.
