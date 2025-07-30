#!/usr/bin/env python3
"""
Enhanced Terminal User Interface for GitHub MCP Client

A beautiful, interactive TUI using the Rich library that provides:
- Interactive forms with validation
- Real-time progress indicators  
- Syntax-highlighted previews
- Beautiful error displays
- Live status updates
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.tree import Tree
from rich.columns import Columns
from rich.align import Align
from rich import box
from rich.rule import Rule

from github_mcp_client import GitHubMCPClient


class GitHubMCPTUI:
    """Enhanced Terminal User Interface for GitHub MCP Client."""
    
    def __init__(self):
        self.console = Console()
        self.client: Optional[GitHubMCPClient] = None
        self.tools: List[Dict[str, Any]] = []
        
    def print_header(self):
        """Display the application header with styling."""
        header_text = Text("GitHub MCP Client", style="bold cyan")
        subtitle_text = Text("Enhanced Terminal Interface", style="italic dim")
        
        header_panel = Panel(
            Align.center(header_text + "\n" + subtitle_text),
            box=box.DOUBLE_EDGE,
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(header_panel)
        self.console.print()
        
    def display_status(self, message: str, status: str = "info"):
        """Display a status message with appropriate styling."""
        styles = {
            "info": "blue",
            "success": "green", 
            "warning": "yellow",
            "error": "red"
        }
        
        emoji_map = {
            "info": "ℹ️ ",
            "success": "✅",
            "warning": "⚠️ ",
            "error": "❌"
        }
        
        style = styles.get(status, "blue")
        emoji = emoji_map.get(status, "")
        
        self.console.print(f"{emoji} {message}", style=style)
        
    def display_connection_progress(self) -> Progress:
        """Create and return a progress indicator for connection."""
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        )
        return progress
        
    async def connect_with_progress(self) -> bool:
        """Connect to GitHub MCP server with visual progress."""
        try:
            self.client = GitHubMCPClient()
            
            with self.display_connection_progress() as progress:
                task = progress.add_task("Connecting to GitHub MCP server...", total=None)
                await self.client.connect_to_github_mcp_server()
                progress.update(task, description="Connected successfully!")
                
            self.display_status("Connected to GitHub MCP server", "success")
            return True
            
        except Exception as e:
            self.display_status(f"Connection failed: {e}", "error")
            self.show_connection_troubleshooting()
            return False
            
    def show_connection_troubleshooting(self):
        """Display connection troubleshooting help."""
        troubleshooting = Panel(
            "[bold yellow]Connection Troubleshooting:[/bold yellow]\n\n"
            "1. [cyan]Set GitHub Token:[/cyan]\n"
            "   export GITHUB_TOKEN='your_token_here'\n\n"
            "2. [cyan]Verify Token Permissions:[/cyan]\n"
            "   • Repository access (read/write)\n"
            "   • Pull request creation\n"
            "   • Code access\n\n"
            "3. [cyan]Check Network:[/cyan]\n"
            "   • Internet connection\n"
            "   • Corporate firewall settings",
            title="🔧 Troubleshooting",
            border_style="yellow"
        )
        self.console.print(troubleshooting)
        
    async def load_tools_with_progress(self) -> bool:
        """Load available tools with visual progress."""
        if not self.client:
            return False
            
        try:
            with self.display_connection_progress() as progress:
                task = progress.add_task("Loading available tools...", total=None)
                self.tools = await self.client.list_tools()
                progress.update(task, description=f"Loaded {len(self.tools)} tools")
                
            self.display_status(f"Found {len(self.tools)} available tools", "success")
            return True
            
        except Exception as e:
            self.display_status(f"Failed to load tools: {e}", "error")
            return False
            
    def display_tools_table(self):
        """Display available tools in a formatted table."""
        if not self.tools:
            self.display_status("No tools available", "warning")
            return
            
        table = Table(title="🛠️  Available GitHub MCP Tools", box=box.ROUNDED)
        table.add_column("Tool Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Status", justify="center")
        
        for tool in self.tools:
            name = tool.get("name", "Unknown")
            description = tool.get("description", "No description available")
            
            # Highlight the main tool we're interested in
            if name == "create_pull_request_with_copilot":
                status = "[green]⭐ Main Tool[/green]"
                name_style = "[bold green]" + name + "[/bold green]"
            else:
                status = "[dim]Available[/dim]"
                name_style = name
                
            table.add_row(name_style, description, status)
            
        self.console.print(table)
        self.console.print()
        
    def get_repository_input(self) -> Tuple[Optional[str], Optional[str]]:
        """Get repository owner and name with validation."""
        self.console.print(Panel("📁 Repository Information", style="blue"))
        
        # Get owner with validation
        while True:
            owner = Prompt.ask("[cyan]Repository owner[/cyan]")
            if owner and owner.strip():
                owner = owner.strip()
                break
            self.display_status("Repository owner cannot be empty", "error")
            
        # Get repo name with validation  
        while True:
            repo = Prompt.ask(f"[cyan]Repository name[/cyan] (owner: {owner})")
            if repo and repo.strip():
                repo = repo.strip()
                break
            self.display_status("Repository name cannot be empty", "error")
            
        # Confirm the repository
        repo_display = Panel(
            f"[bold]Owner:[/bold] {owner}\n[bold]Repository:[/bold] {repo}",
            title="📋 Repository Selected",
            border_style="green"
        )
        self.console.print(repo_display)
        
        if not Confirm.ask("Is this correct?"):
            return None, None
            
        return owner, repo
        
    def get_pr_details(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Get pull request title, problem statement, and base branch."""
        self.console.print(Panel("✏️  Pull Request Details", style="blue"))
        
        # Get PR title
        while True:
            title = Prompt.ask("[cyan]Pull request title[/cyan]")
            if title and title.strip():
                title = title.strip()
                break
            self.display_status("Pull request title cannot be empty", "error")
            
        # Get base branch (optional)
        base_ref = Prompt.ask(
            "[cyan]Base branch[/cyan] (press Enter for default)", 
            default=""
        )
        if base_ref:
            base_ref = base_ref.strip()
        else:
            base_ref = None
            
        # Get problem statement with multi-line support
        self.console.print("\n[cyan]Problem statement[/cyan] (detailed description):")
        self.console.print("[dim]Enter your problem statement. Press Ctrl+D when finished.[/dim]")
        
        problem_lines = []
        try:
            while True:
                line = input()
                problem_lines.append(line)
        except EOFError:
            pass
            
        problem_statement = "\n".join(problem_lines).strip()
        
        if not problem_statement:
            self.display_status("Problem statement cannot be empty", "error")
            return None, None, None
            
        # Display summary
        summary_panel = Panel(
            f"[bold]Title:[/bold] {title}\n"
            f"[bold]Base Branch:[/bold] {base_ref or 'default'}\n"
            f"[bold]Problem:[/bold] {problem_statement[:100]}{'...' if len(problem_statement) > 100 else ''}",
            title="📝 Pull Request Summary",
            border_style="green"
        )
        self.console.print(summary_panel)
        
        if not Confirm.ask("Create pull request with these details?"):
            return None, None, None
            
        return title, problem_statement, base_ref
        
    async def create_pr_with_live_progress(
        self, 
        owner: str, 
        repo: str, 
        title: str, 
        problem_statement: str, 
        base_ref: Optional[str]
    ) -> Dict[str, Any]:
        """Create PR with live progress display."""
        
        # Create layout for live updates
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="progress", size=8),
            Layout(name="status", size=10)
        )
        
        # Header
        header = Panel(
            f"[bold cyan]Creating Pull Request[/bold cyan]\n"
            f"Repository: {owner}/{repo}",
            box=box.ROUNDED
        )
        layout["header"].update(header)
        
        # Progress section
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        )
        layout["progress"].update(progress)
        
        # Status section with steps
        steps = Table(box=box.SIMPLE)
        steps.add_column("Step", style="cyan")
        steps.add_column("Status", justify="center")
        steps.add_row("🔄 Analyzing repository", "[yellow]In Progress[/yellow]")
        steps.add_row("🤖 Generating code with Copilot", "[dim]Pending[/dim]")
        steps.add_row("📝 Creating pull request", "[dim]Pending[/dim]")
        steps.add_row("✅ Finalizing", "[dim]Pending[/dim]")
        
        layout["status"].update(Panel(steps, title="Progress Steps"))
        
        result = None
        
        with Live(layout, console=self.console, refresh_per_second=4):
            task = progress.add_task("Starting PR creation...", total=100)
            
            try:
                # Simulate progress updates (since we can't easily hook into MCP internals)
                await asyncio.sleep(1)
                progress.update(task, advance=25, description="Connecting to GitHub Copilot...")
                
                # Update steps
                steps = Table(box=box.SIMPLE)
                steps.add_column("Step", style="cyan")
                steps.add_column("Status", justify="center")
                steps.add_row("🔄 Analyzing repository", "[green]Complete[/green]")
                steps.add_row("🤖 Generating code with Copilot", "[yellow]In Progress[/yellow]")
                steps.add_row("📝 Creating pull request", "[dim]Pending[/dim]")
                steps.add_row("✅ Finalizing", "[dim]Pending[/dim]")
                layout["status"].update(Panel(steps, title="Progress Steps"))
                
                await asyncio.sleep(2)
                progress.update(task, advance=25, description="Copilot is generating code...")
                
                # Call the actual MCP tool
                result = await self.client.create_pull_request_with_copilot(
                    owner=owner,
                    repo=repo,
                    problem_statement=problem_statement,
                    title=title,
                    base_ref=base_ref
                )
                
                progress.update(task, advance=35, description="Creating pull request...")
                
                # Update steps
                steps = Table(box=box.SIMPLE)
                steps.add_column("Step", style="cyan")
                steps.add_column("Status", justify="center")
                steps.add_row("🔄 Analyzing repository", "[green]Complete[/green]")
                steps.add_row("🤖 Generating code with Copilot", "[green]Complete[/green]")
                steps.add_row("📝 Creating pull request", "[yellow]In Progress[/yellow]")
                steps.add_row("✅ Finalizing", "[dim]Pending[/dim]")
                layout["status"].update(Panel(steps, title="Progress Steps"))
                
                await asyncio.sleep(1)
                progress.update(task, advance=15, description="Finalizing...")
                
                # Final update
                steps = Table(box=box.SIMPLE)
                steps.add_column("Step", style="cyan")
                steps.add_column("Status", justify="center")
                steps.add_row("🔄 Analyzing repository", "[green]Complete[/green]")
                steps.add_row("🤖 Generating code with Copilot", "[green]Complete[/green]")
                steps.add_row("📝 Creating pull request", "[green]Complete[/green]")
                steps.add_row("✅ Finalizing", "[green]Complete[/green]")
                layout["status"].update(Panel(steps, title="Progress Steps"))
                
                progress.update(task, completed=100, description="Pull request created successfully!")
                await asyncio.sleep(1)
                
            except Exception as e:
                progress.update(task, description=f"Error: {e}")
                result = {
                    "success": False,
                    "error": str(e),
                    "content": []
                }
                
        return result
        
    def display_result(self, result: Dict[str, Any]):
        """Display the PR creation result with beautiful formatting."""
        if result.get("success", False):
            # Success case
            success_panel = Panel(
                "🎉 [bold green]Pull Request Created Successfully![/bold green]",
                box=box.DOUBLE_EDGE,
                border_style="green"
            )
            self.console.print(success_panel)
            
            # Display content if available
            if result.get("content"):
                for content_item in result["content"]:
                    if content_item.get("type") == "text":
                        text_content = content_item["text"]
                        
                        # Try to format as code if it looks like code/JSON
                        if text_content.strip().startswith(("{", "[")):
                            try:
                                formatted = json.dumps(json.loads(text_content), indent=2)
                                syntax = Syntax(formatted, "json", theme="monokai", line_numbers=True)
                                self.console.print(Panel(syntax, title="📄 Response Details"))
                            except json.JSONDecodeError:
                                self.console.print(Panel(text_content, title="📄 Response"))
                        else:
                            self.console.print(Panel(text_content, title="📄 Response"))
                            
        else:
            # Error case
            error_msg = result.get("error", "Unknown error occurred")
            
            error_panel = Panel(
                f"[bold red]❌ Pull Request Creation Failed[/bold red]\n\n"
                f"[yellow]Error:[/yellow] {error_msg}",
                box=box.DOUBLE_EDGE,
                border_style="red"
            )
            self.console.print(error_panel)
            
            # Show suggestions based on error type
            self.show_error_suggestions(error_msg)
            
    def show_error_suggestions(self, error_msg: str):
        """Display helpful suggestions based on the error."""
        suggestions = []
        
        if "401" in error_msg or "unauthorized" in error_msg.lower():
            suggestions = [
                "Check your GITHUB_TOKEN environment variable",
                "Verify your token hasn't expired",
                "Ensure token has required permissions (repo, write:repo)",
                "Try regenerating your GitHub token"
            ]
        elif "404" in error_msg or "not found" in error_msg.lower():
            suggestions = [
                "Verify the repository name is spelled correctly",
                "Check if the repository exists and is accessible",
                "Ensure you have access to this repository",
                "For private repos, verify token has private repo access"
            ]
        elif "403" in error_msg or "forbidden" in error_msg.lower():
            suggestions = [
                "Your token may not have sufficient permissions",
                "Check if you're a collaborator on this repository",
                "Verify organization access settings"
            ]
        else:
            suggestions = [
                "Check your internet connection",
                "Verify repository details are correct",
                "Try again in a few moments",
                "Check GitHub status page for service issues"
            ]
            
        if suggestions:
            suggestion_text = "\n".join([f"• {s}" for s in suggestions])
            suggestion_panel = Panel(
                suggestion_text,
                title="💡 Suggestions",
                border_style="yellow"
            )
            self.console.print(suggestion_panel)
            
    async def run_interactive_session(self):
        """Run the full interactive TUI session."""
        try:
            self.print_header()
            
            # Step 1: Connect to GitHub MCP server
            self.console.print(Rule("[bold blue]🌐 Connecting to GitHub MCP Server[/bold blue]"))
            if not await self.connect_with_progress():
                return
                
            self.console.print()
            
            # Step 2: Load and display tools
            self.console.print(Rule("[bold blue]🛠️  Loading Available Tools[/bold blue]"))
            if not await self.load_tools_with_progress():
                return
                
            self.display_tools_table()
            
            # Check if our main tool is available
            copilot_tool = next((t for t in self.tools if t['name'] == 'create_pull_request_with_copilot'), None)
            if not copilot_tool:
                self.display_status("create_pull_request_with_copilot tool not found", "warning")
                self.console.print("Available tools are shown above. You can still use the basic CLI mode.")
                return
                
            # Step 3: Get repository information
            self.console.print(Rule("[bold blue]📁 Repository Setup[/bold blue]"))
            owner, repo = self.get_repository_input()
            if not owner or not repo:
                self.display_status("Repository setup cancelled", "warning")
                return
                
            # Step 4: Get PR details
            self.console.print(Rule("[bold blue]✏️  Pull Request Configuration[/bold blue]"))
            title, problem_statement, base_ref = self.get_pr_details()
            if not title or not problem_statement:
                self.display_status("PR configuration cancelled", "warning")
                return
                
            # Step 5: Create the PR with live progress
            self.console.print(Rule("[bold blue]🚀 Creating Pull Request[/bold blue]"))
            result = await self.create_pr_with_live_progress(
                owner, repo, title, problem_statement, base_ref
            )
            
            # Step 6: Display results
            self.console.print(Rule("[bold blue]📊 Results[/bold blue]"))
            self.display_result(result)
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]👋 Session cancelled by user. Goodbye![/yellow]")
        except Exception as e:
            self.console.print(f"\n[red]❌ Unexpected error: {e}[/red]")
        finally:
            if self.client:
                await self.client.close()
                self.display_status("Disconnected from GitHub MCP server", "info")


async def run_tui():
    """Entry point for the enhanced TUI interface."""
    tui = GitHubMCPTUI()
    await tui.run_interactive_session()


if __name__ == "__main__":
    asyncio.run(run_tui())