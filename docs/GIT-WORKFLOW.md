# Git Workflow

## 1. Branch Strategy

Use short-lived branches aligned to deliverable chunks.

Work in this order, one branch per task cluster:

1. `refactor/tasks-cleanup` — this rewrite
2. `fix/security-ufw-ssh` — UFW SSH rule fix
3. `refactor/split-harden-server-script` — split harden server script
4. `phase2/dns-tls` — DNS script split, DNS verification, TLS setup, backup script
5. `phase3/flask-setup` — server preparation, project structure, database
6. `phase3/owner-workflow` — account, records, uploads
7. `phase3/admin-executor-workflow` — admin and executor paths
8. `phase3/testing` — test plan and test evidence
9. `phase4/operations` — verification script and security review
10. `phase5/reproducibility` — documentation and full rebuild test
11. `phase6/final-package` — evidence, video, submission

## 2. Commit Rules

1. One intent per commit.
2. Subject format:
   - `phase: concise change summary`
   - Example: `phase2: add certbot validation checks`
3. Body must answer:
   - why this change exists
   - what was validated
   - what evidence was captured

## 3. Suggested Tags

1. `v1.0-assessment1-submitted`
2. `v1.1-refactor-complete`
3. `v1.2-dns-tls-complete`
4. `v1.3-backup-integrity-complete`

## 4. Setup Commit Template

From repo root:

```bash
git config commit.template .gitmessage.txt
```

Then commit normally:

```bash
git commit
```

## 5. Review Discipline

Before every commit:

```bash
git status
git diff --staged
```

Do not commit without reviewing the staged diff.
