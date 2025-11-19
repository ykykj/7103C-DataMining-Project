"""
Personal Assistant Agent - Main Entry Point
Run with: python main.py or uv run main.py
"""
import sys
import time
from pathlib import Path

from langchain_core.messages import AIMessage
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
            
            # Display AI responses
            for message in response.get("messages", []):
                if isinstance(message, AIMessage):
                    ai_text = (
                        message.text
                        if isinstance(message.text, str)
                        else str(message.text)
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
