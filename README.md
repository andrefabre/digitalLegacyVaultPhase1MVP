# ICT171 Cloud Server Project + Digital Legacy Vault MVP

The project must build reproducible cloud-hosted infrastructure, a secure web server, manual and automated scripting, and deploy the Digital Legacy Vault Phase 1 MVP application. The application must be non-custodial, compliance and security-first because it stores personal data and releases it to a nominated executor.

## Start Here

The project is structured across four distinct layers:

1. **IaaS layer** — Azure VM, networking, NSG, public IP, DNS
2. **Server layer** — Ubuntu OS, Nginx web server, HTTPS, TLS
3. **Application layer** — Digital Legacy Vault Phase 1 MVP, Flask backend with frontend UI
4. **Documentation and scripting layer** — overarching project documentation, layer specific documentation, evidence artefacts, automated and manually executed scripts for each layer

Read these files in order:

1. [SPEC.md](SPEC.md) — intent and why
2. [PLAN.md](PLAN.md) — architecture and technical decisions
3. [TASKS.md](TASKS.md) — implementation sequence

**Follow the [INFRASTRUCTURE_SETUP](INFRASTRUCTURE_SETUP.md) instructions to deploy this project yourself**

## Current Delivery Status

1. Phase 1: Foundation [Complete]
   - [x] Infrastructure Baseline — Azure VM, SSH to Authorised IP only and Open HTTP/HTTPS in NSG, SSH access to VM
   - [x] Host Hardening — Package install, UFW port rules, Enable Nginx and fail2ban, Disable SSH root login
   - [x] Landing page and compliance content — Deploy static stie to `/var/www/dlv`
   - [x] Evidence package — `/docs/evidence/phase-1`
2. Phase 2: DNS, HTTPS and TLS [Complete]
   - [x] DNS script setup — develop `scripts/iaas/2-setup-dns.sh`
   - [x] DNS verification — confirm domain resolves to Azure static public IP `scripts/iaas/2-setup-dns.sh`
   - [x] TLS setup — Certbot issues certificate, Nginx serves HTTPS, HTTP redirects to HTTPS `scripts/server/6-setup-tls.sh`
   - [x] Backup script setup — develoep `7-backup-integrity.sh`
   - [x] Backup files —  archive, checksum, and report files generated in `/opt/dlv_mvp/backups`
   - [x] `scripts/operations/8-verify-server.sh` script to validate IaaS and Server config and deployment
   - [x] `INFRASTRUCTURE.md` — Document script run order with prerequisites
   - [x] Evidence package — CLI output, browser screenshots, certificate details `/docs/evidence/phase-2`
3. Phase 3: Flask Application Build [Complete]
   - [x] Server preparation
   - [x] Project setup
   - [x] Database setup
   - [x] Owner workflow
   - [x] Admin workflow
   - [x] Executor workflow
   - [x] Testing
   - [x] Evidence package — `/docs/evidence/phase-3`
4. Phase 4: Operations and Security Review [Complete]
   - [x] Verification script
   - [x] Security review pass
   - [x] Evidence package — `/docs/evidence/phase-4`
5. Phase 5: Reproducibility Test
   - [x] Documentation preparation
   - [x] Full rebuild test
   - [x] Evidence package — `/docs/evidence/phase-5`
6. Phase 6: Final Packaging and Submission
   - [x] Evidence finalisation
   - [x] Video explainer
   - [x] Final verification gate
   - [ ] Evidence package — `/docs/evidence/phase-6`

## Repository Structure

```text
├── docs/
│   ├── architecture/   - architecture diagrams and visual references for the project
│   ├── evidence/       - evidence screenshots for each build phase
│   │   ├── phase-1/
│   │   ├── phase-2/
│   └── testing/        - test plans for DLV App
├── public/             - static web assets served by Nginx, the landing page and its dependencies
│   ├── assets/
│   │   └── images/     - image files used by the landing page
│   ├── css/            - stylesheet for the landing page
│   └── js/             - JavaScript for the landing page
├── scripts/
│   ├── application/    - Flask app deployment scripts
│   ├── iaas/           - Azure provisioning scripts
│   ├── operations/     - DNS and backup scripts
│   ├── server/         - server hardening and Nginx deployment scripts
│   │   └── configs/    - server config files
│   └── INFRASTRUCTURE-SETUP.md
├── server/      - Flask application source code
├── SPEC.md      - intent and why for the ICT171 Cloud Server Project
├── PLAN.md      - defines the how for the ICT171 Cloud Server Project
├── TASKS.md     - tasks to implement the ICT171 Cloud Server Project
├── README.md   - project overview, repository structure, and quick start guide
├── LICENSE
└── .gitmessage.txt - template for commit messages
```

## Scripts

Application scripts:

1. TBC

IaaS scripts:

1. `/scripts/iaas/1-provision-vm.sh`
2. `/scripts/iaas/2-setup-dns.sh`

Operations scripts:

1. `/scripts/operations/7-backup-integrity.sh`
2. `/scripts/operations/8-verify-server.sh`

Server scripts:

1. `/scripts/server/3-install-packages.sh`
2. `/scripts/server/4-harden-server.sh`
3. `/scripts/server/5-deploy-nginx.sh`
4. `/scripts/server/6-setup-tls.sh`

## Local App Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r server/requirements.txt
python server/app.py
```

Open `http://127.0.0.1:5000` once the Flask app exists.

## Evidence

1. Phase 1: `docs/evidence/phase-1/`
2. Phase 2: `docs/evidence/phase-2/`
3. Phase 3: `docs/evidence/phase-3/`
4. Phase 4: `docs/evidence/phase-4/`
5. Phase 5: `docs/evidence/phase-5/`
6. Phase 6: `docs/evidence/phase-6/`

## License

MIT License. See `LICENSE`.
