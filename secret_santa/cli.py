"""Secret Santa CLI - Command Line Interface."""

import sys
import os

# Force UTF-8 encoding on Windows for emoji support
if sys.platform == "win32":
    os.environ.setdefault("PYTHONUTF8", "1")
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    if sys.stderr.encoding != "utf-8":
        sys.stderr.reconfigure(encoding="utf-8")

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box

from .models import Participant, Cluster, Config
from .storage import Storage
from .matcher import create_assignments, MatcherError
from .email import send_all_assignments, EmailError

console = Console()
storage = Storage()

# ASCII Santa Art (cleaner version)
SANTA_ART = """
[white]        *    *  *[/]
[white]     *         *[/]
[red]        ███████[/]
[white]       █████████[/]
[red]      ███████████[/]
[white]     █[/][red]██[/][white]█████[/][red]██[/][white]█[/]
[white]     █[/][blue]◉[/][white]█████[/][blue]◉[/][white]█[/]
[white]      █████████[/]
[white]       ██[/][red]███[/][white]██[/]
[red]      ▄█████████▄[/]
[red]     ███████████[/][white]█[/][red]█[/]
[white]    ═══════════════[/]
"""

TITLE_ART = """
[red]╔═════════════════════════════════════════════════════════════════════════╗[/]
[red]║                                                                         ║[/]
[red]║[/]  [white]███████╗███████╗ ██████╗██████╗ ███████╗████████╗[/]                   [red]║[/]
[red]║[/]  [white]██╔════╝██╔════╝██╔════╝██╔══██╗██╔════╝╚══██╔══╝[/]                   [red]║[/]
[red]║[/]  [white]███████╗█████╗  ██║     ██████╔╝█████╗     ██║[/]                     [red]║[/]
[red]║[/]  [white]╚════██║██╔══╝  ██║     ██╔══██╗██╔══╝     ██║[/]                     [red]║[/]
[red]║[/]  [white]███████║███████╗╚██████╗██║  ██║███████╗   ██║[/]                     [red]║[/]
[red]║[/]  [white]╚══════╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝   ╚═╝[/]                     [red]║[/]
[red]║                                                                         ║[/]
[red]║[/]       [red]███████╗ █████╗ ███╗   ██╗████████╗ █████╗[/]                     [red]║[/]
[red]║[/]       [red]██╔════╝██╔══██╗████╗  ██║╚══██╔══╝██╔══██╗[/]                    [red]║[/]
[red]║[/]       [red]███████╗███████║██╔██╗ ██║   ██║   ███████║[/]                    [red]║[/]
[red]║[/]       [red]╚════██║██╔══██║██║╚██╗██║   ██║   ██╔══██║[/]                    [red]║[/]
[red]║[/]       [red]███████║██║  ██║██║ ╚████║   ██║   ██║  ██║[/]                    [red]║[/]
[red]║[/]       [red]╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝[/]                    [red]║[/]
[red]║                                                                         ║[/]
[red]╚═════════════════════════════════════════════════════════════════════════╝[/]
"""


def show_welcome():
    """Display the welcome screen with Santa art and navigation."""
    console.clear()
    
    # Show title
    console.print(TITLE_ART)
    console.print()
    
    # Show Santa
    console.print(Align.center(SANTA_ART))
    
    # Show status dashboard
    show_dashboard()
    
    # Show categorized commands
    console.print()
    commands_text = """[bold white]👤 PEOPLE[/]
  [cyan]santa add[/] [dim]"Name" "email"[/]          Add a person
  [cyan]santa add[/] [dim]"Name" "email" --kid[/]    Add a kid (use with --separate-kids)
  [cyan]santa list[/]                        View all participants
  [cyan]santa remove[/] [dim]"Name"[/]               Remove someone

[bold white]👨‍👩‍👧‍👦 FAMILY GROUPS[/] (prevent matching within group)
  [cyan]santa cluster create[/] [dim]"Family"[/]     Create a group
  [cyan]santa cluster add[/] [dim]"Family" "Name"[/]  Add person to group
  [cyan]santa cluster list[/]                 View all groups
  [cyan]santa cluster kick[/] [dim]"Family" "Name"[/] Remove from group
  [cyan]santa cluster remove[/] [dim]"Family"[/]     Delete entire group

[bold white]🎁 MATCHING & SENDING[/]
  [cyan]santa assign[/]                       Generate random matches
  [cyan]santa assign --separate-kids[/]       Kids match kids only
  [cyan]santa send --dry-run[/]               Preview emails
  [cyan]santa send[/]                         Send all emails

[bold white]⚙️ OTHER[/]
  [cyan]santa config --show[/]                View email settings
  [cyan]santa clear[/]                        Delete all data
  [cyan]santa --help[/]                       Full command reference"""
    
    console.print(Panel(
        commands_text,
        title="[bold red]🎄 Quick Reference 🎄[/]",
        border_style="red",
        box=box.DOUBLE
    ))


def show_dashboard():
    """Show current status of participants, clusters, and assignments."""
    participants = storage.list_participants()
    clusters = storage.list_clusters()
    assignments = storage.get_assignments()
    config = storage.get_config()
    
    # Status indicators
    p_status = f"[green]✓ {len(participants)}[/]" if participants else "[yellow]0[/]"
    c_status = f"[green]✓ {len(clusters)}[/]" if clusters else "[dim]0[/]"
    a_status = f"[green]✓ Done[/]" if assignments else "[yellow]Pending[/]"
    e_status = "[green]✓ Ready[/]" if config.brevo_api_key else "[red]✗ Not configured[/]"
    
    dashboard = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    dashboard.add_column(justify="center")
    dashboard.add_column(justify="center")
    dashboard.add_column(justify="center")
    dashboard.add_column(justify="center")
    
    dashboard.add_row(
        f"[white]👥 Participants[/]\n{p_status}",
        f"[white]👨‍👩‍👧‍👦 Clusters[/]\n{c_status}",
        f"[white]🎁 Assignments[/]\n{a_status}",
        f"[white]📧 Email[/]\n{e_status}",
    )
    
    console.print(Panel(dashboard, title="[bold white]Status Dashboard[/]", border_style="white"))


@click.group(invoke_without_command=True)
@click.version_option(version="1.0.0", prog_name="Secret Santa CLI")
@click.pass_context
def cli(ctx):
    """🎄 Secret Santa CLI - Manage gift exchanges with cluster-based exclusions."""
    if ctx.invoked_subcommand is None:
        show_welcome()



# ============================================================================
# Participant Commands
# ============================================================================

@cli.command("add")
@click.argument("name")
@click.argument("email")
@click.option("--parent-email", "-p", help="Parent email to CC on assignment notification")
@click.option("--kid", "-k", is_flag=True, help="Mark as a kid (kids only match with other kids)")
def add_participant(name: str, email: str, parent_email: str = None, kid: bool = False):
    """Add a NEW participant (person) to the exchange.
    
    Example: santa add "John" "john@email.com"
    """
    try:
        participant = Participant(
            name=name,
            email=email,
            parent_email=parent_email,
            is_kid=kid
        )
        storage.add_participant(participant)
        
        msg = f"✅ Added [bold green]{name}[/] ({email})"
        if kid:
            msg += " [magenta][KID][/]"
        if parent_email:
            msg += f" with parent CC: {parent_email}"
        console.print(msg)
        
    except ValueError as e:
        console.print(f"[red]Error:[/] {e}")
        raise SystemExit(1)


@cli.command("list")
def list_participants():
    """Show all participants."""
    participants = storage.list_participants()
    
    if not participants:
        console.print("[yellow]No participants yet.[/] Add some with: santa add \"name\" \"email\"")
        return
    
    table = Table(title="🎅 Participants", show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=4)
    table.add_column("Name", style="cyan")
    table.add_column("Email", style="green")
    table.add_column("Kid", style="magenta", justify="center")
    table.add_column("Parent Email", style="yellow")
    table.add_column("Cluster", style="blue")
    
    clusters = {c.id: c.name for c in storage.list_clusters()}
    
    for i, p in enumerate(participants, 1):
        cluster_name = clusters.get(p.cluster_id, "-") if p.cluster_id else "-"
        table.add_row(
            str(i),
            p.name,
            p.email,
            "✓" if p.is_kid else "-",
            p.parent_email or "-",
            cluster_name
        )
    
    console.print(table)


@cli.command("remove")
@click.argument("name")
@click.confirmation_option(prompt="Are you sure you want to remove this participant?")
def remove_participant(name: str):
    """Remove a participant from the exchange."""
    if storage.remove_participant(name):
        console.print(f"✅ Removed [bold red]{name}[/]")
    else:
        console.print(f"[red]Error:[/] Participant '{name}' not found")
        raise SystemExit(1)


# ============================================================================
# Cluster Commands
# ============================================================================

@cli.group("cluster")
def cluster_group():
    """Manage exclusion clusters (family groups who shouldn't match).
    
    Use 'cluster create' to make a group, then 'cluster add' to put people in it.
    """
    pass


@cluster_group.command("create")
@click.argument("name")
def create_cluster(name: str):
    """Create a new exclusion cluster (e.g. 'Smith Family').
    
    Example: santa cluster create "Smith Family"
    """
    try:
        cluster = Cluster(name=name)
        storage.create_cluster(cluster)
        console.print(f"✅ Created cluster [bold blue]{name}[/]")
    except ValueError as e:
        console.print(f"[red]Error:[/] {e}")
        raise SystemExit(1)


@cluster_group.command("add")
@click.argument("cluster_name")
@click.argument("participant_name")
def add_to_cluster(cluster_name: str, participant_name: str):
    """Add an EXISTING participant to a cluster.
    
    Note: The person must already exist (use 'santa add' first).
    
    Example: santa cluster add "Smith Family" "John"
    """
    try:
        storage.add_to_cluster(cluster_name, participant_name)
        console.print(f"✅ Added [bold cyan]{participant_name}[/] to cluster [bold blue]{cluster_name}[/]")
    except ValueError as e:
        console.print(f"[red]Error:[/] {e}")
        raise SystemExit(1)


@cluster_group.command("list")
def list_clusters():
    """Show all clusters and their members."""
    clusters = storage.list_clusters()
    
    if not clusters:
        console.print("[yellow]No clusters yet.[/] Create one with: santa cluster create \"Family Name\"")
        return
    
    for cluster in clusters:
        members = []
        for member_id in cluster.member_ids:
            p = storage.get_participant_by_id(member_id)
            if p:
                members.append(p.name)
        
        member_text = ", ".join(members) if members else "[dim]No members yet - use: santa cluster add \"" + cluster.name + "\" \"Name\"[/]"
        
        panel = Panel(
            member_text,
            title=f"[bold blue]{cluster.name}[/]",
            subtitle=f"{len(members)} members",
            border_style="blue"
        )
        console.print(panel)


@cluster_group.command("remove")
@click.argument("cluster_name")
@click.confirmation_option(prompt="Are you sure you want to delete this cluster?")
def remove_cluster(cluster_name: str):
    """Delete an entire cluster (members stay in the exchange).
    
    Example: santa cluster remove "Smith Family"
    """
    if storage.remove_cluster(cluster_name):
        console.print(f"✅ Removed cluster [bold red]{cluster_name}[/]")
    else:
        console.print(f"[red]Error:[/] Cluster '{cluster_name}' not found")
        raise SystemExit(1)


@cluster_group.command("kick")
@click.argument("cluster_name")
@click.argument("participant_name")
def remove_from_cluster(cluster_name: str, participant_name: str):
    """Remove a person from a cluster (they stay in the exchange).
    
    Example: santa cluster kick "Smith Family" "John"
    """
    try:
        storage.remove_from_cluster(cluster_name, participant_name)
        console.print(f"✅ Removed [bold cyan]{participant_name}[/] from cluster [bold blue]{cluster_name}[/]")
    except ValueError as e:
        console.print(f"[red]Error:[/] {e}")
        raise SystemExit(1)


# ============================================================================
# Assignment Commands
# ============================================================================

@cli.command("assign")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing assignments")
@click.option("--separate-kids", "-s", is_flag=True, help="Kids only match with other kids (default: random)")
def assign(force: bool, separate_kids: bool):
    """Generate random Secret Santa assignments."""
    existing = storage.get_assignments()
    
    if existing and not force:
        console.print("[yellow]Assignments already exist![/] Use --force to regenerate.")
        console.print("⚠️  This will overwrite current assignments.")
        return
    
    try:
        mode_msg = "[magenta]Kids match kids only[/]" if separate_kids else "[cyan]Random matching[/]"
        with console.status(f"[bold green]Generating assignments... ({mode_msg})"):
            assignments = create_assignments(storage, separate_kids=separate_kids)
        
        storage.save_assignments(assignments)
        
        console.print(f"\n[bold green]🎉 Assignments generated![/] ({mode_msg})\n")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Giver", style="cyan")
        table.add_column("→", justify="center", style="dim")
        table.add_column("Receiver", style="green")
        
        for a in assignments:
            table.add_row(a.giver_name, "🎁", a.receiver_name)
        
        console.print(table)
        console.print("\n[dim]Run 'santa send' to email everyone their assignments.[/]")
        
    except MatcherError as e:
        console.print(f"[red]Error:[/] {e}")
        raise SystemExit(1)


@cli.command("send")
@click.option("--dry-run", "-n", is_flag=True, help="Preview emails without sending")
def send(dry_run: bool):
    """Send assignment emails to all participants."""
    assignments = storage.get_assignments()
    config = storage.get_config()
    
    if not assignments:
        console.print("[yellow]No assignments yet.[/] Run 'santa assign' first.")
        return
    
    if not config.brevo_api_key and not dry_run:
        console.print("[red]Error:[/] Email not configured. Run: santa config")
        return
    
    if dry_run:
        console.print("[bold yellow]🔍 DRY RUN MODE[/] - No emails will be sent\n")
    
    def on_progress(assignment, result):
        status = result.get("status", "unknown")
        if status == "sent":
            console.print(f"  ✅ Sent to {assignment.giver_name} ({assignment.giver_email})")
        elif status == "would_send":
            console.print(f"  📧 Would send to {assignment.giver_name} ({assignment.giver_email})")
        elif status == "already_sent":
            console.print(f"  ⏭️  Already sent to {assignment.giver_name}")
        else:
            console.print(f"  ❌ Failed: {assignment.giver_name} - {result.get('error', 'Unknown error')}")
    
    console.print("[bold]Sending emails...[/]\n")
    
    try:
        results = send_all_assignments(
            assignments,
            config,
            dry_run=dry_run,
            on_progress=on_progress
        )
        
        # Mark sent emails in storage
        if not dry_run:
            for assignment, result in zip(assignments, results):
                if result.get("status") == "sent":
                    storage.mark_email_sent(assignment.giver_id)
        
        sent = sum(1 for r in results if r.get("status") in ("sent", "would_send"))
        console.print(f"\n[bold green]Done![/] {sent}/{len(assignments)} emails {'would be sent' if dry_run else 'sent'}.")
        
    except EmailError as e:
        console.print(f"[red]Error:[/] {e}")
        raise SystemExit(1)


# ============================================================================
# Config Command
# ============================================================================

@cli.command("config")
@click.option("--api-key", "-k", help="Brevo API key")
@click.option("--sender-email", "-e", help="Sender email address")
@click.option("--sender-name", "-n", help="Sender display name")
@click.option("--show", "-s", is_flag=True, help="Show current config")
def config_cmd(api_key: str, sender_email: str, sender_name: str, show: bool):
    """Configure email settings for Secret Santa notifications."""
    current = storage.get_config()
    
    if show:
        console.print("\n[bold]Current Configuration:[/]\n")
        console.print(f"  API Key:      {'*' * 20 if current.brevo_api_key else '[red]Not set[/]'}")
        console.print(f"  Sender Email: {current.sender_email or '[red]Not set[/]'}")
        console.print(f"  Sender Name:  {current.sender_name}")
        console.print("\nGet your free Brevo API key at: [link=https://www.brevo.com/]https://www.brevo.com/[/]")
        return
    
    if not any([api_key, sender_email, sender_name]):
        console.print("Use --api-key, --sender-email, or --sender-name to configure.")
        console.print("Use --show to view current configuration.")
        return
    
    if api_key:
        current.brevo_api_key = api_key
        console.print("✅ API key saved")
    
    if sender_email:
        current.sender_email = sender_email
        console.print(f"✅ Sender email set to: {sender_email}")
    
    if sender_name:
        current.sender_name = sender_name
        console.print(f"✅ Sender name set to: {sender_name}")
    
    storage.save_config(current)


@cli.command("clear")
@click.confirmation_option(prompt="Are you sure you want to clear ALL data?")
def clear_all():
    """Clear all participants, clusters, and assignments."""
    import shutil
    data_dir = storage.data_dir
    if data_dir.exists():
        shutil.rmtree(data_dir)
    console.print("✅ All data cleared!")


if __name__ == "__main__":
    cli()
