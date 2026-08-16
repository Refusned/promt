#!/usr/bin/env python3
"""Validate the portable skill and the exact public Git index."""

from pathlib import Path
import re
import subprocess
import sys
from typing import NoReturn

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "promt"
SKILL_FILE = SKILL_DIR / "SKILL.md"
README_FILE = ROOT / "README.md"
README_RU_FILE = ROOT / "README.ru.md"
BEHAVIOR_CASES_FILE = ROOT / "tests" / "behavior_cases.md"

EXPECTED_TRACKED_FILES = {
    ".gitattributes",
    ".github/workflows/validate.yml",
    ".gitignore",
    "LICENSE",
    "README.md",
    "README.ru.md",
    "requirements-test.txt",
    "skills/promt/SKILL.md",
    "tests/behavior_cases.md",
    "tests/validate_skill.py",
}
EXPECTED_COMMIT_EMAIL = "250112418+Refusned@users.noreply.github.com"


def fail(message: str) -> NoReturn:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


if not SKILL_FILE.is_file():
    fail(f"missing {SKILL_FILE.relative_to(ROOT)}")

text = SKILL_FILE.read_text(encoding="utf-8")
match = re.match(
    r"\A---\r?\n(?P<frontmatter>.*?)\r?\n---\r?\n",
    text,
    flags=re.DOTALL,
)
if match is None:
    fail("SKILL.md must start with a YAML frontmatter block")

try:
    fields = yaml.safe_load(match.group("frontmatter"))
except yaml.YAMLError as error:
    fail(f"invalid YAML frontmatter: {error}")

if not isinstance(fields, dict):
    fail("frontmatter must be a YAML mapping")
if set(fields) != {"name", "description"}:
    fail("portable frontmatter must contain only name and description")

name = fields["name"]
description = fields["description"]
if not isinstance(name, str) or not re.fullmatch(
    r"[a-z0-9]+(?:-[a-z0-9]+)*", name
):
    fail("name must use lowercase ASCII letters, digits, and hyphens")
if len(name) > 64:
    fail("name exceeds 64 characters")
if name != SKILL_DIR.name:
    fail("name must match the skill directory")
if not isinstance(description, str) or not 1 <= len(description) <= 1024:
    fail("description must contain 1 to 1024 characters")
for required in ("Использовать", "Use when", "Не использовать", "Do not use"):
    if required.casefold() not in description.casefold():
        fail(f"description is missing bilingual trigger boundary {required!r}")

if "TODO" in text:
    fail("SKILL.md contains a TODO placeholder")
if len(text.splitlines()) >= 500:
    fail("SKILL.md must stay below 500 lines")
if not re.search(r"<!-- promt-version: [1-9][0-9]* -->", text):
    fail("SKILL.md is missing a valid promt-version marker")
if (SKILL_DIR / "agents" / "openai.yaml").exists():
    fail("portable skill must not contain agents/openai.yaml")

if not README_FILE.is_file():
    fail("missing README.md")
readme = README_FILE.read_text(encoding="utf-8")
for required in (
    "$promt",
    "/promt",
    "skills/promt/SKILL.md",
    "https://learn.chatgpt.com/docs/build-skills",
    "https://code.claude.com/docs/en/slash-commands",
):
    if required not in readme:
        fail(f"README is missing {required!r}")

if not README_RU_FILE.is_file():
    fail("missing README.ru.md")
readme_ru = README_RU_FILE.read_text(encoding="utf-8")
for required in (
    "README.md",
    "$promt",
    "/promt",
    "skills/promt/SKILL.md",
    "https://learn.chatgpt.com/docs/build-skills",
    "https://code.claude.com/docs/en/slash-commands",
):
    if required not in readme_ru:
        fail(f"README.ru.md is missing {required!r}")

for heading_level in (2, 3):
    marker = "#" * heading_level + " "
    en_count = sum(line.startswith(marker) for line in readme.splitlines())
    ru_count = sum(line.startswith(marker) for line in readme_ru.splitlines())
    if en_count != ru_count:
        fail(
            f"README language structure differs at H{heading_level}: "
            f"English={en_count}, Russian={ru_count}"
        )

if not BEHAVIOR_CASES_FILE.is_file():
    fail("missing tests/behavior_cases.md")

try:
    tracked_result = subprocess.run(
        ["git", "ls-files", "--cached", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
except FileNotFoundError:
    fail("git is required for the tracked-index check")
except subprocess.CalledProcessError as error:
    fail(f"git index is unavailable: exit {error.returncode}")
tracked_files = {
    item.decode("utf-8")
    for item in tracked_result.stdout.split(b"\0")
    if item
}
if tracked_files != EXPECTED_TRACKED_FILES:
    missing = sorted(EXPECTED_TRACKED_FILES - tracked_files)
    extra = sorted(tracked_files - EXPECTED_TRACKED_FILES)
    fail(f"unexpected Git index; missing={missing}, extra={extra}")

head_probe = subprocess.run(
    ["git", "rev-parse", "--verify", "HEAD"],
    cwd=ROOT,
    check=False,
    capture_output=True,
)
if head_probe.returncode == 0:
    cached_diff = subprocess.run(
        ["git", "diff", "--quiet", "--cached", "HEAD", "--"],
        cwd=ROOT,
        check=False,
    )
    if cached_diff.returncode == 0:
        head_tree = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", "-z", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
        head_files = {
            item.decode("utf-8")
            for item in head_tree.stdout.split(b"\0")
            if item
        }
        if head_files != EXPECTED_TRACKED_FILES:
            fail("HEAD tree does not match the expected public file set")
        commit_emails = subprocess.run(
            ["git", "log", "-1", "--format=%ae%n%ce", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        if set(commit_emails) != {EXPECTED_COMMIT_EMAIL}:
            fail("HEAD author or committer does not use the expected GitHub noreply email")

worktree_diff = subprocess.run(
    ["git", "diff", "--quiet", "--"],
    cwd=ROOT,
    check=False,
)
if worktree_diff.returncode != 0:
    fail("worktree differs from the staged index")

literal_forbidden = {
    "absolute macOS home path": "/" + "Users/",
    "absolute Linux home path": "/" + "home/",
    "absolute Windows home path": "C:" + "\\Users\\",
}
secret_patterns = {
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "GitHub token": re.compile(
        r"\b(?:ghp|gho|github_pat)_[A-Za-z0-9_-]{8,}"
    ),
    "OpenAI token": re.compile(
        r"\b" + "sk" + r"-(?:proj-)?[A-Za-z0-9_-]{8,}"
    ),
    "Anthropic token": re.compile(
        r"\b" + "sk" + r"-ant-[A-Za-z0-9_-]{8,}"
    ),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Slack token": re.compile(
        r"\b" + "xox" + r"[baprs]-[A-Za-z0-9-]{8,}"
    ),
}
email_pattern = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

for relative_path in sorted(tracked_files):
    path = ROOT / relative_path
    if path.name.startswith(".env") and path.name != ".env.example":
        fail(f"tracked secret-like file: {relative_path}")
    try:
        blob = subprocess.run(
            ["git", "show", f":{relative_path}"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as error:
        fail(f"cannot read staged blob {relative_path}: exit {error.returncode}")
    raw = blob.stdout
    if b"\0" in raw:
        continue
    try:
        candidate = raw.decode("utf-8")
    except UnicodeDecodeError:
        fail(f"tracked text is not valid UTF-8: {relative_path}")
    for label, needle in literal_forbidden.items():
        if needle in candidate:
            fail(f"{relative_path} contains {label}")
    for label, pattern in secret_patterns.items():
        if pattern.search(candidate):
            fail(f"{relative_path} contains a possible {label}")
    unexpected_emails = {
        email
        for email in email_pattern.findall(candidate)
        if email != EXPECTED_COMMIT_EMAIL
    }
    if unexpected_emails:
        fail(f"{relative_path} contains unexpected email addresses")

print(
    "PASS: YAML frontmatter, expected Git index, documented links, "
    "local-path scan, and common-secret scan are valid "
    f"(description={len(description)} characters/{len(description.encode('utf-8'))} bytes)"
)
