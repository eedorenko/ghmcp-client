#!/usr/bin/env python3
"""
GitHub MCP Client

A client implementation for GitHub's Model Context Protocol (MCP) remote server,
focused on the create_pull_request_with_copilot tool for AI-assisted pull request creation.

Based on the reference implementation from:
https://github.com/modelcontextprotocol/quickstart-resources/tree/main/mcp-client-python
"""

import asyncio
import json
import logging
import os
import re
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitHubMCPClient:
    """Client for GitHub's remote MCP server with focus on Copilot-assisted PR creation."""
    
    def __init__(self, auth_token: Optional[str] = None):
        """
        Initialize GitHub MCP Client.
        
        Args:
            auth_token: GitHub authentication token. If not provided, will use GITHUB_TOKEN env var.
        """
        self.auth_token = auth_token or os.getenv("GITHUB_TOKEN")
        if not self.auth_token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN environment variable or pass auth_token.")
        
        self.remote_url = "https://api.githubcopilot.com/mcp/"
        self.session: Optional[ClientSession] = None
        self.available_tools: List[Dict[str, Any]] = []
        self.chat_history: List[Dict[str, str]] = []
        self.chat_context: Dict[str, Any] = {}
        
    async def connect_to_github_mcp_server(self) -> None:
        """
        Connect to the remote GitHub MCP server using MCP Python SDK.
        """
        try:
            logger.info(f"Connecting to remote GitHub MCP server at {self.remote_url}")
            
            # Set up authentication headers
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "User-Agent": "GitHub-MCP-Client/1.0"
            }
            
            # Connect using MCP SDK's streamable HTTP client  
            self._transport_context = streamablehttp_client(
                self.remote_url,
                headers=headers
            )
            
            # Initialize the client session
            read_stream, write_stream, _ = await self._transport_context.__aenter__()
            
            self.session = ClientSession(read_stream, write_stream)
            await self.session.__aenter__()
            
            # Initialize the MCP connection
            await self.session.initialize()
            
            logger.info("Connected to remote GitHub MCP server successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to remote GitHub MCP server: {e}")
            raise
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from the remote GitHub MCP server."""
        if not self.session:
            raise RuntimeError("Not connected to remote server. Call connect_to_github_mcp_server() first.")
        
        try:
            # Use MCP SDK to list tools
            tools_result = await self.session.list_tools()
            
            tools = []
            for tool in tools_result.tools:
                tool_dict = {
                    "name": tool.name,
                    "description": tool.description or "",
                    "inputSchema": tool.inputSchema or {}
                }
                tools.append(tool_dict)
            
            self.available_tools = tools
            logger.info(f"Listed {len(tools)} available tools from remote server")
            return tools
            
        except Exception as e:
            logger.error(f"Failed to list tools from remote server: {e}")
            raise
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the remote GitHub MCP server."""
        if not self.session:
            raise RuntimeError("Not connected to remote server. Call connect_to_github_mcp_server() first.")
        
        try:
            logger.info(f"Calling tool '{tool_name}' on remote server with arguments: {json.dumps(arguments, indent=2)}")
            
            # Use MCP SDK to call the tool
            result = await self.session.call_tool(tool_name, arguments)
            
            logger.info(f"Tool '{tool_name}' executed successfully on remote server")
            
            # Convert MCP result to dictionary format for compatibility
            result_dict = {
                "success": not result.isError,
                "content": []
            }
            
            if result.isError:
                result_dict["error"] = "Tool execution failed"
                # Extract error messages from content
                for content_item in result.content:
                    if hasattr(content_item, 'text'):
                        result_dict["error"] = content_item.text
                        break
            else:
                # Process content items
                for content_item in result.content:
                    if hasattr(content_item, 'text'):
                        result_dict["content"].append({
                            "type": "text",
                            "text": content_item.text
                        })
                    else:
                        result_dict["content"].append({
                            "type": "unknown",
                            "data": str(content_item)
                        })
            
            # Add structured content if available
            if hasattr(result, 'structuredContent') and result.structuredContent:
                result_dict["structured"] = result.structuredContent
            
            return result_dict
            
        except Exception as e:
            logger.error(f"Failed to call tool '{tool_name}' on remote server: {e}")
            raise
    
    async def create_pull_request_with_copilot(
        self,
        owner: str,
        repo: str,
        problem_statement: str,
        title: str,
        base_ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a pull request with GitHub Copilot coding agent assistance.
        
        Args:
            owner: Repository owner
            repo: Repository name
            problem_statement: Detailed description of the task
            title: Pull request title
            base_ref: Base branch (optional, defaults to repo default)
            
        Returns:
            Result of the Copilot-assisted PR creation
        """
        arguments = {
            "owner": owner,
            "repo": repo,
            "problem_statement": problem_statement,
            "title": title
        }
        
        if base_ref:
            arguments["base_ref"] = base_ref
        
        return await self.call_tool("create_pull_request_with_copilot", arguments)
    
    async def close(self) -> None:
        """Close the connection to the GitHub MCP server."""
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
                self.session = None
                logger.info("Closed MCP session")
            
            if hasattr(self, '_transport_context') and self._transport_context:
                await self._transport_context.__aexit__(None, None, None)
                logger.info("Closed connection to remote GitHub MCP server")
                
        except Exception as e:
            logger.error(f"Error closing connection: {e}")
    
    def add_to_chat_history(self, role: str, content: str) -> None:
        """Add a message to the chat history."""
        self.chat_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 20 messages to avoid memory issues
        if len(self.chat_history) > 20:
            self.chat_history = self.chat_history[-20:]
    
    def get_chat_history_summary(self) -> str:
        """Get a summary of recent chat history for context."""
        if not self.chat_history:
            return "No previous conversation."
        
        # Return last 5 messages as context
        recent_messages = self.chat_history[-5:]
        summary = "Recent conversation:\n"
        for msg in recent_messages:
            summary += f"{msg['role']}: {msg['content'][:100]}{'...' if len(msg['content']) > 100 else ''}\n"
        return summary
    
    def parse_chat_command(self, user_input: str) -> Dict[str, Any]:
        """Parse user input for chat commands."""
        user_input = user_input.strip()
        
        # Chat commands start with /
        if user_input.startswith('/'):
            parts = user_input[1:].split(' ', 1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            return {
                "type": "command",
                "command": command,
                "args": args
            }
        
        # Check if user is asking for tool execution
        tool_patterns = [
            (r"create.*pull.*request|make.*pr|new.*pr", "create_pr"),
            (r"list.*tools|show.*tools|what.*tools", "list_tools"),
            (r"help|assistance", "help"),
        ]
        
        user_input_lower = user_input.lower()
        for pattern, action in tool_patterns:
            if re.search(pattern, user_input_lower):
                return {
                    "type": "tool_request",
                    "action": action,
                    "original_input": user_input
                }
        
        # Default to conversation
        return {
            "type": "conversation",
            "content": user_input
        }
    
    async def handle_chat_command(self, command: str, args: str) -> str:
        """Handle chat commands."""
        if command == "help":
            return self._get_chat_help()
        elif command == "tools":
            if not self.session:
                return "Sorry, I can't list tools without a connection to the GitHub MCP server. Please check your GITHUB_TOKEN and connection."
            try:
                tools = await self.list_tools()
                tools_list = "\n".join([f"  • {tool['name']}: {tool['description']}" for tool in tools])
                return f"Available tools:\n{tools_list}"
            except Exception as e:
                return f"Error listing tools: {e}"
        elif command == "history":
            return self.get_chat_history_summary()
        elif command == "clear":
            self.chat_history.clear()
            return "Chat history cleared."
        elif command == "context":
            if args:
                # Set context
                try:
                    context_data = json.loads(args)
                    self.chat_context.update(context_data)
                    return f"Context updated: {list(context_data.keys())}"
                except json.JSONDecodeError:
                    return "Invalid JSON format for context. Use: /context {\"key\": \"value\"}"
            else:
                # Show current context
                return f"Current context: {json.dumps(self.chat_context, indent=2)}"
        elif command == "quit" or command == "exit":
            return "exit_chat"
        else:
            return f"Unknown command: /{command}. Type /help for available commands."
    
    def _get_chat_help(self) -> str:
        """Get help text for chat mode."""
        return """
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
        """
    
    async def process_chat_input(self, user_input: str) -> str:
        """Process user input in chat mode and return response."""
        # Add user message to history
        self.add_to_chat_history("user", user_input)
        
        # Parse the input
        parsed = self.parse_chat_command(user_input)
        
        try:
            if parsed["type"] == "command":
                response = await self.handle_chat_command(parsed["command"], parsed["args"])
            elif parsed["type"] == "tool_request":
                response = await self._handle_tool_request(parsed)
            else:
                # Regular conversation - provide helpful response
                response = self._generate_conversation_response(parsed["content"])
            
            # Add assistant response to history
            if response != "exit_chat":
                self.add_to_chat_history("assistant", response)
            
            return response
            
        except Exception as e:
            error_msg = f"Error processing request: {e}"
            self.add_to_chat_history("assistant", error_msg)
            return error_msg
    
    async def _handle_tool_request(self, parsed: Dict[str, Any]) -> str:
        """Handle tool execution requests from chat."""
        action = parsed["action"]
        
        if action == "list_tools":
            if not self.session:
                return "Sorry, I can't list tools without a connection to the GitHub MCP server. Please check your GITHUB_TOKEN and connection."
            
            try:
                tools = await self.list_tools()
                return f"Available tools ({len(tools)}):\n" + "\n".join([f"  • {t['name']}: {t['description']}" for t in tools])
            except Exception as e:
                return f"Error listing tools: {e}"
        
        elif action == "create_pr":
            if not self.session:
                return """I'd love to help you create a pull request, but I need a connection to the GitHub MCP server.

Please:
1. Set your GITHUB_TOKEN environment variable
2. Restart the chat mode
3. Then I can help you create PRs with GitHub Copilot!

For now, I can provide guidance on PR creation best practices if you'd like."""
            
            return """To create a pull request, I need some information:
            
Please provide:
1. Repository owner
2. Repository name  
3. Pull request title
4. Problem statement (what you want to implement)
5. Base branch (optional)

You can provide this in natural language or use the format:
"Create PR for owner/repo with title 'Your Title' to implement: Your problem statement"
            """
        
        elif action == "help":
            return self._get_chat_help()
        
        return "I understand you want to use a tool, but I need more specific information."
    
    def _generate_conversation_response(self, content: str) -> str:
        """Generate a conversational response."""
        content_lower = content.lower()
        
        # Context-aware responses
        if "github" in content_lower and "mcp" in content_lower:
            return """I'm a GitHub MCP (Model Context Protocol) client! I can help you:

• Connect to GitHub's MCP server
• Create pull requests with AI assistance
• List and use available GitHub tools
• Provide information about MCP and GitHub integration

What would you like to know or do?"""
        
        elif "pull request" in content_lower or "pr" in content_lower:
            return """I can help you create pull requests with GitHub Copilot assistance! 

To create a PR, I need:
- Repository (owner/name)
- Title for the PR
- Problem statement describing what to implement

Would you like to start creating a pull request?"""
        
        elif "tools" in content_lower or "what can you do" in content_lower:
            return """I can access GitHub's MCP tools! Use '/tools' to see what's available.

Common things I can help with:
• Creating pull requests with AI
• Listing repository information
• GitHub API interactions
• Copilot-assisted coding

What specific task would you like help with?"""
        
        elif any(greeting in content_lower for greeting in ["hello", "hi", "hey"]):
            return """Hello! I'm your GitHub MCP assistant. I can help you:

• Create AI-assisted pull requests
• Access GitHub tools via MCP
• Answer questions about GitHub and development

What would you like to work on today?"""
        
        else:
            # Generic helpful response
            return f"""I'm here to help with GitHub and MCP-related tasks. You mentioned: "{content[:100]}{'...' if len(content) > 100 else ''}"

I can help you:
• Create pull requests (/tools to see available options)
• Access GitHub via MCP protocol
• Answer questions about development

Type /help for commands or ask me anything specific!"""


async def interactive_cli():
    """Interactive command-line interface for the GitHub MCP client."""
    print("GitHub MCP Client - Copilot PR Creator")
    print("=====================================")
    print()
    print("Connecting to GitHub's remote MCP server...")
    print()
    
    # Initialize client
    try:
        client = GitHubMCPClient()
        
        print(f"🌐 Connecting to remote GitHub MCP server...")
        print("This connects directly to GitHub's hosted MCP server")
        await client.connect_to_github_mcp_server()
        
        print("✅ Connected to GitHub MCP server")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure GITHUB_TOKEN environment variable is set")
        print("2. Verify your token has the necessary permissions")
        print("3. Check your internet connection")
        return
    
    try:
        # List available tools
        tools = await client.list_tools()
        print(f"\n📋 Available tools: {len(tools)}")
        for tool in tools:
            print(f"  • {tool['name']}: {tool['description']}")
        
        # Check if our target tool is available
        copilot_tool = next((t for t in tools if t['name'] == 'create_pull_request_with_copilot'), None)
        if not copilot_tool:
            print("\n⚠️  Warning: create_pull_request_with_copilot tool not found.")
            print("This tool may only be available in the remote GitHub MCP server.")
            print("Available tools are listed above.")
            
            # Allow user to proceed with any available tool
            tool_name = input("\nEnter tool name to use (or 'quit' to exit): ").strip()
            if tool_name.lower() == 'quit':
                return
        else:
            tool_name = 'create_pull_request_with_copilot'
        
        print(f"\n" + "="*50)
        print(f"Using tool: {tool_name}")
        print("="*50)
        
        # Get user input based on the tool
        if tool_name == 'create_pull_request_with_copilot':
            # Get input for Copilot PR creation
            owner = input("Repository owner: ").strip()
            if not owner:
                print("❌ Repository owner is required")
                return
            
            repo = input("Repository name: ").strip()
            if not repo:
                print("❌ Repository name is required")
                return
            
            title = input("Pull request title: ").strip()
            if not title:
                print("❌ Pull request title is required")
                return
            
            print("\nProblem statement (detailed description of the task):")
            print("(Enter multiple lines, press Ctrl+D when done)")
            problem_lines = []
            try:
                while True:
                    line = input()
                    problem_lines.append(line)
            except EOFError:
                pass
            
            problem_statement = "\n".join(problem_lines).strip()
            if not problem_statement:
                print("❌ Problem statement is required")
                return
            
            base_ref = input("Base branch (optional, press Enter for default): ").strip()
            
            print(f"\n🚀 Creating pull request with Copilot...")
            print(f"   Owner: {owner}")
            print(f"   Repo: {repo}")
            print(f"   Title: {title}")
            print(f"   Base ref: {base_ref or 'default'}")
            print(f"   Problem: {problem_statement[:100]}{'...' if len(problem_statement) > 100 else ''}")
            
            # Create the PR with Copilot
            result = await client.create_pull_request_with_copilot(
                owner=owner,
                repo=repo,
                problem_statement=problem_statement,
                title=title,
                base_ref=base_ref if base_ref else None
            )
        else:
            # Generic tool execution
            print(f"\nExecuting tool: {tool_name}")
            print("Enter arguments as JSON (press Ctrl+D when done):")
            
            args_lines = []
            try:
                while True:
                    line = input()
                    args_lines.append(line)
            except EOFError:
                pass
            
            args_text = "\n".join(args_lines).strip()
            try:
                arguments = json.loads(args_text) if args_text else {}
            except json.JSONDecodeError:
                print("❌ Invalid JSON format for arguments")
                return
            
            result = await client.call_tool(tool_name, arguments)
        
        print("\n✅ Result:")
        print(json.dumps(result, indent=2))
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()


async def chat_mode():
    """Interactive chat mode for the GitHub MCP client."""
    print("GitHub MCP Chat Mode")
    print("===================")
    print("💬 Welcome! I'm your GitHub MCP assistant.")
    print("   Type /help for commands or just chat naturally!")
    print("   Type /quit to exit.")
    print()
    
    # Initialize client
    client = None
    try:
        client = GitHubMCPClient()
        
        print("🌐 Connecting to GitHub MCP server...")
        await client.connect_to_github_mcp_server()
        print("✅ Connected! Ready to chat.")
        print()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nI can still chat with you about GitHub and development,")
        print("but I won't be able to execute tools without a connection.")
        print("Make sure GITHUB_TOKEN is set for full functionality.")
        print()
        
        # Create a client without connection for basic chat
        if client:
            try:
                await client.close()
            except:
                pass
        
        try:
            client = GitHubMCPClient()
            client.session = None  # Indicate no connection
        except Exception as e2:
            print(f"❌ Cannot initialize client: {e2}")
            return
    
    # Chat loop
    try:
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Process the input
                response = await client.process_chat_input(user_input)
                
                # Check for exit
                if response == "exit_chat":
                    print("\n👋 Goodbye! Thanks for chatting!")
                    break
                
                # Display response
                print(f"\n🤖 Assistant: {response}\n")
                
            except EOFError:
                print("\n\n👋 Goodbye!")
                break
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
                
    except Exception as e:
        print(f"\n❌ Chat error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if client and client.session:
            try:
                await client.close()
            except:
                pass


async def main():
    """Main entry point."""
    
    if len(sys.argv) > 1 and sys.argv[1] == "--chat":
        await chat_mode()
    elif len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        await interactive_cli()
    elif len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("GitHub MCP Client")
        print("================")
        print()
        print("Usage:")
        print("  python github_mcp_client.py --chat          # Chat mode (NEW!)")
        print("  python github_mcp_client.py --interactive    # Interactive mode")
        print("  python github_mcp_client.py --help          # Show this help")
        print("  python github_mcp_client.py                 # Example usage")
        print()
        print("Chat Mode:")
        print("  New conversational interface with natural language")
        print("  - Chat naturally about GitHub and development")
        print("  - Use commands like /help, /tools, /quit")
        print("  - Request tool execution through conversation")
        print()
        print("Connection:")
        print("  Connects to GitHub's remote MCP server at api.githubcopilot.com/mcp/")
        print("  - No installation required")
        print("  - Requires GITHUB_TOKEN environment variable")
        print()
        print("Environment Variables:")
        print("  GITHUB_TOKEN       # GitHub token with appropriate permissions")
        print()
        print("Prerequisites:")
        print("  1. GitHub token with appropriate permissions")
        print("  2. Install Python dependencies: pip install -r requirements.txt")
        return
    else:
        # Example usage
        print("GitHub MCP Client Example")
        print("========================")
        print()
        print("This example demonstrates connecting to the GitHub MCP remote server")
        print("and listing available tools.")
        print()
        print("💡 NEW: Try the chat mode with: python github_mcp_client.py --chat")
        print()
        
        try:
            client = GitHubMCPClient()
            
            # Try to connect to remote server
            try:
                print("🌐 Connecting to GitHub MCP remote server...")
                await client.connect_to_github_mcp_server()
                print("✅ Connected to GitHub MCP remote server")
            except Exception as e:
                print(f"❌ Failed to connect to GitHub MCP server: {e}")
                print()
                print("Connection failed. Make sure you have:")
                print("1. GITHUB_TOKEN environment variable set")
                print("2. Valid GitHub token with proper permissions") 
                print("3. Internet connection")
                print()
                print("Run with --interactive flag for guided setup")
                return
            
            # List tools
            tools = await client.list_tools()
            print(f"\n📋 Available tools: {len(tools)}")
            for tool in tools:
                print(f"  • {tool['name']}: {tool['description']}")
            
            # Check for our target tool
            copilot_tool = next((t for t in tools if t['name'] == 'create_pull_request_with_copilot'), None)
            if copilot_tool:
                print(f"\n✅ Found create_pull_request_with_copilot tool!")
                print("\nTo use the tool interactively, run:")
                print("python github_mcp_client.py --interactive")
            else:
                print(f"\n⚠️  create_pull_request_with_copilot tool not found.")
                print("Available tools are listed above.")
            
            await client.close()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
