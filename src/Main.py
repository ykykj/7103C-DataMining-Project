from langchain_core.messages import ToolMessage, AIMessage, HumanMessage
from src.agent.PersonalAssistantAgent import PersonalAssistantAgent
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Initialize Rich console
console = Console()

# Initialize your agent
agent = PersonalAssistantAgent()

console.print("[bold cyan]Welcome to Personal Assistant![/bold cyan]\n")

while True:
    try:
        query = console.input("[bold green]You:[/bold green] ")
        if query.lower() in ("exit", "quit"):
            console.print("\n[bold yellow]Goodbye![/bold yellow]")
            break

        response = agent.callAgent(query)

        for message in response["messages"]:
            if isinstance(message, AIMessage):
                # Use a panel for AI messages
                ai_text = Text(message.content if isinstance(message.content, str) else str(message.content), style="bold magenta")
                console.print(Panel(ai_text, title="[bold red]Assistant[/bold red]", border_style="magenta"))
            elif isinstance(message, ToolMessage):
                tool_text = Text(message.content if message.content else "Tool executed", style="bold blue")
                console.print(Panel(tool_text, title="[bold blue]Tool[/bold blue]", border_style="blue"))

    except KeyboardInterrupt:
        console.print("\n[bold yellow]Exiting...[/bold yellow]")
        break
