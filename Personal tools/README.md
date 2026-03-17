# 🔐 Password Strength Checker

A lightweight, dependency-free command-line tool that evaluates password strength against industry-standard security rules and optionally checks passwords against the **rockyou.txt** leaked password wordlist.

---

## Features

- ✅ Eight weighted security rules with per-rule feedback
- 📊 Color-coded strength bar with percentage score (Weak / Fair / Good / Strong)
- 🔒 Secure hidden input via `getpass` — your password is never echoed to the terminal
- 📋 Optional wordlist check against `rockyou.txt` or any custom wordlist
- 🐍 Zero dependencies — pure Python 3.10+ standard library

---

## Requirements

- Python **3.10 or higher**
- No third-party packages required

Verify your Python version:

```bash
python --version
```

---

## Installation

No installation needed. Just download the script and run it:

```bash
# Clone or download the file
curl -O https://your-host/password_checker.py

# Make it executable (Linux / macOS)
chmod +x password_checker.py
```

---

## Usage

### Interactive Mode *(recommended)*

Run without arguments to be securely prompted for a password. The input is hidden while you type:

```bash
python password_checker.py
```

```
  Password Strength Checker
  ─────────────────────────
  Enter password (hidden):
```

---

### Pass Password Directly

```bash
python password_checker.py --password "MyP@ssw0rd!"
# or short form
python password_checker.py -p "MyP@ssw0rd!"
```

> ⚠️ **Security note:** Passing passwords via `--password` may expose them in your shell history. Prefer interactive mode for sensitive use.

---

### Check Against a Wordlist

Supply a path to `rockyou.txt` (or any newline-separated wordlist) to flag passwords that appear in known breach data:

```bash
python password_checker.py --wordlist /path/to/rockyou.txt
# or short form
python password_checker.py -w rockyou.txt
```

Both flags can be combined:

```bash
python password_checker.py -p "hunter2" -w rockyou.txt
```

---

### Show Password in Plain Text

By default the report masks the password. Use `--show` to display it in full:

```bash
python password_checker.py --show
```

---

## All Options

| Flag | Short | Description |
|---|---|---|
| `--password TEXT` | `-p` | Password to check (omit to be prompted securely) |
| `--wordlist FILE` | `-w` | Path to `rockyou.txt` or any newline-separated wordlist |
| `--show` | | Display password in plain text in the report |
| `--help` | `-h` | Show help message and exit |

---

## Scoring Rules

Passwords are scored out of **10 points** across eight rules. Each rule carries a weight that reflects its security impact:

| Rule | Points |
|---|---|
| At least 8 characters | 2 |
| At least 12 characters *(recommended)* | 1 |
| Contains uppercase letter (A–Z) | 1 |
| Contains lowercase letter (a–z) | 1 |
| Contains a number (0–9) | 1 |
| Contains a symbol (`!@#$%^&*` …) | 2 |
| No leading/trailing whitespace | 1 |
| No character repeated 3+ times in a row | 1 |

### Strength Tiers

| Score | Tier |
|---|---|
| 0–39% | 🔴 Weak |
| 40–64% | 🟡 Fair |
| 65–84% | 🔵 Good |
| 85–100% | 🟢 Strong |

---

## Sample Output

```
  ╔══════════════════════════════════════╗
  ║     PASSWORD STRENGTH CHECKER        ║
  ╚══════════════════════════════════════╝

  Password : My************
  Length   : 14 characters

  Strength : [██████████████████████████████]  Strong  (100%)

  Rules:
  ✔  At least 8 characters                      (+2)
  ✔  At least 12 characters (recommended)       (+1)
  ✔  Contains uppercase letter (A-Z)            (+1)
  ✔  Contains lowercase letter (a-z)            (+1)
  ✔  Contains a number (0-9)                    (+1)
  ✔  Contains a symbol (!@#$...)                (+2)
  ✔  No leading/trailing whitespace             (+1)
  ✔  No character repeated 3+ times in a row    (+1)

  Verdict: Strong
  Great password! Make sure you store it safely.
```

---

## Getting rockyou.txt

`rockyou.txt` is a well-known dataset of over 14 million real-world leaked passwords. A few ways to obtain it:

**Kali Linux** — pre-installed, just decompress:
```bash
gunzip /usr/share/wordlists/rockyou.txt.gz
```

**SecLists** — community wordlist collection:
```bash
git clone --depth 1 https://github.com/danielmiessler/SecLists.git
# File location:
# SecLists/Passwords/Leaked-Databases/rockyou.txt.tar.gz
```

Any plain text file with one password per line works as a wordlist — it does not have to be `rockyou.txt`.

---

## Examples

```bash
# Secure interactive prompt
python password_checker.py

# Quick inline check
python password_checker.py -p "correct-horse-battery"

# Full check with wordlist
python password_checker.py -p "sunshine1" -w rockyou.txt

# Show password in report + wordlist check
python password_checker.py --show -w /usr/share/wordlists/rockyou.txt
```

---

## Privacy & Security

- Passwords are **never written to disk**, logged, or transmitted anywhere.
- The wordlist check is performed **entirely offline** — no network access is made.
- When using interactive mode, Python's `getpass` module suppresses terminal echo so the password is not visible.

---

## License

This project is released into the public domain. Use freely, modify openly.
