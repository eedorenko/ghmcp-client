# GitHub MCP Client

A Python client for GitHub's remote Model Context Protocol (MCP) server, focused on the `create_pull_request_with_copilot` tool for AI-assisted pull request creation.

## Overview

This client connects directly to GitHub's remote MCP server at `api.githubcopilot.com/mcp/` to leverage GitHub Copilot's coding agent for automated pull request creation. It's based on the reference implementation from the [MCP quickstart resources](https://github.com/modelcontextprotocol/quickstart-resources/tree/main/mcp-client-python).

## Features

- Connect to GitHub's remote MCP server (no local installation required)
- List available GitHub tools
- Create pull requests with GitHub Copilot coding agent assistance
- **🌟 Enhanced Terminal User Interface (TUI)** with rich formatting and interactive experience
- Interactive command-line interface (basic mode)
- Proper error handling and logging

## Prerequisites

1. **GitHub Token**: Set up a GitHub personal access token with appropriate permissions
   ```bash
   export GITHUB_TOKEN="your_github_token_here"
   ```

2. **Python Dependencies**: Install required packages
   ```bash
   pip install -r requirements.txt
   ```

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your GitHub token:
   ```bash
   export GITHUB_TOKEN="your_github_token"
   ```

## Usage

### Interactive Mode (Recommended)

# GitHub MCP Client

A Python client for GitHub's remote Model Context Protocol (MCP) server, focused on the `create_pull_request_with_copilot` tool for AI-assisted pull request creation.

## Overview

This client connects directly to GitHub's remote MCP server at `api.githubcopilot.com/mcp/` using the official [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) to leverage GitHub Copilot's coding agent for automated pull request creation. It's based on the reference implementation from the [MCP quick start resources](https://github.com/modelcontextprotocol/quickstart-resources/tree/main/mcp-client-python).

## Features

- Connect to GitHub's remote MCP server using the official MCP Python SDK
- No local installation required - connects directly to GitHub's hosted service
- List available GitHub tools
- Create pull requests with GitHub Copilot coding agent assistance
- Interactive command-line interface
- Proper error handling and logging

## Prerequisites

1. **GitHub Token**: Set up a GitHub personal access token with appropriate permissions
   ```bash
   export GITHUB_TOKEN="your_github_token_here"
   ```

2. **Python Dependencies**: Install required packages
   ```bash
   pip install -r requirements.txt
   ```

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your GitHub token:
   ```bash
   export GITHUB_TOKEN="your_github_token"
   ```

## Usage

## Usage

### Enhanced TUI Mode (Recommended) 🌟

Run the client with the beautiful, interactive Terminal User Interface:

```bash
python github_mcp_client.py --tui
```

The Enhanced TUI provides:
- 🎨 Beautiful visual interface with colors and formatting
- 📝 Interactive forms with real-time validation
- 📊 Live progress indicators during operations
- 🌈 Syntax highlighting for code and JSON
- 🛠️ Enhanced error handling with helpful suggestions
- ⚡ Professional terminal experience

### Basic Interactive Mode

Run the client in basic interactive mode for guided usage:

```bash
python github_mcp_client.py --interactive
```

This will:
1. Connect to GitHub's remote MCP server
2. List available tools
3. Guide you through creating a pull request with Copilot

### Example Usage

Run the basic example:

```bash
python github_mcp_client.py
```

### Help

View usage instructions:

```bash
python github_mcp_client.py --help
```

### Demo

See a demonstration of the Enhanced TUI features:

```bash
python demo_tui.py
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | GitHub personal access token | Yes |

## Supported Tools

The client is primarily designed for the `create_pull_request_with_copilot` tool, which:

- Takes a problem statement describing the task
- Uses GitHub Copilot to generate code changes
- Creates a pull request with the generated changes

### Tool Parameters

- `owner` (required): Repository owner
- `repo` (required): Repository name  
- `problem_statement` (required): Detailed description of the task
- `title` (required): Pull request title
- `base_ref` (optional): Base branch (defaults to repository default)

## Architecture

```
┌─────────────────┐    ┌──────────────────────────┐    ┌─────────────────┐
│ GitHub MCP      │    │ GitHub Remote MCP Server │    │ GitHub API /    │
│ Client (Python) │◄──►│ api.githubcopilot.com    │◄──►│ Copilot Service │
└─────────────────┘    └──────────────────────────┘    └─────────────────┘
```

The client connects directly to GitHub's remote MCP server, which communicates with GitHub's services including the Copilot coding agent.

## Error Handling

The client includes comprehensive error handling for:

- Connection failures to the remote MCP server
- Missing authentication tokens
- Invalid tool arguments
- GitHub API errors
- Network issues

## Logging

Logging is configured to show:
- Connection status
- Tool execution progress
- Error details
- Debug information (when enabled)

## Troubleshooting

### Connection Issues

1. **"Failed to connect to GitHub MCP server"**
   - Ensure GITHUB_TOKEN environment variable is set
   - Verify your GitHub token has the necessary permissions
   - Check your internet connection

2. **"create_pull_request_with_copilot tool not found"**
   - This tool is available on GitHub's remote MCP server
   - Check available tools in the output
   - Ensure you're connecting to the remote server

3. **Authentication errors**
   - Verify your GitHub token has the necessary permissions
   - Check that the token hasn't expired
   - Ensure the token has access to the target repository

## Development

### Project Structure

```
ghmcp-client/
├── github_mcp_client.py    # Main client implementation
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── .env.example          # Environment variable template
```

### Dependencies

- `mcp`: Official Model Context Protocol Python SDK
- `python-dotenv`: Environment variable loading
- `rich`: Enhanced terminal interface and formatting (for TUI mode)

## References

- [GitHub MCP Server](https://github.com/github/github-mcp-server)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Quick Start Resources](https://github.com/modelcontextprotocol/quickstart-resources)
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)

## License

MIT License - see the original MCP quick start resources for license details.
