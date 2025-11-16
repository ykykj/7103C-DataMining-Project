from langchain_core.messages import ToolMessage, AIMessage, HumanMessage
from src.agent.PersonalAssistantAgent import PersonalAssistantAgent
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
import time
import sys

# Initialize Rich console
console = Console()

# --- Retro ASCII Banner ---
banner = r"""
[magenta]__        __   _                            _ [/magenta]
[purple]\ \      / /__| | ___ ___  _ __ ___   ___  | |[/purple]
[blue] \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \ | |[/blue]
[cyan]  \ V  V /  __/ | (_| (_) | | | | | |  __/ |_|[/cyan]
[green]   \_/\_/ \___|_|\___\___/|_| |_| |_|\___| (_)[/green]
"""


def type_writer_effect(text, delay=0.002):
    """Print text with a typing animation for a retro computer feel."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

# --- Display Retro Intro ---
console.print(f"[bold green]{banner}[/bold green]")
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

# Initialize your agent
agent = PersonalAssistantAgent()

# --- Main Loop ---
while True:
    try:
        query = console.input("\n[bold green]You:[/bold green] ")

        if query.lower().strip() in ("exit", "quit"):
            console.print("\n[bold yellow]👋 Goodbye! Have a great day![/bold yellow]")
            break

        # Typing effect for thinking
        with console.status("[bold magenta]Working on it...[/bold magenta]", spinner="dots"):
            response = agent.callAgent(query)

        # Display responses
        for message in response.get("messages", []):
            if isinstance(message, AIMessage):
                ai_text = (
                    message.text
                    if isinstance(message.text, str)
                    else str(message.text)
                )
                if len(ai_text.strip()) != 0:
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