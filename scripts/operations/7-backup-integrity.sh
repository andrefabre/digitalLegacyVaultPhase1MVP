#!/usr/bin/env bash
set -euo pipefail

# Backup and integrity workflow for DLV MVP.

APP_DIR="${APP_DIR:-/opt/dlv_mvp}"
BACKUP_DIR="${BACKUP_DIR:-/opt/dlv_mvp/backups}"
UPLOAD_DIR="${UPLOAD_DIR:-/opt/dlv_mvp/uploads}"
DB_PATH="${DB_PATH:-/opt/dlv_mvp/app/dlv_mvp.db}"
WEB_ROOT="${WEB_ROOT:-/var/www/dlv}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
INSTALL_CRON="${INSTALL_CRON:-false}"
CRON_SCHEDULE="${CRON_SCHEDULE:-30 2 * * *}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
HOSTNAME_VALUE="$(hostname)"

if command -v sudo >/dev/null 2>&1 && [[ "${EUID}" -ne 0 ]]; then
  SUDO="sudo"
else
  SUDO=""
fi

ARCHIVE_FILE="${BACKUP_DIR}/dlv_backup_${TIMESTAMP}.tar.gz"
CHECKSUM_FILE="${BACKUP_DIR}/dlv_backup_${TIMESTAMP}.sha256"
REPORT_FILE="${BACKUP_DIR}/dlv_backup_${TIMESTAMP}.report.txt"

${SUDO} mkdir -p "${BACKUP_DIR}"
${SUDO} chmod 750 "${BACKUP_DIR}"

backup_targets=()

for path in "${WEB_ROOT}" "${UPLOAD_DIR}" "${DB_PATH}" "${APP_DIR}/app" "${APP_DIR}/repo"; do
  if [[ -e "${path}" ]]; then
    backup_targets+=("${path}")
  fi
done

if [[ "${#backup_targets[@]}" -eq 0 ]]; then
  echo "ERROR: No backup targets found."
  exit 1
fi

echo "Creating backup archive: ${ARCHIVE_FILE}"
${SUDO} tar -czf "${ARCHIVE_FILE}" "${backup_targets[@]}"

echo "Generating checksum: ${CHECKSUM_FILE}"
${SUDO} sha256sum "${ARCHIVE_FILE}" | ${SUDO} tee "${CHECKSUM_FILE}" >/dev/null

archive_size_bytes="$(${SUDO} stat -c%s "${ARCHIVE_FILE}")"

{
  echo "Backup Report"
  echo "timestamp=${TIMESTAMP}"
  echo "hostname=${HOSTNAME_VALUE}"
  echo "archive=${ARCHIVE_FILE}"
  echo "checksum=${CHECKSUM_FILE}"
  echo "archive_size_bytes=${archive_size_bytes}"
  echo "retention_days=${RETENTION_DAYS}"
  echo "targets="
  for target in "${backup_targets[@]}"; do
    echo "  - ${target}"
  done
  echo "checksum_verify_result="
  ${SUDO} sha256sum -c "${CHECKSUM_FILE}" 2>&1
} | ${SUDO} tee "${REPORT_FILE}" >/dev/null

echo "Applying retention policy for files older than ${RETENTION_DAYS} days."
${SUDO} find "${BACKUP_DIR}" -type f -name 'dlv_backup_*' -mtime +"${RETENTION_DAYS}" -delete

if [[ "${INSTALL_CRON}" == "true" ]]; then
  script_path="$(realpath "$0")"
  cron_line="${CRON_SCHEDULE} ${script_path} >> ${BACKUP_DIR}/backup_cron.log 2>&1"

  (crontab -l 2>/dev/null | grep -v "$(basename "$0")"; echo "${cron_line}") | crontab -
  echo "Installed cron entry: ${cron_line}"
fi

echo ""
echo "Backup and integrity workflow complete."
echo "Archive: ${ARCHIVE_FILE}"
echo "Checksum: ${CHECKSUM_FILE}"
echo "Report: ${REPORT_FILE}"
