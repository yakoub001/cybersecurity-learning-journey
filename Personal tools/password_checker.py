#!/usr/bin/env python3
"""
Password Strength Checker
Checks passwords against common rules and optionally against rockyou.txt.
"""

import re
import sys
import argparse
import getpass
from pathlib import Path


# ─── ANSI Colors ────────────────────────────────────────────────────────────

class Color:
    RED    = "\033[91m"
    YELLOW = "\033[93m"
    GREEN  = "\033[92m"
    CYAN   = "\033[96m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    RESET  = "\033[0m"

def c(text, *codes):
    return "".join(codes) + str(text) + Color.RESET


# ─── Rules ──────────────────────────────────────────────────────────────────

RULES = [
    {
        "id":      "length",
        "label":   "At least 8 characters",
        "check":   lambda p: len(p) >= 8,
        "weight":  2,
    },
    {
        "id":      "length_strong",
        "label":   "At least 12 characters (recommended)",
        "check":   lambda p: len(p) >= 12,
        "weight":  1,
    },
    {
        "id":      "uppercase",
        "label":   "Contains uppercase letter (A-Z)",
        "check":   lambda p: bool(re.search(r"[A-Z]", p)),
        "weight":  1,
    },
    {
        "id":      "lowercase",
        "label":   "Contains lowercase letter (a-z)",
        "check":   lambda p: bool(re.search(r"[a-z]", p)),
        "weight":  1,
    },
    {
        "id":      "digits",
        "label":   "Contains a number (0-9)",
        "check":   lambda p: bool(re.search(r"\d", p)),
        "weight":  1,
    },
    {
        "id":      "symbols",
        "label":   "Contains a symbol (!@#$...)",
        "check":   lambda p: bool(re.search(r"[^A-Za-z0-9]", p)),
        "weight":  2,
    },
    {
        "id":      "no_spaces",
        "label":   "No leading/trailing whitespace",
        "check":   lambda p: p == p.strip(),
        "weight":  1,
    },
    {
        "id":      "no_repeat",
        "label":   "No character repeated 3+ times in a row",
        "check":   lambda p: not bool(re.search(r"(.)\1{2,}", p)),
        "weight":  1,
    },
]

MAX_SCORE = sum(r["weight"] for r in RULES)


def score_password(password: str) -> tuple[int, list[dict]]:
    """Return (score, list of rule results)."""
    results = []
    total = 0
    for rule in RULES:
        passed = rule["check"](password)
        if passed:
            total += rule["weight"]
        results.append({**rule, "passed": passed})
    return total, results


def strength_label(score: int) -> tuple[str, str]:
    """Return (label, color) based on score."""
    ratio = score / MAX_SCORE
    if ratio < 0.40:
        return "Weak", Color.RED
    elif ratio < 0.65:
        return "Fair", Color.YELLOW
    elif ratio < 0.85:
        return "Good", Color.CYAN
    else:
        return "Strong", Color.GREEN


# ─── rockyou.txt check ──────────────────────────────────────────────────────

def load_wordlist(path: str) -> set[str]:
    p = Path(path)
    if not p.exists():
        print(c(f"  ✗ Wordlist not found: {path}", Color.RED))
        sys.exit(1)

    print(c(f"  Loading wordlist: {path} … ", Color.DIM), end="", flush=True)
    words: set[str] = set()
    try:
        with open(p, "r", encoding="latin-1", errors="replace") as f:
            for line in f:
                words.add(line.rstrip("\n"))
    except Exception as e:
        print(c(f"\n  Error reading wordlist: {e}", Color.RED))
        sys.exit(1)

    print(c(f"loaded {len(words):,} entries.", Color.DIM))
    return words


def check_wordlist(password: str, wordlist: set[str]) -> bool:
    """Return True if password is in the wordlist."""
    return password in wordlist


# ─── Display ────────────────────────────────────────────────────────────────

def progress_bar(score: int, width: int = 30) -> str:
    filled = round(width * score / MAX_SCORE)
    _, col = strength_label(score)
    bar = col + "█" * filled + Color.DIM + "░" * (width - filled) + Color.RESET
    return f"[{bar}]"


def print_report(password: str, score: int, results: list[dict],
                 wordlist: set[str] | None = None) -> None:

    label, col = strength_label(score)

    print()
    print(c("  ╔══════════════════════════════════════╗", Color.DIM))
    print(c("  ║     PASSWORD STRENGTH CHECKER        ║", Color.DIM))
    print(c("  ╚══════════════════════════════════════╝", Color.DIM))
    print()

    # Masked password display
    masked = password[:2] + "*" * (len(password) - 2) if len(password) > 2 else "**"
    print(f"  Password : {c(masked, Color.BOLD)}")
    print(f"  Length   : {len(password)} characters")
    print()

    # Strength bar
    bar = progress_bar(score)
    pct = round(100 * score / MAX_SCORE)
    print(f"  Strength : {bar}  {c(label, col, Color.BOLD)}  ({pct}%)")
    print()

    # Rule breakdown
    print(c("  Rules:", Color.BOLD))
    for r in results:
        icon = c("  ✔", Color.GREEN) if r["passed"] else c("  ✗", Color.RED)
        label_text = c(r["label"], Color.DIM if not r["passed"] else "")
        pts = f"  (+{r['weight']})" if r["passed"] else f"  ( 0/{r['weight']})"
        print(f"{icon}  {label_text}{c(pts, Color.DIM)}")

    # Wordlist check
    if wordlist is not None:
        print()
        print(c("  Wordlist check (rockyou.txt):", Color.BOLD))
        if check_wordlist(password, wordlist):
            print(c("  ✗  Password found in wordlist — VERY WEAK!", Color.RED, Color.BOLD))
        else:
            print(c("  ✔  Not found in wordlist.", Color.GREEN))

    print()

    # Final verdict
    label2, col2 = strength_label(score)
    if label2 == "Weak":
        tip = "Consider adding symbols, numbers, and making it longer."
    elif label2 == "Fair":
        tip = "Add more variety — symbols, mixed case, and length help."
    elif label2 == "Good":
        tip = "Almost there! A symbol or extra length would make it strong."
    else:
        tip = "Great password! Make sure you store it safely."

    print(f"  {c('Verdict:', Color.BOLD)} {c(label2, col2, Color.BOLD)}")
    print(f"  {c(tip, Color.DIM)}")
    print()


# ─── CLI ────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Check password strength against common rules.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python password_checker.py
  python password_checker.py --password "MyP@ssw0rd!"
  python password_checker.py --wordlist /path/to/rockyou.txt
  python password_checker.py -p "hunter2" -w rockyou.txt
        """,
    )
    p.add_argument(
        "-p", "--password",
        help="Password to check (omit to be prompted securely)",
    )
    p.add_argument(
        "-w", "--wordlist",
        metavar="FILE",
        help="Path to rockyou.txt (or any newline-separated wordlist)",
    )
    p.add_argument(
        "--show",
        action="store_true",
        help="Show the password in plain text in the report",
    )
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    print()
    print(c("  Password Strength Checker", Color.BOLD, Color.CYAN))
    print(c("  ─────────────────────────", Color.DIM))

    # Get password
    if args.password:
        password = args.password
    else:
        try:
            password = getpass.getpass("  Enter password (hidden): ")
        except KeyboardInterrupt:
            print("\n  Aborted.")
            sys.exit(0)

    if not password:
        print(c("  No password entered.", Color.RED))
        sys.exit(1)

    # Load wordlist if requested
    wordlist: set[str] | None = None
    if args.wordlist:
        wordlist = load_wordlist(args.wordlist)

    # Run checks
    score, results = score_password(password)

    # If --show, temporarily restore for display
    if not args.show:
        # mask already done inside print_report
        pass

    print_report(password if args.show else password, score, results, wordlist)


if __name__ == "__main__":
    main()
