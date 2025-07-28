#!/usr/bin/env python3
"""
Setup script for GitHub MCP Client.

This script helps configure the client by:
1. Creating .env file with GitHub token
2. Installing dependencies
3. Testing the setup
"""

import os
import subprocess
import sys
from pathlib import Path


def create_env_file():
    """Create .env file with user's GitHub token."""
    print("🔧 Setting up environment configuration...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print(f"✅ .env file already exists")
        return
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return
    
    # Read example file
    with open(env_example, 'r') as f:
        example_content = f.read()
    
    print("\n📝 GitHub Token Setup")
    print("You need a GitHub personal access token to use this client.")
    print("Get one from: https://github.com/settings/tokens")
    print("Required scopes: repo, read:user, read:org")
    print()
    
    while True:
        token = input("Enter your GitHub token: ").strip()
        if token:
            break
        print("Token cannot be empty. Please try again.")
    
    # Create .env file
    env_content = example_content.replace("your_github_token_here", token)
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Created .env file")
    

def install_dependencies():
    """Install Python dependencies."""
    print("\n📦 Installing dependencies...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        # Install dependencies
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True, check=True)
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_github_mcp_server():
    """Check if GitHub MCP server is available."""
    print("\n🔍 Checking GitHub MCP server...")
    
    # Try to find github-mcp-server in PATH
    try:
        result = subprocess.run(["which", "github-mcp-server"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            server_path = result.stdout.strip()
            print(f"✅ Found GitHub MCP server at: {server_path}")
            return True
    except:
        pass
    
    # Try common installation paths
    common_paths = [
        "/usr/local/bin/github-mcp-server",
        "/opt/homebrew/bin/github-mcp-server",
        os.path.expanduser("~/.local/bin/github-mcp-server"),
        "./github-mcp-server"
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            print(f"✅ Found GitHub MCP server at: {path}")
            return True
    
    print("⚠️  GitHub MCP server not found in common locations")
    print("\n📥 Installation instructions:")
    print("1. Visit: https://github.com/github/github-mcp-server")
    print("2. Follow the installation instructions for your platform")
    print("3. Make sure the binary is in your PATH")
    return False


def run_test():
    """Run the setup test."""
    print("\n🧪 Running setup test...")
    
    try:
        result = subprocess.run([sys.executable, "test_setup.py"], 
                              check=True)
        print("✅ Setup test passed!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Setup test failed. Please check the errors above.")
        return False


def main():
    """Main setup process."""
    print("GitHub MCP Client - Setup Wizard")
    print("=================================")
    print()
    
    # Check if we're in the right directory
    if not Path("github_mcp_client.py").exists():
        print("❌ Please run this script from the ghmcp-client directory")
        sys.exit(1)
    
    success = True
    
    # Step 1: Create .env file
    create_env_file()
    
    # Step 2: Install dependencies
    if not install_dependencies():
        success = False
    
    # Step 3: Check GitHub MCP server
    if not check_github_mcp_server():
        success = False
        print("\n💡 You can still proceed, but you'll need to install the GitHub MCP server")
        print("   or provide the path manually when running the client.")
    
    # Step 4: Run test (only if dependencies installed)
    if success:
        run_test()
    
    print("\n" + "="*50)
    
    if success:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("  python github_mcp_client.py --interactive")
        print("  python example.py")
    else:
        print("⚠️  Setup completed with some issues.")
        print("Please address the warnings above, then run:")
        print("  python test_setup.py")
    
    print("\n📚 Documentation:")
    print("  README.md - Full documentation")
    print("  example.py - Usage examples")
    print("  test_setup.py - Test your setup")


if __name__ == "__main__":
    main()
