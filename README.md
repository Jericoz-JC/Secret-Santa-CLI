# 🎅 Secret Santa CLI

A beautiful command-line tool for organizing Secret Santa gift exchanges.

```
╔═══════════════════════════════════════════════════════╗
║ ███████╗███████╗ ██████╗██████╗ ███████╗████████╗   ║
║ ██╔════╝██╔════╝██╔════╝██╔══██╗██╔════╝╚══██╔══╝   ║
║ ███████╗█████╗  ██║     ██████╔╝█████╗     ██║      ║
║ ╚════██║██╔══╝  ██║     ██╔══██╗██╔══╝     ██║      ║
║ ███████║███████╗╚██████╗██║  ██║███████╗   ██║      ║
║ ╚══════╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝   ╚═╝      ║
║                                                       ║
║    ███████╗ █████╗ ███╗   ██╗████████╗ █████╗        ║
║    ██╔════╝██╔══██╗████╗  ██║╚══██╔══╝██╔══██╗       ║
║    ███████╗███████║██╔██╗ ██║   ██║   ███████║       ║
║    ╚════██║██╔══██║██║╚██╗██║   ██║   ██╔══██║       ║
║    ███████║██║  ██║██║ ╚████║   ██║   ██║  ██║       ║
║    ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝       ║
╚═══════════════════════════════════════════════════════╝
```

## ✨ Features

- 🎁 Random matching with cluster exclusions (family members don't match)
- 📧 Email notifications via Brevo (free tier: 300 emails/day)
- 👨‍👧 Parent CC option for children's assignments
- 🎨 Beautiful festive terminal UI

---

## 📦 One-Click Install

### Windows
```powershell
git clone https://github.com/Jericoz-JC/Secret-Santa-CLI.git && cd Secret-Santa-CLI && pip install -e .
```

### macOS / Linux
```bash
git clone https://github.com/Jericoz-JC/Secret-Santa-CLI.git && cd Secret-Santa-CLI && pip3 install -e .
```

Then run:
```bash
santa
```

> **Note:** On Windows, run `$env:PYTHONUTF8=1` first for emoji support.

---

## 🚀 Quick Start

```bash
# Add participants
santa add "Alice" "alice@example.com"
santa add "Bob" "bob@example.com"
santa add "Timmy" "timmy@example.com" --parent-email "parent@example.com"

# Create exclusion groups (prevent matching)
santa cluster create "Smith Family"
santa cluster add "Smith Family" "Alice"
santa cluster add "Smith Family" "Bob"

# Generate random assignments
santa assign

# Configure email (get free API key at brevo.com)
santa config --api-key "YOUR_KEY" --sender-email "your@email.com"

# Send emails
santa send --dry-run   # preview first
santa send             # send for real
```

---

## 📖 Commands

| Command | Description |
|---------|-------------|
| `santa` | Show welcome screen |
| `santa add "name" "email"` | Add participant |
| `santa list` | View all participants |
| `santa remove "name"` | Remove participant |
| `santa cluster create "name"` | Create exclusion group |
| `santa cluster add "group" "name"` | Add to group |
| `santa cluster list` | View groups |
| `santa assign` | Generate matches |
| `santa send` | Send emails |
| `santa config --show` | View config |
| `santa clear` | Delete all data |

---

## 📄 License

MIT License - see [LICENSE](LICENSE)
