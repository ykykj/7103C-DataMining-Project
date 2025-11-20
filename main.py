"""
Personal Assistant Agent - Main Entry Point
Run with: python main.py or uv run main.py
"""
import sys
import time
from pathlib import Path

from langchain_core.messages import AIMessage, ToolMessage
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

from src.agent.PersonalAssistantAgent import PersonalAssistantAgent

# Initialize Rich console
console = Console()

# --- Retro ASCII Banner ---
BANNER = r"""
[magenta]__        __   _                            _ [/magenta]
[purple]\ \      / /__| | ___ ___  _ __ ___   ___  | |[/purple]
[blue] \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \ | |[/blue]
[cyan]  \ V  V /  __/ | (_| (_) | | | | | |  __/ |_|[/cyan]
[green]   \_/\_/ \___|_|\___\___/|_| |_| |_|\___| (_)[/green]
"""


def display_intro():
    """Display the welcome banner and intro message."""
    console.print(f"[bold green]{BANNER}[/bold green]")
    console.print(
        Panel.fit(
            "[bold magenta blink]Welcome to Personal Assistant Agent![/bold magenta blink]\n"
            "[cyan]Type your query like 'what can you do?' or type 'exit' to quit.[/cyan]",
            title="[yellow]Your AI Agent[/yellow]",
            border_style="bright_yellow",
            box=box.DOUBLE_EDGE,
            padding=(1, 4),
        )
    )
    time.sleep(0.5)


def main():
    """Main application loop."""
    display_intro()
    
    # Initialize agent
    agent = PersonalAssistantAgent()
    
    # Main interaction loop
    while True:
        try:
            query = console.input("\n[bold green]You:[/bold green] ")
            
            if query.lower().strip() in ("exit", "quit"):
                console.print("\n[bold yellow]👋 Goodbye! Have a great day![/bold yellow]")
                break
            
            # Process query with status indicator
            with console.status("[bold magenta]Working on it...[/bold magenta]", spinner="dots"):
                response = agent.callAgent(query)
            
            # Display tool calls and final response
            messages = response.get("messages", [])
            
            # Track tool calls from this query only (reset for each query)
            # We only want to show tool calls from the current query, not historical ones
            displayed_tool_calls = set()
            
            # Find the index where the current query starts
            # Tool calls before this point are from previous queries
            current_query_start_idx = 0
            for i in range(len(messages) - 1, -1, -1):
                if hasattr(messages[i], 'content') and query in str(messages[i].content):
                    current_query_start_idx = i
                    break
            
            # Only display tool calls from the current query (after current_query_start_idx)
            for i, message in enumerate(messages):
                if i < current_query_start_idx:
                    continue  # Skip messages from previous queries
                    
                # Display tool calls
                if isinstance(message, AIMessage) and hasattr(message, 'tool_calls') and message.tool_calls:
                    for tool_call in message.tool_calls:
                        tool_id = tool_call.get('id', '')
                        if tool_id and tool_id not in displayed_tool_calls:
                            displayed_tool_calls.add(tool_id)
                            tool_name = tool_call.get('name', 'Unknown Tool')
                            tool_args = tool_call.get('args', {})
                            
                            console.print(
                                Panel(
                                    f"[yellow]Tool:[/yellow] {tool_name}\n[dim]Args: {tool_args}[/dim]",
                                    title="[bold yellow]🔧 Tool Call[/bold yellow]",
                                    border_style="yellow",
                                    box=box.ROUNDED,
                                )
                            )
            
            # Display only the final AI response
            if messages:
                last_message = messages[-1]
                if isinstance(last_message, AIMessage):
                    ai_text = (
                        last_message.text
                        if isinstance(last_message.text, str)
                        else str(last_message.text)
                    )
                    if ai_text.strip():
                        console.print(
                            Panel(
                                Text(ai_text, style="bold cyan"),
                                title="[bold red]Assistant[/bold red]",
                                border_style="magenta",
                                box=box.ROUNDED,
                            )
                        )
        
        except KeyboardInterrupt:
            console.print("\n[bold yellow]⚙️ Exiting...[/bold yellow]")
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            console.print(
                "[bold yellow]⚠️ An error occurred. Please check your API key and balance, then retry.[/bold yellow]"
            )


if __name__ == "__main__":
    main()
