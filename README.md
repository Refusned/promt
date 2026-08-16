<div align="center">

# promt

**One rough idea in. One production-ready master prompt out.**

[![Agent Skill](https://img.shields.io/badge/Agent_Skill-open_standard-111827?style=for-the-badge)](https://agentskills.io/specification)
[![Codex](https://img.shields.io/badge/Codex-%24promt-0F766E?style=for-the-badge)](https://learn.chatgpt.com/docs/build-skills)
[![Claude Code](https://img.shields.io/badge/Claude_Code-%2Fpromt-C2410C?style=for-the-badge)](https://code.claude.com/docs/en/slash-commands)
[![MIT](https://img.shields.io/badge/License-MIT-2563EB?style=for-the-badge)](LICENSE)

[![Validate skill](https://github.com/refusned/promt/actions/workflows/validate.yml/badge.svg)](https://github.com/refusned/promt/actions/workflows/validate.yml)

**English** | [Русский](README.ru.md)

</div>

`promt` turns a short thought, idea, or rough brief into one self-contained master prompt for a fresh Codex, Claude Code, or other AI-agent session. The spelling is intentional.

It does not execute the original task. It packages the task with the right context, scope, safety boundaries, acceptance criteria, verification, and output format.

## See the difference

Input:

```text
$promt I want an agent that reviews pull requests and reports only material risks.
```

Output shape:

````text
Master prompt: material-risk pull request review
```text
Review the current pull request in read-only mode. Focus only on defects that can affect correctness, security, data integrity, or production behavior...
```
````

If a missing decision would materially change the result, `promt` asks focused questions first. Otherwise it returns the master prompt immediately.

## Why use it

| Capability | What it gives you |
|---|---|
| Intent preservation | Keeps the actual goal instead of inflating a one-line idea into generic prompt jargon |
| Adaptive depth | Produces a concise prompt for a simple request and a structured contract for a complex project |
| Project awareness | Uses relevant project instructions and files when they materially improve the prompt |
| Verifiable outcomes | Adds scope, non-goals, Definition of Done, checks, and evidence requirements when needed |
| Safety boundaries | Keeps secrets out and gates publishing, production, payments, destructive actions, and scope expansion |
| Portable core | Uses one shared `SKILL.md` in Codex and Claude Code, preserves the input language, and has bilingual discovery metadata |

## Use it

Codex:

```text
$promt <your idea or rough task>
```

Claude Code:

```text
/promt <your idea or rough task>
```

Examples:

```text
$promt Design a research agent that compares three CRM systems using primary sources.
```

```text
/promt Нужно исправить медленный поиск в текущем проекте и доказать улучшение замерами.
```

`/prompt` is not an alias. The command is intentionally named `promt`.

## Install on macOS or Linux

The installation uses one local clone as the source of truth. Each command refuses to replace an existing source or skill path.

### 1. Clone once

```bash
promt_source="${promt_source:-$HOME/.local/share/promt}"

if [ -e "$promt_source" ] || [ -L "$promt_source" ]; then
  printf 'Source already exists: %s\n' "$promt_source"
else
  git clone https://github.com/refusned/promt.git "$promt_source"
fi
```

### 2. Install for Codex

```bash
promt_source="${promt_source:-$HOME/.local/share/promt}"
promt_target="${promt_target:-$HOME/.agents/skills/promt}"

if [ ! -f "$promt_source/skills/promt/SKILL.md" ]; then
  printf 'SKILL.md was not found in %s\n' "$promt_source"
elif [ -e "$promt_target" ] || [ -L "$promt_target" ]; then
  printf 'Target already exists; refusing to replace it: %s\n' "$promt_target"
else
  mkdir -p "$(dirname "$promt_target")"
  ln -s "$promt_source/skills/promt" "$promt_target"
fi
```

Start a new Codex session and type `$promt`.

### 3. Install for Claude Code

```bash
promt_source="${promt_source:-$HOME/.local/share/promt}"
promt_target="${promt_target:-$HOME/.claude/skills/promt}"

if [ ! -f "$promt_source/skills/promt/SKILL.md" ]; then
  printf 'SKILL.md was not found in %s\n' "$promt_source"
elif [ -e "$promt_target" ] || [ -L "$promt_target" ]; then
  printf 'Target already exists; refusing to replace it: %s\n' "$promt_target"
else
  mkdir -p "$(dirname "$promt_target")"
  ln -s "$promt_source/skills/promt" "$promt_target"
fi
```

Start a new Claude Code session and run `/promt`.

Codex documents personal skills under `$HOME/.agents/skills`; Claude Code documents them under `$HOME/.claude/skills`. Both support symlinked skill directories. See the official [Codex skills guide](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills) and [Claude Code skills guide](https://code.claude.com/docs/en/slash-commands#where-skills-live).

### Project-scoped installation

Run this from the root of a trusted project to make the same skill available only there:

```bash
promt_source="${promt_source:-$HOME/.local/share/promt}"
promt_project_root="${promt_project_root:-$PWD}"

if [ ! -f "$promt_source/skills/promt/SKILL.md" ]; then
  printf 'SKILL.md was not found in %s\n' "$promt_source"
else
  for promt_target in \
    "$promt_project_root/.agents/skills/promt" \
    "$promt_project_root/.claude/skills/promt"
  do
    if [ -e "$promt_target" ] || [ -L "$promt_target" ]; then
      printf 'Target already exists; refusing to replace it: %s\n' "$promt_target"
    else
      mkdir -p "$(dirname "$promt_target")"
      ln -s "$promt_source/skills/promt" "$promt_target"
    fi
  done
fi
```

If symlinks are unavailable, copy the `skills/promt` directory into the applicable location. A copied installation must be updated separately.

### Windows

Windows installation has not been verified yet. Clone the repository, then copy `skills\promt` into a target that does not already exist:

- Codex: `%USERPROFILE%\.agents\skills\promt`
- Claude Code: `%USERPROFILE%\.claude\skills\promt`

## How it works

1. Detects the desired outcome and whether the task is read-only or allows local changes.
2. Reads limited project context only when it can materially improve the prompt.
3. Asks one to five questions only when an answer changes the result, scope, authority, acceptance criteria, or output.
4. Produces exactly one master prompt with no hidden execution of the original task.
5. Uses a dynamic outer fence, so generated prompts containing Markdown code blocks remain copyable.

The final prompt keeps external writes, production changes, spending, destructive operations, and scope expansion behind explicit approval. Secret values are replaced by placeholders such as `API_KEY`.

## Update safely

Review incoming changes before activating them:

```bash
promt_source="${promt_source:-$HOME/.local/share/promt}"
git -C "$promt_source" fetch origin
git -C "$promt_source" log --oneline HEAD..origin/main
git -C "$promt_source" diff --stat HEAD..origin/main
git -C "$promt_source" merge --ff-only origin/main
```

## Verify or remove

Verify an installation without changing it:

```bash
promt_target="${promt_target:-$HOME/.agents/skills/promt}"
if [ -e "$promt_target" ] || [ -L "$promt_target" ]; then
  ls -ld "$promt_target"
  test -f "$promt_target/SKILL.md"
else
  printf 'Skill path was not found: %s\n' "$promt_target"
fi
```

Remove only a symlink installation:

```bash
promt_target="${promt_target:-$HOME/.agents/skills/promt}"
if [ -L "$promt_target" ]; then
  unlink "$promt_target"
else
  printf 'Not a symlink; refusing to remove: %s\n' "$promt_target"
fi
```

For Claude Code, set `promt_target` to `$HOME/.claude/skills/promt`. Inspect copied directories manually before removing them.

Removing a link leaves the shared clone in place so another host can keep using it. Inspect that clone and any local changes before deleting it manually.

## Compatibility and verification

| Host and scope | Verified behavior |
|---|---|
| Codex CLI `0.146.0`, personal scope | Discovery and explicit `$promt` invocation from a fresh isolated project |
| Codex CLI `0.146.0`, project scope | Empty input, local mutation, secret placeholder, and nested-fence cases |
| Claude Code `2.1.177`, project scope | Read-only research, mandatory single-task choice, no-questions override, and nested-fence cases |
| Claude Code, personal scope | Install path is documented upstream, but the author has not installed it personally |
| Windows | Not verified |

Claude Code smoke tests ran with tools disabled. Project-scoped symlink discovery was tested for both hosts.

## Validate the repository

```bash
python3 -m pip install -r requirements-test.txt
python3 tests/validate_skill.py
```

The validator checks frontmatter, the exact public Git tree, documentation links, commit identity, UTF-8 text, local-path leakage, and common secret patterns. GitHub Actions runs the same check for every push and pull request.

## Repository layout

```text
.github/workflows/validate.yml  Continuous validation
README.md                       English documentation
README.ru.md                    Russian documentation
skills/promt/SKILL.md           Portable Agent Skill, Russian runtime body
tests/behavior_cases.md         Behavior and edge-case fixtures
tests/validate_skill.py         Structural and publication checks
```

`promt` follows the open [Agent Skills specification](https://agentskills.io/specification), the [Codex skills guidance](https://learn.chatgpt.com/docs/build-skills), and the current Claude Code guide [Extend Claude with skills](https://code.claude.com/docs/en/slash-commands).

## License

[MIT](LICENSE)
