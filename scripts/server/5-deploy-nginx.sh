#!/usr/bin/env bash
set -euo pipefail

# Deploy public assets to Nginx web root on the Ubuntu VM.

if [[ "${EUID}" -eq 0 ]]; then
    echo "Run this script as a non-root user with sudo privileges."
    exit 1
fi

APP_SRC_DIR="${APP_SRC_DIR:-$(pwd)/public}"
WEB_ROOT="${WEB_ROOT:-/var/www/dlv}"
SERVER_NAME="${SERVER_NAME:-_}"
SITE_NAME="${SITE_NAME:-dlv}"
NGINX_CONF_SOURCE="${NGINX_CONF_SOURCE:-$(pwd)/scripts/server/configs/nginx.conf}"

if [[ ! -d "${APP_SRC_DIR}" ]]; then
    echo "ERROR: APP_SRC_DIR does not exist: ${APP_SRC_DIR}"
    exit 1
fi

sudo mkdir -p "${WEB_ROOT}"
sudo cp -r "${APP_SRC_DIR}/." "${WEB_ROOT}/"
sudo chown -R www-data:www-data "${WEB_ROOT}"
sudo chmod -R 755 "${WEB_ROOT}"

if [[ -f "${NGINX_CONF_SOURCE}" ]]; then
    rendered_conf="$(sed "s|__WEB_ROOT__|${WEB_ROOT}|g; s|__SERVER_NAME__|${SERVER_NAME}|g" "${NGINX_CONF_SOURCE}")"
    echo "${rendered_conf}" | sudo tee "/etc/nginx/sites-available/${SITE_NAME}" >/dev/null
else
    echo "ERROR: Nginx config template not found: ${NGINX_CONF_SOURCE}"
    exit 1
fi

sudo ln -sf "/etc/nginx/sites-available/${SITE_NAME}" "/etc/nginx/sites-enabled/${SITE_NAME}"
sudo rm -f /etc/nginx/sites-enabled/default

sudo nginx -t
sudo systemctl reload nginx

echo ""
echo "Nginx deploy complete."
echo "Validation commands:"
echo "  curl -I http://localhost"
echo "  curl -I http://localhost/health"