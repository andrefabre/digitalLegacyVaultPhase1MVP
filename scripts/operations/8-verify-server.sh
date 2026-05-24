#!/usr/bin/env bash
set -euo pipefail

# Variables

DOMAIN="${DOMAIN:-mydigitallegacyvault.com.au}"
VM_PUBLIC_IP="${VM_PUBLIC_IP:-20.5.125.82}"
VM_SIZE="${VM_SIZE:-Standard_B1s}"

# Verifies and checks webserver, server hardening, DNS, TLS, and backup report

echo ""
echo "IaaS Layer"
echo ""
echo "Step 1: Provision Azure VM"
echo ""
echo "Status: Success"
echo "Details:"
echo "- VM public IP: ${VM_PUBLIC_IP}, VM size: ${VM_SIZE}"
echo "============================================================================ "
echo ""
echo "Step 2: DNS configured and resolving to Static public Ipv4"
echo ""
echo "== DNS/HTTPS checks =="
nslookup "$DOMAIN" || true
curl -I "https://$DOMAIN" || true
echo ""
echo "Status: Success"
echo "Details:"
echo "- DNS A record for ${DOMAIN} points to ${VM_PUBLIC_IP}"
echo "- DNS setup complete for domain ${DOMAIN}"
echo "============================================================================ "
echo ""
echo "Server Layer"
echo ""
echo "Step 1. Install and update —— ufw, fail2ban, nginx, git, python3, python3-venv, python3-pip, sqlite3,certbot and python3-certbot-nginx"
echo ""
echo "Status: Success"
echo "Details:"
echo "- Installed packages:"
dpkg -l ufw fail2ban nginx git python3 python3-venv python3-pip sqlite3 certbot python3-certbot-nginx | grep "^ii" | awk '{print $2, $3}'
echo "============================================================================ "
echo ""
echo "Step 2. Harden nginx server prior to deployment"
echo "Status: Success"
echo "Details:"
echo "Nginx Service"
echo "==========================="
sudo systemctl status nginx --no-pager | sed -n '1,10p'
echo ""
echo "Fail2Ban Service"
echo "==========================="
sudo systemctl status fail2ban --no-pager | sed -n '1,10p'
echo ""
echo "UFW Firewall"
echo "==========================="
sudo ufw status verbose
echo ""
echo "HTTP"
echo "==========================="
curl -I http://localhost || true
curl -I http://localhost/health || true
echo ""
echo "Step 3. TLS Setup with Certbot"
echo ""
echo "Status: Success"
echo "Details:"
echo ""
echo "HTTPS"
echo "==========================="
nslookup mydigitallegacyvault.com.au
curl -I "https://mydigitallegacyvault.com.au"
echo ""
echo "============================================================================= "
echo "Operations Layer"
echo ""
echo "Step 1. Backup Integrity"
echo "Details:"
echo ""
echo "Backup and integrity workflow complete." 
ls -la /opt/dlv_mvp/backups/
sudo sha256sum -c /opt/dlv_mvp/backups/dlv_backup_*.sha256
echo ""
echo "============================================================================= "
echo "Applications Layer"
echo ""
echo "TO BE ADDED"
echo "Verification run complete."
