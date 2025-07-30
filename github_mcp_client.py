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
import sys
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
                error_messages = []
                
                # Extract error messages from content
                for content_item in result.content:
                    if hasattr(content_item, 'text'):
                        error_text = content_item.text
                        error_messages.append(error_text)
                        
                        # Parse common GitHub API errors for prettier messages
                        if "401: Unauthorized" in error_text:
                            result_dict["error"] = "GitHub API returned 401 Unauthorized. Please check:\n- Your GitHub token is valid and not expired\n- Token has the required permissions for this repository\n- Repository exists and you have access to it"
                        elif "404: Not Found" in error_text:
                            result_dict["error"] = f"Repository '{arguments.get('owner', 'unknown')}/{arguments.get('repo', 'unknown')}' not found. Please verify:\n- Repository name is spelled correctly\n- Repository exists\n- You have access to this repository"
                        elif "403: Forbidden" in error_text:
                            result_dict["error"] = "Access forbidden. Your GitHub token may not have the required permissions for this operation."
                        else:
                            result_dict["error"] = error_text
                        break
                
                if not error_messages:
                    result_dict["error"] = "Tool execution failed with unknown error"
                    
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
            # Return a formatted error instead of re-raising
            return {
                "success": False,
                "error": f"Failed to execute tool '{tool_name}': {str(e)}",
                "content": []
            }
    
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


async def main():
    """Main entry point."""
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        await interactive_cli()
    elif len(sys.argv) > 1 and sys.argv[1] == "--tui":
        # Enhanced TUI mode
        try:
            from rich_cli import run_tui
            await run_tui()
        except ImportError as e:
            print("❌ TUI mode requires the 'rich' library.")
            print("Install it with: pip install rich>=13.7.0")
            print(f"Error: {e}")
        except Exception as e:
            print(f"❌ Error launching TUI: {e}")
    elif len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("GitHub MCP Client")
        print("================")
        print()
        print("Usage:")
        print("  python github_mcp_client.py --tui           # Enhanced TUI mode (recommended)")
        print("  python github_mcp_client.py --interactive   # Basic interactive mode")
        print("  python github_mcp_client.py --help         # Show this help")
        print("  python github_mcp_client.py                # Example usage")
        print()
        print("Modes:")
        print("  --tui          Enhanced Terminal User Interface with rich formatting")
        print("  --interactive  Basic command-line interface")
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
                print("\nTo use the tool, you have several options:")
                print("🌟 python github_mcp_client.py --tui          # Enhanced TUI (recommended)")
                print("💬 python github_mcp_client.py --interactive  # Basic interactive mode")
                print("📝 See example.py for programmatic usage")
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
