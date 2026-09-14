import os
import sys
import json
import uuid
import time
import requests
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table
from rich import box
from rich.text import Text

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.formatted_text import FormattedText

console = Console()

API_URL = "https://xpert-api-services.prod.ai.2u.com/v1/message"
CONVERSATION_ID = str(uuid.uuid4())

HISTORY_FILE = Path.home() / ".kni_history"

SYSTEM_MESSAGE = (
    "You are KNI, an intelligent personal AI assistant. "
    "Your primary purpose is to help users learn, build projects, solve problems, program, debug, research, "
    "explore technology, and improve productivity. You are professional, practical, accurate, friendly, reliable, "
    "and adapt to the user's goals and knowledge level. You have broad expertise in programming, software development, "
    "AI, machine learning, deep learning, LLMs, local and offline AI, web development, APIs, databases, Linux, Windows, "
    "Git, GitHub, networking, cybersecurity, cloud, DevOps, Docker, operating systems, quantum computing, Qiskit, "
    "mathematics, science, and technology. Understand the actual goal before answering and prefer practical, clear, "
    "and efficient solutions over unnecessary theory. Explain what, how, why, and when useful. For programming, "
    "analyze requirements and errors carefully, identify the real cause, explain why it happens, provide clean and "
    "maintainable code, and suggest how to verify the solution. Never invent functions, APIs, commands, libraries, "
    "documentation, results, or system behavior. Never claim code was executed or tested without evidence. "
    "Clearly distinguish facts, assumptions, possibilities, and suggestions. Teach progressively with practical "
    "examples and break complex topics into simple steps. Maintain conversation context and do not repeatedly ask for "
    "information already provided. Format all responses using standard Markdown. Include language tags on code blocks "
    "(e.g., ```python, ```bash). Use bolding, bullet points, headers, and tables where appropriate for maximum clarity."
)


def print_status_bar():
    console.print("[dim white]Type [bold #FFD700]help[/bold #FFD700] for commands  •  Type [bold #FFD700]exit[/bold #FFD700] to quit[/dim white]\n")


def print_help():
    table = Table(title="✨ KNI Command Center ✨", box=box.ROUNDED, border_style="#00F5FF")
    table.add_column("Command", style="bold #FFD700", justify="left")
    table.add_column("Description", style="white")

    table.add_row("💡 help", "Display command guide")
    table.add_row("🧹 clear", "Clear screen & refresh UI")
    table.add_row("↺ reset", "Reset memory context")
    table.add_row("💾 save [file]", "Export chat log to markdown")
    table.add_row("👋 exit / quit", "Exit session")

    console.print(table)
    console.print()


def save_chat_log(context, filepath=None):
    if not filepath:
        filename = f"kni_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = os.path.join(os.getcwd(), filename)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# KNI Chat Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            for msg in context:
                role = "You" if msg["role"] == "user" else "Kni"
                f.write(f"### {role}\n\n{msg['content']}\n\n---\n\n")
        console.print(f"[bold #10B981]💾 Chat log saved to:[/bold #10B981] [underline #00F5FF]{filepath}[/underline #00F5FF]\n")
    except Exception as e:
        console.print(f"[bold #FF4444]❌ Failed to save log:[/bold #FF4444] {e}\n")


def stream_kni_response(context):
    payload = {
        "messages": context[-5:],
        "client_id": "edx-explorer",
        "stream": True,
        "system_message": SYSTEM_MESSAGE,
        "tags": [],
        "conversation_id": CONVERSATION_ID
    }

    full_text = ""
    decoder = json.JSONDecoder()

    with Live(
        Panel(
            Spinner("dots", text="[bold dim #00F5FF]Thinking...[/bold dim #00F5FF]", style="#FF007F"),
            subtitle="[bold #FF007F]Kni[/bold #FF007F]",
            subtitle_align="right",
            border_style="#00F5FF",
            box=box.ROUNDED,
            padding=(1, 2)
        ),
        console=console,
        refresh_per_second=20,
        transient=False
    ) as live:

        try:
            response = requests.post(API_URL, json=payload, stream=True, timeout=45)
            response.raise_for_status()

            buffer = ""
            for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                if chunk:
                    buffer += chunk
                    pos = 0
                    while pos < len(buffer):
                        try:
                            data, next_pos = decoder.raw_decode(buffer, pos)
                            if data and isinstance(data, list) and len(data) > 0:
                                content = data[0].get("content")
                                if content:
                                    full_text = content
                                    live.update(
                                        Panel(
                                            Markdown(full_text),
                                            subtitle="[bold #FF007F]Kni[/bold #FF007F]",
                                            subtitle_align="right",
                                            border_style="#00F5FF",
                                            box=box.ROUNDED,
                                            padding=(1, 2)
                                        )
                                    )
                            pos = next_pos
                        except json.JSONDecodeError:
                            break
                    buffer = buffer[pos:]

            if not full_text:
                live.update(
                    Panel(
                        "[bold #FF4444]⚠️ No response received from server.[/bold #FF4444]",
                        subtitle="[bold #FF4444]Error[/bold #FF4444]",
                        subtitle_align="right",
                        border_style="#FF4444",
                        box=box.ROUNDED
                    )
                )

        except requests.exceptions.RequestException as req_err:
            live.update(
                Panel(
                    f"[bold #FF4444]❌ Network Connection Error:[/bold #FF4444]\n{req_err}",
                    subtitle="[bold #FF4444]Connection Error[/bold #FF4444]",
                    subtitle_align="right",
                    border_style="#FF4444",
                    box=box.ROUNDED
                )
            )
        except Exception as err:
            live.update(
                Panel(
                    f"[bold #FF4444]❌ An error occurred:[/bold #FF4444]\n{err}",
                    subtitle="[bold #FF4444]Unexpected Error[/bold #FF4444]",
                    subtitle_align="right",
                    border_style="#FF4444",
                    box=box.ROUNDED
                )
            )

    console.print()
    return full_text


def main():
    os.system("")
    console.clear()
    print_status_bar()

    context = []
    session = PromptSession(history=FileHistory(str(HISTORY_FILE)))

    prompt_text = FormattedText([('#00F5FF bold', '⚡ You '), ('#FFD700 bold', '❯ ')])

    while True:
        try:
            user_input = session.prompt(prompt_text).strip()

            if not user_input:
                continue

            cmd_lower = user_input.lower()

            if cmd_lower in ["exit", "quit", "/exit", "/quit"]:
                console.print()
                console.print("[bold #10B981]👋 Goodbye! Have a great day![/bold #10B981]\n")
                break

            elif cmd_lower in ["clear", "/clear"]:
                console.clear()
                print_status_bar()
                continue

            elif cmd_lower in ["reset", "/reset"]:
                context.clear()
                console.clear()
                print_status_bar()
                console.print("[bold #FFD700]↺ Conversation context reset.[/bold #FFD700]\n")
                continue

            elif cmd_lower in ["help", "/help"]:
                console.print()
                print_help()
                continue

            elif cmd_lower.startswith("save") or cmd_lower.startswith("/save"):
                parts = user_input.split(maxsplit=1)
                filepath = parts[1] if len(parts) > 1 else None
                console.print()
                save_chat_log(context, filepath)
                continue

            context.append({"role": "user", "content": user_input})

            console.print()

            ai_response = stream_kni_response(context)

            if ai_response:
                context.append({"role": "assistant", "content": ai_response})
            else:
                if context and context[-1]["role"] == "user":
                    context.pop()

        except KeyboardInterrupt:
            console.print("\n[bold #FFD700]⚠️ Input cancelled. Type exit to leave.[/bold #FFD700]\n")
        except EOFError:
            console.print("\n[bold #FF4444]Session closed.[/bold #FF4444]\n")
            break


if __name__ == "__main__":
    main()
