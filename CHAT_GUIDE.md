# GitHub MCP Chat Mode Guide

## Overview

The GitHub MCP Client now includes a new **Chat Mode** that provides a conversational interface for interacting with GitHub's Model Context Protocol (MCP) server. This mode allows for natural language interactions, making it easier and more intuitive to work with GitHub Copilot and other MCP tools.

## Starting Chat Mode

```bash
python github_mcp_client.py --chat
```

## Features

### 🗣️ Natural Language Conversations
- Chat naturally about GitHub, development, and coding
- Ask questions and get helpful responses
- No need to remember complex command syntax

### 📝 Chat Commands
- `/help` - Show available commands and usage
- `/tools` - List available MCP tools (requires connection)
- `/history` - Show recent conversation history
- `/clear` - Clear conversation history
- `/context [json]` - Set or view conversation context
- `/quit` or `/exit` - Exit chat mode

### 🔗 Tool Integration
- Request tool execution through natural language
- "create a pull request" - Get guided PR creation
- "list tools" - Show available GitHub MCP tools
- Seamless integration with existing MCP functionality

### 🧠 Context Management
- Maintains conversation history
- Tracks context across interactions
- Smart parsing of user intent

## Example Conversations

### Basic Interaction
```
You: hello
🤖 Assistant: Hello! I'm your GitHub MCP assistant. I can help you:
• Create AI-assisted pull requests
• Access GitHub tools via MCP
• Answer questions about GitHub and development

What would you like to work on today?
```

### Tool Requests
```
You: create a pull request
🤖 Assistant: To create a pull request, I need some information:

Please provide:
1. Repository owner
2. Repository name  
3. Pull request title
4. Problem statement (what you want to implement)
5. Base branch (optional)

You can provide this in natural language or use the format:
"Create PR for owner/repo with title 'Your Title' to implement: Your problem statement"
```

### Command Usage
```
You: /help
🤖 Assistant: 
GitHub MCP Chat Commands:
========================

/help                    - Show this help message
/tools                   - List available MCP tools
/history                 - Show recent chat history
/clear                   - Clear chat history
/context [json]          - Set/view conversation context
/quit or /exit           - Exit chat mode

Tool Requests:
- "create a pull request" - Guide you through PR creation
- "list tools"           - Show available tools
- "help"                 - General assistance

You can also have natural conversations about GitHub, coding, or ask questions!
```

## Offline Mode

Chat mode can work even without a connection to the GitHub MCP server:

- Provides helpful guidance and information
- Explains MCP concepts and GitHub workflows
- Offers development advice and best practices
- Gracefully handles connection issues

## Technical Features

### Conversation History
- Automatically tracks last 20 messages
- Provides context for follow-up questions
- Can be cleared with `/clear` command

### Smart Intent Recognition
- Parses natural language for tool requests
- Recognizes common patterns and keywords
- Provides appropriate responses based on context

### Error Handling
- Graceful handling of connection failures
- Clear error messages and guidance
- Fallback to offline mode when needed

## Integration with Existing Features

Chat mode seamlessly integrates with all existing GitHub MCP Client features:

- **Tool Execution**: Call any available MCP tool through conversation
- **PR Creation**: Natural language interface for `create_pull_request_with_copilot`
- **Connection Management**: Same authentication and connection logic
- **Error Handling**: Consistent error handling and logging

## Benefits

1. **Lower Learning Curve**: No need to learn command syntax
2. **Natural Interaction**: Chat like you would with a human assistant
3. **Context Awareness**: Maintains conversation state and history
4. **Flexible Input**: Multiple ways to request the same action
5. **Progressive Disclosure**: Get more information as needed
6. **Offline Capability**: Useful even without server connection

## Getting Started

1. Set your GitHub token:
   ```bash
   export GITHUB_TOKEN="your_github_token_here"
   ```

2. Start chat mode:
   ```bash
   python github_mcp_client.py --chat
   ```

3. Try these first commands:
   - Say "hello" to get started
   - Type "/help" to see available commands
   - Ask "what can you do?" to learn about capabilities
   - Request "create a pull request" to try the main feature

The chat mode makes the GitHub MCP Client more accessible and user-friendly while maintaining all the powerful features of the original tool-focused interface.