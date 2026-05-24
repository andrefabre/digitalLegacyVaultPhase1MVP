# TASKS: Master Execution Board

## Document Context

This file defines execution and what for the ICT171 Cloud Server Project.
Read these files in this order:

1. [SPEC.md](SPEC.md) — intent and why
2. [PLAN.md](PLAN.md) — architecture and how
3. `TASKS.md` — execution and what (this file)

Assessment criteria and marking rubric are defined in `instructions.md`.
This file is not included in the repository.

---

## How to Use This File

- Work through phases in order — do not start a phase until the previous phase gate is complete
- Each task has acceptance criteria — a task is not done until its criteria is met
- Capture evidence for every task that produces output
- Commit after every completed task using the commit template in `.gitmessage.txt`
- Update task status as you go — `[ ]` not started, `[x]` complete

---

## TCO Presentation (Assessment 2)

Due: 10 May 2026. Managed separately from the cloud server project build.
Estimated 5 hours remaining — references, speech content, rubric verification, final polish.
See PowerPoint deck in `docs/`.

---

## Phase 0: Refactor and Cleanup (Current)

### 0.1 Governance documents

- [x] Rewrite SPEC.md — all sections complete, declarative language, internally consistent
- [x] Rewrite PLAN.md — all sections complete, four layer architecture, script model updated
- [x] Rewrite TASKS.md — this file, complete
- [x] Update README.md — reflect new repo structure, updated script paths, correct layer descriptions
- [x] Fix PLAN.md typo — double em dash on TLS certificate line in Section 6 Security Controls

### 0.2 Repository structure cleanup

- [x] Delete orphaned Next.js files — `app/globals.css`, `app/layout.tsx`, `app/page.tsx`
- [x] Delete Next.js config files — `next-env.d.ts`, `next.config.js`, `package.json`, `tsconfig.json`
- [x] Restructure scripts into layer folders — `scripts/iaas/`, `scripts/server/`, `scripts/operations/`, `scripts/application/`
- [x] Move `nginx.conf` to `scripts/server/configs/nginx.conf`
- [x] Move `INFRASTRUCTURE-SETUP.md` to `scripts/INFRASTRUCTURE-SETUP.md`
- [x] Delete obsolete `infrastructure/docs/ARCHITECTURE.md`
- [x] Delete obsolete `infrastructure/docs/DEPLOYMENT-GUIDE.md`
- [x] Move architecture diagram to `docs/architecture/`
- [x] Fix `index.html` title tag — change from personal portfolio title to DLV project title
- [x] Remove Bootstrap from licence acknowledgements table in `index.html`
- [x] Create evidence folder structure for future phases — `docs/evidence/phase-3/`, `docs/evidence/phase-4/`, `docs/evidence/phase-5/`

### 0.3 Harden Server script split to separate concerns

- [x] Rewrite `2-harden-server.sh` — split into `3-install-packages.sh` and `4-harden-server.sh`
  - Acceptance criteria: package installation and hardening are separate scripts with separate responsibilities
- [x] Update `4-harden-server.sh` — fail loudly if `SSH_CIDR` is not set, remove insecure fallback
  - Acceptance criteria: script exits with clear error if `SSH_CIDR` is not set

### 0.4 Security fix

- [x] Fix UFW SSH rule — restrict port 22 to authorised IP only
  - Current state: port 22 open to all (`Anywhere`)
  - Fix: `sudo ufw delete allow 22/tcp` then `sudo ufw allow from YOUR_IP/32 to any port 22 proto tcp`
  - Acceptance criteria: `sudo ufw status verbose` shows port 22 restricted to specific IP

### 0.5 Phase 0 gate

- [x] All cleanup tasks complete
- [x] Harden server script split to harden server and install packages
- [x] Security fix applied and verified
- [x] README updated
- [x] Evidence folder structure created for all phases
- [x] Commit history shows deliberate progress

---

## Phase 1: Foundation (Complete)

### 1.1 Infrastructure baseline

- [x] Provision Azure resource group, VNet, subnet, NSG, static public IP, and Ubuntu VM
- [x] Restrict SSH to authorised IP and open HTTP/HTTPS in NSG
- [x] Validate SSH access to VM

### 1.2 Host hardening

- [x] Install packages — Nginx, UFW, fail2ban, Git, Python3 runtime, SQLite
- [x] Enable UFW with port rules — 22, 80, 443
- [x] Disable password authentication and root SSH login
- [x] Enable and start Nginx and fail2ban

### 1.3 Landing page and compliance content

- [x] Deploy static site to `/var/www/dlv`
- [x] Configure Nginx site and health endpoint at `/health`
- [x] Publish student number, proposal content, and licence rationale

### 1.4 Evidence package

- [x] Capture VM, IP, DNS, HTTP reachability, and page content screenshots
- [x] Store artifacts in `docs/evidence/phase-1/`
- [x] Add group discussion evidence artifact

---

## Phase 2: DNS, HTTPS and TLS

### 2.1 DNS script setup

- [x] Split `4-setup-dns-tls.sh` into `2-setup-dns.sh` and `6-setup-tls.sh`
  - Acceptance criteria: DNS verification and TLS configuration are separate scripts in correct layer folders
  - `2-setup-dns.sh` — `scripts/iaas/`
  - `6-setup-tls.sh` — `scripts/server/`

### 2.2 DNS verification

- [x] Run `scripts/iaas/2-setup-dns.sh` and confirm domain resolves to Azure static public IP
  - Acceptance criteria: `nslookup mydigitallegacyvault.com.au` returns `20.5.125.82`
- [x] Capture DNS evidence — CLI output and GoDaddy portal screenshot
  - Evidence: `docs/evidence/phase-2/`

### 2.3 TLS setup

- [x] Run `scripts/server/6-setup-tls.sh` with `DOMAIN` and `ADMIN_EMAIL` set
  - Acceptance criteria: Certbot issues certificate, Nginx serves HTTPS, HTTP redirects to HTTPS
- [x] Verify HTTPS in browser — Edge, Chrome, Firefox
  - Acceptance criteria: padlock visible, no certificate warnings
- [x] Verify HTTPS from CLI — `curl -I https://mydigitallegacyvault.com.au` returns `200`
- [x] Capture TLS evidence — CLI output, browser screenshots, certificate details
  - Evidence: `docs/evidence/phase-2/02_https.md`

### 2.4 Backup script setup

- [x] Rewrite `5-backup-integrity.sh` as `7-backup-integrity.sh` in `scripts/operations/`
  - Acceptance criteria: script correctly targets all backup paths defined in PLAN.md
- [x] Run `scripts/operations/7-backup-integrity.sh` on VM
  - Acceptance criteria: archive, checksum, and report files generated in `/opt/dlv_mvp/backups`
- [x] Verify checksum validation passes
  - Acceptance criteria: `sha256sum -c` returns OK for generated archive
- [x] Enable cron schedule for daily backup
  - Acceptance criteria: cron entry installed and confirmed
- [x] Capture backup evidence — CLI output showing archive, checksum, and report paths
  - Evidence: `docs/evidence/phase-2/`

### 2.5 Verify script and run order finalisation

- [x] Update `scripts/operations/8-verify-server.sh` — add package verification, backup report check, full output formatted for assessor review
  - Acceptance criteria: single script run produces formatted output confirming all rubric criteria are met
- [x] Update `scripts/INFRASTRUCTURE-SETUP.md` — reflect new eight-script run order after restructure
  - Acceptance criteria: document lists all eight scripts in correct run order with prerequisites for each
- [x] Confirm final script run order:
  - `1-provision-vm.sh`
  - `2-setup-dns.sh`
  - `3-install-packages.sh`
  - `4-harden-server.sh`
  - `5-deploy-nginx.sh`
  - `6-setup-tls.sh`
  - `7-backup-integrity.sh`
  - `8-verify-server.sh`

### 2.6 Phase 2 gate

- [x] DNS resolves correctly
- [x] HTTPS valid and reachable without certificate warnings
- [x] Backup script produces timestamped verifiable report
- [x] Evidence captured and committed
- [x] Commit and tag phase milestone

---

## Phase 3: Flask Application Build

### 3.1 Server preparation

- [x] Create application directory structure on VM
  - `sudo mkdir -p /opt/dlv_mvp/uploads`
  - `sudo mkdir -p /opt/dlv_mvp/app`
  - `sudo mkdir -p /opt/dlv_mvp/backups`
  - `sudo chown -R azureuser:azureuser /opt/dlv_mvp`
  - `sudo chmod -R 755 /opt/dlv_mvp`
  - Acceptance criteria: all directories exist on VM with correct permissions

### 3.2 Project setup

- [x] Create Flask app structure in `server/`
  - `server/app.py` — main application file
  - `server/requirements.txt` — pip dependencies
  - `server/templates/` — HTML templates
  - `server/static/` — static assets
- [x] Create virtual environment at `/opt/dlv_mvp/.venv`
- [x] Install dependencies — `pip install -r server/requirements.txt`
  - Dependencies: `flask`, `python-magic`
- [x] Verify Flask app runs locally — `python server/app.py`
  - Acceptance criteria: `http://127.0.0.1:5000` returns 200

### 3.3 Database setup

- [x] Create SQLite database at `/opt/dlv_mvp/app/dlv_mvp.db`
- [x] Define schema — users, asset records, audit log tables
- [x] Verify database connection from Flask app
  - Acceptance criteria: app starts without database errors

### 3.4 Owner workflow

- [x] Implement account creation — registration form and server-side validation
  - Acceptance criteria: owner can create account, credentials stored securely
- [x] Implement asset record creation — form, validation, database write
  - Acceptance criteria: owner can create, read, update, delete own records
- [x] Implement document upload with security controls
  - Allowlist file types verified by python-magic
  - File size limit enforced server side
  - UUID rename on storage
  - Store uploads outside web root
  - Acceptance criteria: PDF and DOCX accepted, all other types rejected, 
    files not accessible via direct URL, stored with UUID filename
- [x] Implement executor nomination — owner selects executor from registered users
  - Acceptance criteria: executor nomination stored, vault becomes active

### 3.5 Admin workflow

- [x] Implement admin authentication and session management
  - Acceptance criteria: admin login works, session persists, logout clears session
- [x] Implement admin review page — view submissions and uploaded document metadata
  - Acceptance criteria: admin can view all owner submissions
- [x] Implement manual probate verification and release approval
  - Acceptance criteria: admin can approve executor release, status updates in database
- [x] Implement audit logging — submission, upload, login, and status change events
  - Acceptance criteria: audit events written to log for all critical actions listed in SPEC.md

### 3.6 Executor workflow

- [x] Implement executor account creation
  - Acceptance criteria: executor can register and log in
- [x] Implement executor read-only access — view owner asset records after admin approval
  - Acceptance criteria: executor can only read, cannot create, update, or delete
- [x] Implement access condition — executor cannot view records until admin approves
  - Acceptance criteria: executor sees restricted message before approval, records after

### 3.7 Testing

- [x] Write test plan in `docs/testing/` — document what is being tested and expected outcomes for each workflow
- [x] Test owner workflow end to end — account creation, asset record, upload, executor nomination
- [x] Test admin workflow end to end — login, review, probate verification, release approval
- [x] Test executor workflow end to end — login, access denied before approval, access granted after
- [ ] Test upload security controls — verify rejected file types, size limits, and UUID rename
- [x] Capture test evidence — screenshots for each test scenario
  - Evidence: `docs/evidence/phase-3/`

### 3.8 Phase 3 gate

- [x] End-to-end workflow demonstrated — owner account creation to simulated executor release
- [x] All three roles verified against access levels in SPEC.md
- [ ] Upload security controls verified
- [ ] Test plan complete and evidence captured
- [ ] Commit history shows iterative development

---

## Phase 4: Operations and Security Review

### 4.1 Verification script

- [ ] Run `scripts/operations/8-verify-server.sh` and capture full output
  - Acceptance criteria: all checks pass, output formatted for assessor review
- [ ] Store output as evidence artifact
  - Evidence: `docs/evidence/phase-4/verify-server-output.txt`

### 4.2 Security review pass

- [ ] Verify HTTPS-only behaviour — HTTP redirects to HTTPS
- [ ] Verify upload restrictions and storage boundaries
- [ ] Verify UFW, fail2ban, and SSH settings match Security Controls in PLAN.md
- [ ] Verify NSG rules match documented configuration

### 4.3 Phase 4 gate

- [ ] Verify script output confirms all rubric criteria
- [ ] Security review complete with no outstanding issues
- [ ] Evidence captured and committed

---

## Phase 5: Reproducibility Test

### 5.1 Documentation preparation

- [ ] Document all config files, environment variables, and troubleshooting notes
- [ ] Confirm documentation covers all eight scripts in run order with prerequisites

### 5.2 Full rebuild test

- [ ] Delete all Azure infrastructure — resource group and all contained resources
- [ ] Follow `scripts/INFRASTRUCTURE-SETUP.md` from scratch using only repo documentation
- [ ] Run each script in order, document any gaps, errors, or missing steps
- [ ] Fix documentation where the rebuild reveals issues
- [ ] Rebuild again until it completes without documentation gaps
  - Acceptance criteria: full rebuild completed using only repo documentation with no undocumented steps

### 5.3 Phase 5 gate

- [ ] Full rebuild completed successfully using documentation only
- [ ] All documentation gaps identified and fixed
- [ ] Evidence captured — rebuild CLI output and screenshots
  - Evidence: `docs/evidence/phase-5/`
- [ ] Commit documentation fixes

---

## Phase 6: Final Packaging and Submission

### 6.1 Evidence finalisation

- [ ] Capture final screenshots — intake, upload, admin, DNS, HTTPS, script outputs
- [ ] Confirm evidence indexed and linked in `docs/evidence/`
- [ ] Confirm commit history shows iterative progress across multiple weeks
  - Acceptance criteria: commits spread across 3+ weeks with meaningful messages

### 6.2 Video explainer

- [ ] Write video run sheet — VM launch, web server setup, DNS linking, app workflow, script output
- [ ] Record explainer video
  - Acceptance criteria: video covers all required rubric elements within time limit

### 6.3 Final verification gate

- [ ] Run `8-verify-server.sh` — confirm all checks pass
- [ ] Validate public accessibility — domain resolves, HTTPS works, app accessible
- [ ] Validate documentation completeness against SPEC.md success criteria
- [ ] Freeze release tag for final submission

---

## Branch Sequence

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

---

## Hour Budget Tracking

Total budget: 110 hours
Buffer: 30 hours reserved for overruns

| Phase | Estimated Hours | Actual Hours | Status |
| --- | --- | --- | --- |
| Phase 0 — Refactor and Cleanup | 8 | | In Progress |
| Phase 2 — DNS, HTTPS and TLS | 5 | | Not Started |
| Phase 3 — Flask Application | 32 | | Not Started |
| Phase 4 — Operations and Security | 4 | | Not Started |
| Phase 5 — Reproducibility Test | 8 | | Not Started |
| Phase 6 — Final Packaging | 5 | | Not Started |
| **Total Estimated** | **62** | | |
| **Buffer** | **30** | | |
| **Total Budget** | **92** | | |