#!/usr/bin/env python3
"""
Simple usage example for the GitHub MCP Client.

This script demonstrates basic usage of the create_pull_request_with_copilot tool
using the official MCP Python SDK.
"""

import asyncio
from github_mcp_client import GitHubMCPClient

## add consttants for example_owner , example_repo, example_title,  example_problem
example_owner = "eedorenko"
example_repo = "ghmcp-client"
example_title = "feat: Add example feature with Copilot"
example_problem = """
Add a simple HTTP server endpoint that returns a JSON response with the current time.

Requirements:
- Create a new file `time_server.py`
- Use Flask or FastAPI
- Add a GET /time endpoint
- Return current UTC time in ISO format
- Include basic error handling
- Add proper documentation
"""

async def example_usage():
    """Example showing how to use the GitHub MCP client programmatically."""
    
    print("GitHub MCP Client - Example Usage")
    print("=================================")
    print("Using official MCP Python SDK")
    
    try:
        # Initialize the client
        # Make sure GITHUB_TOKEN environment variable is set
        client = GitHubMCPClient()
        
        # Connect to the GitHub MCP server using MCP SDK
        print("Connecting to GitHub MCP server...")
        await client.connect_to_github_mcp_server()
        print("✅ Connected successfully!")
        
        # List available tools
        print("\nListing available tools...")
        tools = await client.list_tools()
        print(f"Found {len(tools)} tools:")
        for tool in tools:
            print(f"  • {tool['name']}: {tool['description']}")
        
        # Example: Create a pull request with Copilot
        # Replace these values with your actual repository and requirements
        print("\n" + "="*50)
        print("Example: Creating a PR with Copilot")
        print("="*50)
        
        # Note: Using the actual repository details from the current project
        print(f"Owner: {example_owner}")
        print(f"Repo: {example_repo}")
        print(f"Title: {example_title}")
        print(f"Problem: {example_problem[:100]}...")
        
        print("\nCreating pull request with Copilot...")
        result = await client.create_pull_request_with_copilot(
            owner=example_owner,
            repo=example_repo,
            problem_statement=example_problem,
            title=example_title,
            base_ref="main"  # or whatever your default branch is
        )
        
        # Check if the operation was successful
        if result.get("success", False):
            print("\n✅ Pull request creation successful!")
            if result.get("content"):
                for content_item in result["content"]:
                    if content_item.get("type") == "text":
                        print(f"📝 {content_item['text']}")
            
            if result.get("structured"):
                print("\n📊 Structured result:")
                import json
                print(json.dumps(result["structured"], indent=2))
        else:
            print(f"\n❌ Pull request creation failed!")
            error_msg = result.get("error", "Unknown error occurred")
            print(f"🚫 Error: {error_msg}")
            
            # Provide helpful suggestions
            if "not found" in error_msg.lower() or "404" in error_msg:
                print(f"\n💡 Suggestions:")
                print(f"   • Check if the repository '{example_owner}/{example_repo}' exists")
                print(f"   • Verify the owner name is correct (current: '{example_owner}')")
                print(f"   • Make sure your GitHub token has access to this repository")
                print(f"   • If it's a private repository, ensure your token has private repo permissions")
            elif "unauthorized" in error_msg.lower() or "401" in error_msg:
                print(f"\n💡 Suggestions:")
                print(f"   • Verify your GITHUB_TOKEN environment variable is set correctly")
                print(f"   • Check that your GitHub token hasn't expired")
                print(f"   • Ensure your token has the required scopes (repo, write:repo)")
                print(f"   • Try regenerating your GitHub token if needed")
        
        print(f"\n📋 Full result:")
        import json
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Always clean up
        if 'client' in locals():
            await client.close()
            print("\n🔌 Disconnected from GitHub MCP server")


if __name__ == "__main__":
    asyncio.run(example_usage())
