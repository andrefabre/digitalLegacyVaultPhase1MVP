#!/usr/bin/env bash
set -euo pipefail

# Variable Declarations

DOMAIN="${DOMAIN:-mydigitallegacyvault.com.au}"
ADMIN_EMAIL="${ADMIN_EMAIL:-your-email@example.com}"

# Admin email validation and sudo check

if [[ -z "${DOMAIN}" || -z "${ADMIN_EMAIL}" ]]; then
  echo "ERROR: DOMAIN and ADMIN_EMAIL are required."
  exit 1
fi

if [[ "${ADMIN_EMAIL}" == "your-email@example.com" ]]; then
  echo "ERROR: Set ADMIN_EMAIL to a real address before running."
  exit 1
fi

if command -v sudo >/dev/null 2>&1 && [[ "${EUID}" -ne 0 ]]; then
  SUDO="sudo"
else
  SUDO=""
fi

# DNS resolution check

echo "Resolving domain: ${DOMAIN}"
resolved_ip="$(getent ahostsv4 "${DOMAIN}" | awk 'NR==1 {print $1}')"

if [[ -z "${resolved_ip}" ]]; then
  resolved_ip="$(nslookup "${DOMAIN}" 2>/dev/null | awk '/^Address: / {print $2}' | tail -n 1)"
fi

if [[ -z "${resolved_ip}" ]]; then
  echo "ERROR: Could not resolve ${DOMAIN}."
  exit 1
fi

echo "Domain resolves to: ${resolved_ip}"

${SUDO} apt update
${SUDO} apt install -y certbot python3-certbot-nginx

${SUDO} certbot --nginx \
  -d "${DOMAIN}" \
  --agree-tos \
  -m "${ADMIN_EMAIL}" \
  --redirect \
  --non-interactive \
  --keep-until-expiring

${SUDO} systemctl status certbot.timer --no-pager | sed -n '1,12p'

echo ""
echo "HTTPS validation output:"
curl -I "https://${DOMAIN}" | sed -n '1,10p'
echo ""
echo "TLS setup complete for ${DOMAIN}."
