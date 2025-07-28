#!/usr/bin/env python3
"""
Test script for GitHub MCP Client setup and connection.

This script validates:
1. Environment variables are set
2. Dependencies are installed  
3. GitHub MCP server is accessible
4. Basic connection and tool listing works
"""

import asyncio
import os
import sys
import traceback
from typing import Optional


def check_environment() -> bool:
    """Check if environment is properly configured."""
    print("🔍 Checking environment setup...")
    
    # Check GitHub token
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("❌ GITHUB_TOKEN environment variable not set")
        print("   Set it with: export GITHUB_TOKEN='your_token_here'")
        return False
    
    print(f"✅ GITHUB_TOKEN is set (length: {len(github_token)})")
    
    # Check if token looks valid (should be a long alphanumeric string)
    if len(github_token) < 20:
        print("⚠️  Warning: GitHub token seems too short")
    
    return True


def check_dependencies() -> bool:
    """Check if required dependencies are installed."""
    print("\n🔍 Checking dependencies...")
    
    required_packages = [
        "mcp",
        "anyio", 
        "httpx",
        "dotenv"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True


async def test_github_mcp_connection(server_path: Optional[str] = None) -> bool:
    """Test connection to GitHub MCP server."""
    print("\n🔍 Testing GitHub MCP server connection...")
    
    try:
        # Import here to avoid issues if dependencies are missing
        from github_mcp_client import GitHubMCPClient
        
        client = GitHubMCPClient()
        
        # Try to connect
        if server_path:
            print(f"   Using server path: {server_path}")
        else:
            print("   Using default server path: github-mcp-server")
        
        await client.connect_to_github_mcp_server(server_path)
        print("✅ Connected to GitHub MCP server")
        
        # Try to list tools
        tools = await client.list_tools()
        print(f"✅ Listed {len(tools)} available tools:")
        
        for tool in tools[:5]:  # Show first 5 tools
            print(f"   • {tool['name']}")
        
        if len(tools) > 5:
            print(f"   ... and {len(tools) - 5} more tools")
        
        # Check for our target tool
        copilot_tool = next((t for t in tools if t['name'] == 'create_pull_request_with_copilot'), None)
        if copilot_tool:
            print("✅ Found create_pull_request_with_copilot tool!")
        else:
            print("⚠️  create_pull_request_with_copilot tool not found")
            print("   This tool may only be available in the remote GitHub MCP server")
        
        await client.close()
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import GitHub MCP client: {e}")
        return False
    except Exception as e:
        print(f"❌ Failed to connect to GitHub MCP server: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Install GitHub MCP server: https://github.com/github/github-mcp-server")
        print("   2. Make sure it's in your PATH or provide full path")
        print("   3. Check GITHUB_TOKEN has proper permissions")
        return False


async def main():
    """Run all tests."""
    print("GitHub MCP Client - Setup Test")
    print("==============================")
    
    success = True
    
    # Test environment
    if not check_environment():
        success = False
    
    # Test dependencies
    if not check_dependencies():
        success = False
    
    # If basic checks pass, test MCP connection
    if success:
        # Allow user to specify server path
        server_path = None
        if len(sys.argv) > 1:
            server_path = sys.argv[1]
            print(f"\nUsing custom server path: {server_path}")
        
        if not await test_github_mcp_connection(server_path):
            success = False
    
    print("\n" + "="*50)
    if success:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("   python github_mcp_client.py --interactive")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("GitHub MCP Client Test Script")
        print("Usage:")
        print("  python test_setup.py [server_path]")
        print("")
        print("Arguments:")
        print("  server_path    Optional path to GitHub MCP server binary")
        print("")
        print("Examples:")
        print("  python test_setup.py")
        print("  python test_setup.py /usr/local/bin/github-mcp-server")
        print("  python test_setup.py ./github-mcp-server")
    else:
        asyncio.run(main())
