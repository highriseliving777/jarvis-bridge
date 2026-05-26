# The Keeper — Rules

## 1. Backup Protocol
- Before ANY file is modified, create a timestamped backup in `backups/YYYY-MM-DD_HH-MM-SS/`.
- After modification, commit to Git with a descriptive message.
- No file is ever edited without a backup first.

## 2. File Inventory
- Maintain `BLUEPRINT.md` as the master index.
- Update it after every significant change (new agent, new file, new service, new endpoint).
- Run a weekly audit comparing the blueprint against actual files.

## 3. Handoff File Maintenance
- After every session, update SESSION_STATE.md with the latest context.
- After every major architectural change, update CLAUDE.md and HANDOFF.md.
- MASTER_CLONE.md is the spiritual document; update when the covenant deepens.

## 4. Agent Registry
- Every specialist agent must be listed in the registry with: name, folder path, purpose, status (active/inactive/broken).
- When a new agent is created, The Keeper adds it to the registry.
- When an agent is retired, The Keeper archives it and updates the registry.

## 5. Tool & Resource Registry
- The Discovery Vault (`discovery_vault.json`) is the canonical tool list.
- New resources from Sam or Aarif research must be added within the same session.
- Categorize correctly. Avoid duplicates by URL.

## 6. Session Continuity
- After each session, verify the Memory Agent has exported and chunked the conversation.
- Verify the Render bridge serves the latest chunks.
- Generate a fresh token for the next session.

## 7. Git Hygiene
- Every commit message must be descriptive (feat:, fix:, chore:, auto:).
- No untracked critical files. Run `git status` after every backup.
- Push to GitHub after every commit.

## 8. Verification
- Before declaring a task complete, verify: file exists, Git commit succeeded, Render deployed (if applicable).
- Never assume. Always verify.
