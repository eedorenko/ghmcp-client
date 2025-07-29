#!/bin/bash

# Hello World with GitHub MCP Client
# A simple shell script demonstrating basic functionality

set -e  # Exit on any error

# Script information
SCRIPT_NAME="Hello World - GitHub MCP Client"
SCRIPT_VERSION="1.0.0"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to print banner
print_banner() {
    echo ""
    print_color "$BLUE" "╭─────────────────────────────────────╮"
    print_color "$BLUE" "│     Hello World - GitHub MCP       │"
    print_color "$BLUE" "│           Shell Client              │"
    print_color "$BLUE" "╰─────────────────────────────────────╯"
    echo ""
}

# Function to check prerequisites
check_prerequisites() {
    print_color "$YELLOW" "🔍 Checking prerequisites..."
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        print_color "$RED" "❌ Python 3 is required but not installed"
        exit 1
    fi
    
    # Check if required Python files exist
    if [ ! -f "github_mcp_client.py" ]; then
        print_color "$RED" "❌ github_mcp_client.py not found"
        exit 1
    fi
    
    if [ ! -f "requirements.txt" ]; then
        print_color "$RED" "❌ requirements.txt not found"
        exit 1
    fi
    
    # Check if GITHUB_TOKEN is set
    if [ -z "$GITHUB_TOKEN" ]; then
        print_color "$YELLOW" "⚠️  GITHUB_TOKEN environment variable not set"
        print_color "$YELLOW" "   You can set it with: export GITHUB_TOKEN='your_token_here'"
    else
        print_color "$GREEN" "✅ GITHUB_TOKEN is set"
    fi
    
    print_color "$GREEN" "✅ Prerequisites check completed"
}

# Function to demonstrate basic functionality
demo_basic() {
    print_color "$YELLOW" "🚀 Running basic Hello World demo..."
    
    echo ""
    print_color "$GREEN" "Hello, World!"
    print_color "$GREEN" "Welcome to the GitHub MCP Client Shell Interface"
    echo ""
    
    print_color "$BLUE" "This shell script demonstrates:"
    echo "  • Shell script integration with GitHub MCP Client"
    echo "  • Basic environment validation"
    echo "  • Colorized output for better user experience"
    echo "  • Error handling and status reporting"
    echo ""
}

# Function to show client information
show_client_info() {
    print_color "$YELLOW" "📋 GitHub MCP Client Information..."
    
    if command -v python3 &> /dev/null; then
        print_color "$BLUE" "Python version: $(python3 --version)"
    fi
    
    echo ""
    print_color "$BLUE" "Available client commands:"
    echo "  • python3 github_mcp_client.py --help"
    echo "  • python3 github_mcp_client.py --interactive"
    echo "  • python3 github_mcp_client.py"
    echo ""
    
    if [ -f "Makefile" ]; then
        print_color "$BLUE" "Available make targets:"
        echo "  • make help      - Show available commands"
        echo "  • make setup     - Run setup wizard"
        echo "  • make test      - Test setup and connection"
        echo "  • make interactive - Run in interactive mode"
        echo ""
    fi
}

# Function to run interactive client (if token is available)
run_interactive_demo() {
    if [ -n "$GITHUB_TOKEN" ]; then
        print_color "$YELLOW" "🎯 Would you like to run the interactive GitHub MCP client? (y/N)"
        read -r response
        
        if [[ "$response" =~ ^[Yy]$ ]]; then
            print_color "$GREEN" "🚀 Starting interactive GitHub MCP client..."
            python3 github_mcp_client.py --interactive
        else
            print_color "$BLUE" "ℹ️  Skipping interactive demo"
        fi
    else
        print_color "$YELLOW" "ℹ️  Set GITHUB_TOKEN to enable interactive demo"
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -v, --version  Show version information"
    echo "  -i, --info     Show client information only"
    echo "  -d, --demo     Run demo without interactive client"
    echo ""
    echo "Environment Variables:"
    echo "  GITHUB_TOKEN   GitHub personal access token (optional for basic demo)"
    echo ""
}

# Function to show version
show_version() {
    echo "$SCRIPT_NAME v$SCRIPT_VERSION"
}

# Main function
main() {
    case "${1:-}" in
        -h|--help)
            show_usage
            exit 0
            ;;
        -v|--version)
            show_version
            exit 0
            ;;
        -i|--info)
            print_banner
            check_prerequisites
            show_client_info
            exit 0
            ;;
        -d|--demo)
            print_banner
            check_prerequisites
            demo_basic
            show_client_info
            exit 0
            ;;
        "")
            # Default behavior - full demo
            print_banner
            check_prerequisites
            demo_basic
            show_client_info
            run_interactive_demo
            ;;
        *)
            print_color "$RED" "❌ Unknown option: $1"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"