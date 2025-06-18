#!/usr/bin/env python3
import subprocess
import re
import argparse
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.box import MINIMAL_HEAVY_HEAD
from rich.text import Text

def parse_last_output():
    """Parse 'last -x' output to extract system boot entries, including 'still running'."""
    output = subprocess.check_output(["last", "-x"], text=True)
    lines = output.strip().split("\n")

    parsed_entries = []
    year = datetime.now().year

    for line in lines:
        if not line.startswith("reboot"):
            continue

        RE_BOOT_LINE = re.compile(
            r"(?P<type>reboot)\s+system boot\s+(?P<kernel>[\w\.\-\*]+)?\s+(?P<start>\w{3}\s+\w{3}\s+\d+\s+\d+:\d+)"
            r"(?:\s+-\s+(?P<end>\w{3}\s+\d+:\d+|\d+:\d+|crash|down|still running))?\s+\((?P<duration>[^)]+)\)"
        )

        match = RE_BOOT_LINE.match(line)
        if not match:
            continue

        start_str = match.group("start")
        try:
            start_dt = datetime.strptime(f"{year} {start_str}", "%Y %a %b %d %H:%M")
        except ValueError:
            continue

        parsed_entries.append({
            "type": match.group("type"),
            "kernel": match.group("kernel") or "-",
            "start_dt": start_dt,
            "duration": match.group("duration"),
            "end": match.group("end") or "still running"
        })

    parsed_entries.sort(key=lambda x: x["start_dt"], reverse=True)
    return parsed_entries

def format_duration(duration_str):
    """Convert raw duration string into human-readable format."""
    if duration_str.strip() == "00:00":
        return "a few sec"

    if "+" in duration_str:
        days_part, time_part = duration_str.split("+")
        days = int(days_part.strip())
        hours, minutes = map(int, time_part.strip().split(":"))
        return f"{days}d {hours}h {minutes}m"
    else:
        hours, minutes = map(int, duration_str.strip().split(":"))
        return f"{hours}h {minutes}m"

def format_timedelta(td: timedelta):
    """Convert timedelta to human-readable uptime string."""
    total_seconds = int(td.total_seconds())
    days = total_seconds // (24 * 3600)
    hours = (total_seconds % (24 * 3600)) // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{days}d {hours}h {minutes}m"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Show boot history with optional date format.")
    parser.add_argument("--long-date", action="store_true", help="Display date as 'May 05, 2025' instead of '2025-05-05'")
    args = parser.parse_args()

    entries = parse_last_output()
    use_long_date = args.long_date
    console = Console()

    table = Table(
        box=MINIMAL_HEAVY_HEAD,
        show_lines=False
    )

    table.add_column("Boot Time", style="bright_cyan", no_wrap=True, justify="left")
    table.add_column("Shutdown", style="bright_blue", no_wrap=True, justify="left")  # changed to bright_blue
    table.add_column("Uptime", style="green", justify="center")
    table.add_column("Exit", justify="center")
    table.add_column("Kernel", style="yellow", justify="right")

    now = datetime.now()

    for entry in entries:
        duration = entry["duration"]
        exit_type = entry["end"]

        if exit_type == "still running":
            shutdown = "still running"
            td = now - entry["start_dt"]
            uptime = format_timedelta(td)
        else:
            if "+" in duration:
                days_part, time_part = duration.split("+")
                days = int(days_part.strip())
                hours, minutes = map(int, time_part.strip().split(":"))
            else:
                days = 0
                hours, minutes = map(int, duration.strip().split(":"))
            shutdown_dt = entry["start_dt"] + timedelta(days=days, hours=hours, minutes=minutes)
            shutdown = shutdown_dt.strftime("%b %d, %Y %H:%M") if use_long_date else shutdown_dt.strftime("%Y-%m-%d %H:%M")
            uptime = format_duration(duration)

        boot_time = entry["start_dt"].strftime("%b %d, %Y %H:%M") if use_long_date else entry["start_dt"].strftime("%Y-%m-%d %H:%M")

        if exit_type == "crash":
            exit_label = "crash"
        elif exit_type == "still running":
            exit_label = "running"
        else:
            exit_label = "shutdown"

        exit_text = Text(exit_label)
        exit_styles = {
            "crash": "bold red",
            "shutdown": "bright_blue",
            "running": "green"
        }
        exit_text.stylize(exit_styles.get(exit_label, "white"))

        table.add_row(
            boot_time,
            shutdown,
            uptime,
            exit_text,
            entry["kernel"]
        )

    console.print(Panel(table, title="Boot History", border_style="cyan", padding=(0, 1), expand=False))
