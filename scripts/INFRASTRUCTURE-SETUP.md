# Infrastructure Setup Guide

This guide walks through the full deployment of the ICT171 Cloud Server Project
and Digital Legacy Vault Phase 1 MVP from scratch.

Read SPEC.md, PLAN.md, and TASKS.md before following this guide.

---

## Prerequisites

Before starting, confirm the following are in place:

1. Azure account with an active subscription
2. Azure CLI installed and logged in on your local machine — run `az login`
3. Git Bash or terminal available on your local machine
4. Domain registered with GoDaddy — `mydigitallegacyvault.com.au`
5. DNS A record configured in GoDaddy pointing domain to the Azure public IP
6. GitHub account with access to the repository

---

## Step 1 — Provision Azure VM (local machine)

Run from your local machine:

```bash
chmod +x scripts/iaas/1-provision-vm.sh
./scripts/iaas/1-provision-vm.sh
```

Optional — specify a subscription ID:

```bash
SUBSCRIPTION_ID=<your-subscription-id> ./scripts/iaas/1-provision-vm.sh
```

Expected output:

```
Provisioning complete.
VM public IP: 20.5.125.82
SSH command: ssh azureuser@20.5.125.82
```

---

## Step 2 — SSH to VM

```bash
ssh azureuser@20.5.125.82
```

---

## Step 3 — Install Git and Clone Repository

```bash
sudo apt update && sudo apt install -y git
cd ~
git clone https://github.com/andrefabre/digitalLegacyVaultPhase1MVP.git
cd digitalLegacyVaultPhase1MVP
```

---

## Step 4 — Make Scripts Executable

```bash
chmod +x scripts/iaas/*.sh
chmod +x scripts/server/*.sh
chmod +x scripts/operations/*.sh
```

---

## Step 5 — Verify DNS

Confirm the domain resolves to the VM public IP:

```bash
EXPECTED_PUBLIC_IP=20.5.125.82 ./scripts/iaas/2-setup-dns.sh
```

Expected output:

```
Domain resolves to: 20.5.125.82
DNS verification complete for domain: mydigitallegacyvault.com.au.
```

If this fails, check the GoDaddy A record is pointing to the correct IP and wait
for DNS propagation (up to 10 minutes).

---

## Step 6 — Install Packages

```bash
./scripts/server/3-install-packages.sh
```

Expected output confirms all packages installed with versions.

---

## Step 7 — Harden Server

Replace `YOUR_PUBLIC_IP` with your local machine's public IP:

```bash
SSH_CIDR=YOUR_PUBLIC_IP/32 ./scripts/server/4-harden-server.sh
```

To find your public IP:

```bash
curl -s https://api.ipify.org
```

Expected output:

```
Hardening complete.
```

---

## Step 8 — Deploy Nginx

```bash
./scripts/server/5-deploy-nginx.sh
```

Expected output:

```
Nginx deploy complete.
```

---

## Step 9 — Configure Nginx Proxy for Flask App

After deploying Nginx, add the Flask proxy routes to the Nginx config:

```bash
sudo nano /etc/nginx/sites-available/dlv
```

Add these two location blocks inside the server block before the closing `}`:

```nginx
location /app/ {
    proxy_pass http://127.0.0.1:5000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

location ~ ^/(login|logout|register|owner|admin|executor) {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

Test and reload Nginx:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

---

## Step 10 — Setup TLS

Replace `your-email@example.com` with your real email address:

```bash
DOMAIN=mydigitallegacyvault.com.au \
ADMIN_EMAIL=your-email@example.com \
EXPECTED_PUBLIC_IP=20.5.125.82 \
./scripts/server/6-setup-tls.sh
```

Expected output confirms certificate issued and HTTPS returns 200.

---

## Step 11 — Create Application Directories

```bash
sudo mkdir -p /opt/dlv_mvp/uploads
sudo mkdir -p /opt/dlv_mvp/app
sudo mkdir -p /opt/dlv_mvp/backups
sudo chown -R azureuser:azureuser /opt/dlv_mvp
sudo chmod -R 755 /opt/dlv_mvp
sudo chmod 755 /opt/dlv_mvp/backups
```

---

## Step 12 — Deploy Flask Application

```bash
python3 -m venv /opt/dlv_mvp/.venv
source /opt/dlv_mvp/.venv/bin/activate
pip install -r ~/digitalLegacyVaultPhase1MVP/server/requirements.txt
deactivate

nohup /opt/dlv_mvp/.venv/bin/python3 \
  ~/digitalLegacyVaultPhase1MVP/server/app.py \
  > /opt/dlv_mvp/app/flask.log 2>&1 &

sleep 2
curl http://127.0.0.1:5000/health
```

Expected output: `OK`

---

## Step 13 — Run Backup Script

```bash
INSTALL_CRON=true ./scripts/operations/7-backup-integrity.sh
```

Fix permissions if needed:

```bash
sudo chmod 755 /opt/dlv_mvp/backups
sudo chown azureuser:azureuser /opt/dlv_mvp/backups
```

Verify backup files:

```bash
ls -la /opt/dlv_mvp/backups/
sudo sha256sum -c /opt/dlv_mvp/backups/dlv_backup_*.sha256
crontab -l
```

---

## Step 14 — Verify Full Server Setup

```bash
VM_PUBLIC_IP=20.5.125.82 ./scripts/operations/8-verify-server.sh
```

Review the output and confirm all checks pass before proceeding.

---

## Validation Checklist

Run these commands to confirm everything is working:

```bash
# Services
sudo systemctl status nginx --no-pager | head -5
sudo systemctl status fail2ban --no-pager | head -5

# Firewall
sudo ufw status verbose

# HTTP and health
curl -I https://mydigitallegacyvault.com.au
curl https://mydigitallegacyvault.com.au/health

# Flask app
curl http://127.0.0.1:5000/health

# DNS
nslookup mydigitallegacyvault.com.au

# Backup files
ls -la /opt/dlv_mvp/backups/
```

---

## Troubleshooting

**SSH times out:**
- Check your public IP has not changed: `curl -s https://api.ipify.org`
- Update NSG rule: `az network nsg rule update --resource-group rg-dlv-mvp-prod --nsg-name nsg-dlv-mvp-prod --name Allow-SSH-From-My-IP --source-address-prefixes YOUR_IP/32`
- Update UFW rule: `sudo ufw delete allow from OLD_IP to any port 22 proto tcp && sudo ufw allow from NEW_IP/32 to any port 22 proto tcp`

**Flask not responding:**
- Check log: `cat /opt/dlv_mvp/app/flask.log`
- Check if port 5000 is in use: `sudo lsof -i :5000`
- Restart Flask: `sudo kill $(sudo lsof -t -i:5000) && nohup /opt/dlv_mvp/.venv/bin/python3 ~/digitalLegacyVaultPhase1MVP/server/app.py > /opt/dlv_mvp/app/flask.log 2>&1 &`

**Backup permission denied:**
- Run: `sudo chmod 755 /opt/dlv_mvp/backups && sudo chown azureuser:azureuser /opt/dlv_mvp/backups`

**Certbot cannot find server block:**
- Check server_name in Nginx config: `cat /etc/nginx/sites-available/dlv`
- Must show: `server_name mydigitallegacyvault.com.au;`
- Fix: `sudo sed -i 's/server_name _;/server_name mydigitallegacyvault.com.au;/' /etc/nginx/sites-available/dlv`
- Then rerun: `sudo certbot install --cert-name mydigitallegacyvault.com.au`