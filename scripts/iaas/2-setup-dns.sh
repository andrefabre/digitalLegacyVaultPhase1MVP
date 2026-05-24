#!/usr/bin/env bash
set -euo pipefail

# Verify DNS resolves to expected public IP

# Variable Declarations

DOMAIN="${DOMAIN:-mydigitallegacyvault.com.au}"
EXPECTED_PUBLIC_IP="${EXPECTED_PUBLIC_IP:-}"
STRICT_DNS_CHECK="${STRICT_DNS_CHECK:-true}"

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


if [[ -n "${EXPECTED_PUBLIC_IP}" && "${resolved_ip}" != "${EXPECTED_PUBLIC_IP}" ]]; then
  echo "ERROR: DNS mismatch. Expected ${EXPECTED_PUBLIC_IP}, got ${resolved_ip}."
  exit 1
fi

if [[ -z "${EXPECTED_PUBLIC_IP}" && "${STRICT_DNS_CHECK}" == "true" ]]; then
  echo "INFO: EXPECTED_PUBLIC_IP not provided; proceeding with resolved DNS value."
fi

echo ""
echo "DNS verification complete for domain: ${DOMAIN}."