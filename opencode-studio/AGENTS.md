# Agent Contract

## Read first, every session
Before doing anything else, read `CHARTER.md` and `.ai/MEMORY.md`.
State the project mission in one sentence before you propose any action.
When this file and the charter disagree, the charter wins.

## Zones
- Workspace, you may edit: `artifact/`
- Read-only, ask before editing: `CHARTER.md`, `AGENTS.md`, `spec.md`, `.ai/`, `docs/`
- Never edit: `transcripts/`

## Durable memory
When you learn something about this project that would be useful to a session
that has never seen it, append it to `.ai/MEMORY.md` under a dated heading.
Append only. Never rewrite or delete an existing entry.

## GitHub: try gh, fall back to git, then ask
1. Reach for `gh` first for anything GitHub-side: creating and cloning
   repositories, issues, pull requests, reviews. Confirm once per session
   with `gh auth status`.
2. Fall back to `git` for what it does on its own: pull, add, commit, push,
   log, change. Say in your next message that you fell back, and why.
3. If both fail, stop and ask me. A push that prompts for a password, or a
   401 or 403 from either tool, means there is no working credential here.
   Tell me which command failed and quote what it said. Do not switch the
   remote between HTTPS and SSH, do not ask me to paste a token into a
   file, and do not retry in a loop.

## Credentials
Never ask me to paste a token, key, or password into this conversation, and
never print one into your output. If a task needs a secret, stop and tell me
which environment variable should hold it, then assume it is set. If you find
a credential in a file, do not repeat it back to me: say where it is and that
it should be moved and rotated.
