# 🎅 Secret Santa CLI

A beautiful command-line tool for managing Secret Santa gift exchanges with cluster-based exclusions and email notifications.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey.svg)

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

- 🎁 **Random Matching** - Automatically pairs gift-givers with recipients
- 👨‍👩‍👧‍👦 **Cluster Exclusions** - Prevent family members from matching with each other
- 📧 **Email Notifications** - Send beautiful festive emails to all participants
- 👨‍👧 **Parent CC** - Parents can be CC'd on their child's assignment
- 🎨 **Beautiful CLI** - Rich terminal UI with colors and ASCII art
- 💾 **Persistent Storage** - Data saved locally in JSON format

---

## 📦 Installation

### Prerequisites

- **Python 3.10 or higher**
- **pip** (Python package manager)

---

### 🪟 Windows

#### Option 1: Install from PyPI (Recommended)
```powershell
pip install secret-santa-cli
```

#### Option 2: Install from Source
```powershell
# Clone the repository
git clone https://github.com/Jericoz-JC/Secret-Santa-CLI.git
cd Secret-Santa-CLI

# Install in editable mode
pip install -e .
```

#### Running on Windows
```powershell
# Set UTF-8 encoding for emoji support (run once per terminal session)
$env:PYTHONUTF8=1

# Run the app
santa
```

> **Tip**: Add `C:\Users\<YourUsername>\AppData\Roaming\Python\Python3XX\Scripts` to your PATH if `santa` command isn't found.

---

### 🍎 macOS

#### Option 1: Install from PyPI (Recommended)
```bash
pip3 install secret-santa-cli
```

#### Option 2: Install from Source
```bash
# Clone the repository
git clone https://github.com/Jericoz-JC/Secret-Santa-CLI.git
cd Secret-Santa-CLI

# Install in editable mode
pip3 install -e .
```

#### Running on macOS
```bash
santa
```

> **Note**: If you see `command not found: santa`, try `python3 -m secret_santa.cli` or add `~/.local/bin` to your PATH.

---

### 🐧 Linux

#### Option 1: Install from PyPI (Recommended)
```bash
pip install secret-santa-cli
```

#### Option 2: Install from Source
```bash
# Clone the repository
git clone https://github.com/Jericoz-JC/Secret-Santa-CLI.git
cd Secret-Santa-CLI

# Install in editable mode
pip install -e .
```

#### Running on Linux
```bash
santa
```

> **Note**: You may need to use `pip3` instead of `pip` on some distributions. If `santa` isn't found, add `~/.local/bin` to your PATH:
> ```bash
> echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
> source ~/.bashrc
> ```

---

## ⚙️ Configuration

Before sending emails, you need to set up a free Brevo (SendinBlue) account:

### 1. Get Your API Key
1. Sign up at [brevo.com](https://www.brevo.com/) (free tier: 300 emails/day)
2. Go to **SMTP & API** → **API Keys**
3. Create a new API key

### 2. Verify Sender Email
1. In Brevo, go to **Senders & IP** → **Senders**
2. Add and verify your email address

### 3. Configure the CLI
```bash
santa config --api-key "YOUR_API_KEY" --sender-email "your@email.com" --sender-name "Secret Santa"
```

### 4. Verify Configuration
```bash
santa config --show
```

---

## 🚀 Quick Start

### 1. Add Participants
```bash
# Basic participant
santa add "John Doe" "john@example.com"

# Child with parent CC (parent receives copy of child's assignment)
santa add "Little Timmy" "timmy@example.com" --parent-email "parent@example.com"
```

### 2. View All Participants
```bash
santa list
```

### 3. Create Exclusion Clusters
Clusters prevent people from being matched with each other (e.g., family members):

```bash
# Create a cluster
santa cluster create "Smith Family"

# Add members to the cluster
santa cluster add "Smith Family" "John Smith"
santa cluster add "Smith Family" "Jane Smith"

# View all clusters
santa cluster list
```

### 4. Generate Random Assignments
```bash
santa assign
```

### 5. Send Email Notifications
```bash
# Preview emails first (no actual sending)
santa send --dry-run

# Send for real
santa send
```

---

## 📖 All Commands

| Command | Description |
|---------|-------------|
| `santa` | Show welcome screen with status dashboard |
| `santa add <name> <email>` | Add a participant |
| `santa add <name> <email> -p <parent_email>` | Add participant with parent CC |
| `santa list` | Show all participants |
| `santa remove <name>` | Remove a participant |
| `santa cluster create <name>` | Create an exclusion cluster |
| `santa cluster add <cluster> <name>` | Add participant to cluster |
| `santa cluster list` | Show all clusters |
| `santa assign` | Generate random assignments |
| `santa assign --force` | Regenerate assignments |
| `santa send` | Send assignment emails |
| `santa send --dry-run` | Preview emails without sending |
| `santa config --show` | View current configuration |
| `santa config --api-key <key>` | Set Brevo API key |
| `santa config --sender-email <email>` | Set sender email |
| `santa clear` | Delete all data |
| `santa --help` | Show help |
| `santa --version` | Show version |

---

## 📁 Data Storage

Your data is stored locally in:

| Platform | Location |
|----------|----------|
| Windows | `C:\Users\<Username>\.secret-santa\data.json` |
| macOS | `~/.secret-santa/data.json` |
| Linux | `~/.secret-santa/data.json` |

---

## 🎨 Email Template

Recipients receive a beautiful festive HTML email:

```
┌────────────────────────────────────┐
│         ❄️ ⛄ ❄️                    │
│      🎄 Secret Santa 🎄            │
│      You've been matched!          │
│                                    │
│   ┌────────────────────────────┐   │
│   │  You are buying a gift for: │   │
│   │       🎁 John Doe 🎁        │   │
│   └────────────────────────────┘   │
│                                    │
│         🎄                         │
│   Remember: Keep it a secret! 🤫   │
│        Happy Holidays!             │
└────────────────────────────────────┘
```

---

## 🛠️ Development

### Setup Development Environment
```bash
git clone https://github.com/Jericoz-JC/Secret-Santa-CLI.git
cd Secret-Santa-CLI
pip install -e .
pip install pytest
```

### Run Tests
```bash
pytest tests/ -v
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Click](https://click.palletsprojects.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Beautiful terminal formatting
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [Brevo](https://www.brevo.com/) - Email API

---

Made with ❤️ for the holiday season 🎄
