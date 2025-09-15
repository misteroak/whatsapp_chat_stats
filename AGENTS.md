# AGENTS.md — Collaboration Guide for Codex CLI Agents

This repository uses Codex CLI to collaborate with AI coding agents. This guide defines how agents and humans work together here: approvals, safety, coding standards, and response conventions. Keep changes minimal and focused; ask when unsure.

## Audience & Scope
- For: AI agents and maintainers collaborating via Codex CLI.
- Covers: How to plan work, use tools, edit files, validate changes, and hand off results.
- Defaults: Workspace-write filesystem, restricted network, on-request approvals (may vary per session).

---

## Quick Start (for Agents)
1) Decide if a plan is needed.
   - Simple, single-step tasks: no plan.
   - Multi-step or ambiguous tasks: use the `update_plan` tool.

2) Announce actions before tool calls.
   - One short preamble sentence grouping related actions (8–12 words).

3) Prefer fast reads and small chunks.
   - Use `rg` for search; read files in <=250-line chunks.

4) Edit files with `apply_patch` only.
   - Do not use ad-hoc shell redirection to write files.

5) Validate changes where practical.
   - Run narrow tests or commands relevant to your edits. Avoid slow/global runs unless requested.

6) Summarize and propose next steps.
   - Keep final messages concise, structured, and actionable.

---

## Approvals, Sandbox, and Safety
- Mode: on-request
  - Run normally in sandbox; request escalation only if needed (e.g., network access or writing outside workspace).
- Filesystem: workspace-write
  - You may read and write within this repo. Do not modify outside the workspace.
- Network: restricted
  - Any command requiring network access must be explicitly approved. Provide a one-sentence justification.
- Destructive actions
  - Ask before `rm`, `git reset`, large refactors, or anything that could lose state.
- GUI/open
  - Opening external apps or links requires approval.

When escalation is required, state:
```
- Command(s): what you plan to run
- Reason: why escalation is necessary
- Alternatives: if any safe workaround exists
```

---

## Tooling Conventions
- Preambles: Always send a brief note before grouped tool calls.
- Search: Use `rg`/`rg --files` (fallback to `grep`/`find` if unavailable).
- File edits: Use `apply_patch` with minimal diffs; include only the intended changes.
- Reading files: Limit outputs to <=250 lines per read.
- Plans: Use `update_plan` only for non-trivial, multi-step tasks. Keep steps short (5–7 words), one `in_progress` at a time.

---

## Coding Standards
- Scope: Fix the root cause relevant to the task; avoid unrelated changes.
- Style: Match existing patterns; keep code simple and focused.
- Comments: Avoid inline comments unless the user asks for them.
- Naming: Avoid single-letter variables unless contextually conventional.
- Licenses: Do not add copyright/license headers unless asked.
- Citations/Formatting: Do not include bracketed citations or ANSI codes in responses.
- File creation: Reference files using clickable paths and 1-based line numbers.

---

## Responses: Structure and Tone
- Headers: Use when helpful, 1–3 words, `**Title Case**`.
- Bullets: `- ` followed by bold keyword and short description.
- Monospace: Wrap commands, file paths, env vars, and code identifiers in backticks.
- File references: Use standalone, clickable paths with optional `:line`.
  - Examples: `src/app.ts`, `src/app.ts:42`, `b/server/index.js#L10`.
- Voice: Concise, friendly, and factual. Present tense, active voice.

Example final message outline:
```
**What Changed**
- Summary: concise description of edits and rationale.

**Files**
- `path/to/file.ext:line`: short note on change.

**Next Steps**
- Suggest: tests to run, config to update, or follow-ups.
```

---

## Validation Philosophy
- Specific first: Verify only what you changed, then expand scope if needed.
- Don’t add new frameworks/tools just to validate.
- If tests exist nearby, run them; otherwise, propose a light check.
- In non-interactive modes, be proactive; in on-request, confirm before heavy runs.

---

## Git Practices
- Default: Do not commit unless explicitly requested.
- If asked to commit:
  - Branch naming: `feat/…`, `fix/…`, `chore/…` as appropriate.
  - Conventional Commits style is preferred:
    - `feat: add X`
    - `fix: correct Y`
    - `docs: update Z`
- Initial repo setup: add `.gitignore`, `README.md`, and make an initial commit upon request.

---

## Security & Privacy
- Do not check secrets or tokens into the repo.
- Do not fetch from the network without approval or necessity.
- Avoid printing large environment dumps or tokens in logs.

---

## When to Ask vs. Act
- Ask when:
  - Requirements are ambiguous; multiple viable designs exist.
  - The task implies destructive changes or external dependencies.
  - You need approvals for network or non-workspace writes.
- Act when:
  - The task is small, local, and reversible.
  - The change is clearly scoped and consistent with existing patterns.

---

## Handy Templates

Preamble examples:
```
"I’ll add the parser and wire tests."
"Explored the repo; now updating API routes."
"Next, I’ll scaffold CLI commands and helpers."
```

Plan example (good):
```
1. Add CLI entry with args
2. Parse Markdown via CommonMark
3. Apply semantic HTML template
4. Handle code blocks/images/links
5. Add error handling
```

Escalation request example:
```
- Command: npm install
- Reason: Need dependency to run tests
- Alternatives: Skip tests or use vendored lockfile (none available)
```

Final message example:
```
**What Changed**
- Implemented X with Y approach; minimal surface area; added tests.

**Files**
- `src/x.ts:1`: new module with core logic.
- `test/x.test.ts:1`: coverage for edge cases.

**Next Steps**
- Run `npm test` locally; confirm Node 18+.
```

---

## Repo-Specific Notes
- Project: `whatsapp_chat_stats` — WhatsApp chat analytics dashboard.
- Overview: Lightweight dashboard built with Python and Dash. Input is a
  folder containing WhatsApp chat exports; chats may be split across multiple
  files and should be merged during parsing.
- Visualizations: Interactive stats like who texts more, common words,
  top emojis, and activity over time.
- Stack: Python + Dash (Plotly).

- Dash styling preference:
  - Keep layout and component styling in CSS under `assets/styles.css`.
  - Avoid inline Dash `style={...}` except for dynamic, data-driven tweaks.
  - Use meaningful `className`s on components and group rules in CSS.
  - Plotly figure styling (e.g., `update_layout`) remains in Python.

- Suggested bootstrap:
  - Add a Python-focused `.gitignore`.
  - Create `README.md` with quick start instructions.
  - Scaffold a minimal Dash app (`app.py`) and a parser module.
  - Configure any formatters or linters you plan to use.

If you want me to generate these bootstrap files (Dash app + parser), ask.

---

## FAQ
- Can the agent run networked commands? Only with approval in this setup.
- Will the agent commit code? Not unless explicitly asked to commit.
- How verbose should responses be? Default to concise, increase detail when helpful.
- How are files edited? Exclusively via `apply_patch` patches.

---

## Changelog
- v1: Initial AGENTS.md scaffold for Codex CLI collaboration.
