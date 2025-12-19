# 🎅 Secret Santa CLI

A beautiful command-line tool for organizing Secret Santa gift exchanges with family exclusions.

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║    ███████╗███████╗ ██████╗██████╗ ███████╗████████╗                      ║
║    ██╔════╝██╔════╝██╔════╝██╔══██╗██╔════╝╚══██╔══╝                      ║
║    ███████╗█████╗  ██║     ██████╔╝█████╗     ██║                         ║
║    ╚════██║██╔══╝  ██║     ██╔══██╗██╔══╝     ██║                         ║
║    ███████║███████╗╚██████╗██║  ██║███████╗   ██║                         ║
║    ╚══════╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝   ╚═╝                         ║
║                                                                           ║
║         ███████╗ █████╗ ███╗   ██╗████████╗ █████╗                        ║
║         ██╔════╝██╔══██╗████╗  ██║╚══██╔══╝██╔══██╗                       ║
║         ███████╗███████║██╔██╗ ██║   ██║   ███████║                       ║
║         ╚════██║██╔══██║██║╚██╗██║   ██║   ██╔══██║                       ║
║         ███████║██║  ██║██║ ╚████║   ██║   ██║  ██║                       ║
║         ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝                       ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

## ✨ Features

- 🎁 **Random matching** with cluster exclusions (family members don't match)
- 👶 **Kids-only matching** - Optional `--separate-kids` so kids only match kids
- 👨‍👩‍👧‍👦 **Family groups** - Prevent matching within families
- 📧 **Email notifications** via Brevo (free tier: 300 emails/day)
- 👨‍👧 **Parent notifications for kids** - When you add a kid, the parent receives the email showing their child's assignment
- 🔐 **Verification codes** - Each assignment includes a unique 4-character code
- 🎨 **Festive terminal UI** with status dashboard

---

## 📦 Install

### Windows
```powershell
git clone https://github.com/Jericoz-JC/Secret-Santa-CLI.git && cd Secret-Santa-CLI && pip install -e .
```

### macOS / Linux
```bash
git clone https://github.com/Jericoz-JC/Secret-Santa-CLI.git && cd Secret-Santa-CLI && pip3 install -e .
```

Then run: `santa`

> **Windows tip:** Run `$env:PYTHONUTF8=1` first for emoji support.

---

## 🚀 Quick Start

```bash
# 1. Add participants (use --cluster for one-step family grouping!)
santa add "Alice" "alice@example.com" --cluster "Smith Family"
santa add "Bob" "bob@example.com" --cluster "Smith Family"

# 2. Add kids (email goes to parent, shows child's assignment)
santa add "Timmy" "parent@example.com" --kid --cluster "Smith Family"

# 3. Generate matches
santa assign                  # Random matching
santa assign --separate-kids  # Kids only match kids

# 4. Configure email (brevo.com for free API key)
santa config --api-key "YOUR_KEY" --sender-email "your@email.com"

# 5. Send emails
santa send --dry-run   # Preview first
santa send             # Send for real
```

---

## 📖 All Commands

### 👤 People
| Command | Description |
|---------|-------------|
| `santa add "name" "email"` | Add a participant |
| `santa add ... --kid` | Mark as a kid (parent receives email) |
| `santa add ... --cluster "name"` | Add and assign to cluster in one step |
| `santa add ... --parent-email "email"` | CC parent on assignment |
| `santa list` | View all participants |
| `santa remove "name"` | Remove someone |

### 👨‍👩‍👧‍👦 Family Groups
| Command | Description |
|---------|-------------|
| `santa clusters` | Quick view all groups |
| `santa cluster create "name"` | Create exclusion group |
| `santa cluster add "group" "name"` | Add person to group |
| `santa cluster list` | View all groups (same as `clusters`) |
| `santa cluster kick "group" "name"` | Remove person from group |
| `santa cluster remove "name"` | Delete entire group |

### 🎁 Matching & Email
| Command | Description |
|---------|-------------|
| `santa assign` | Generate random matches |
| `santa assign --separate-kids` | Kids only match with kids |
| `santa send --dry-run` | Preview emails |
| `santa send` | Send all emails |
| `santa config --api-key "KEY"` | Set Brevo API key |
| `santa config --sender-email "email"` | Set sender email |
| `santa config --show` | View current config |

### ⚙️ Other
| Command | Description |
|---------|-------------|
| `santa` | Show welcome screen |
| `santa clear` | Delete all data |
| `santa --help` | Full command reference |

---

## 👶 Kids & Parent Notifications

When you add a participant with `--kid`, the assignment email goes to the provided email address (typically the parent's) with special parent-friendly content:

- Shows "Your child **[Kid Name]** is buying a gift for: **[Receiver]**"
- Includes helping them keep it a secret
- Same verification code and gift limit info

```bash
# The email address should be the parent's email
santa add "Tommy" "parent@example.com" --kid
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE)


