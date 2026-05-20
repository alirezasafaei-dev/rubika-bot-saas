#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [[ -z "${DATABASE_URL:-}" || -z "${DOMAIN_FOR_RUBIKABOTSAAS:-}" || -z "${RUBIKA_BOT_TOKEN:-}" ]]; then
  set -a
  [[ -f .env ]] && . ./.env
  set +a
fi

TOKEN="${RUBIKA_BOT_TOKEN:-${1:-}}"
if [[ -z "${TOKEN}" ]]; then
  echo "RUBIKA_BOT_TOKEN is required (arg1 or .env value)." >&2
  exit 1
fi

BASE_DOMAIN="${DOMAIN_FOR_RUBIKABOTSAAS:-${2:-}}"
if [[ -z "${BASE_DOMAIN}" ]]; then
  BASE_DOMAIN="https://rbsaas.alirezasafaeisystems.ir"
fi
if [[ -z "${BASE_DOMAIN}" ]]; then
  echo "DOMAIN_FOR_RUBIKABOTSAAS is required (or pass as arg2)." >&2
  exit 1
fi

CHANNEL_ID="${3:-}"
if [[ -n "${CHANNEL_ID}" ]]; then
  WEBHOOK_PATH="/"
else
  WEBHOOK_PATH="/"
fi
if [[ "${BASE_DOMAIN}" =~ ^https?:// ]]; then
  WEBHOOK_URL="${BASE_DOMAIN%/}${WEBHOOK_PATH}"
else
  WEBHOOK_URL="https://${BASE_DOMAIN%/}${WEBHOOK_PATH}"
fi

if [[ -n "${WEBHOOK_SECRET:-}" ]]; then
  SECRET="${WEBHOOK_SECRET}"
elif [[ -n "${RUBIKA_WEBHOOK_SECRET:-}" ]]; then
  SECRET="${RUBIKA_WEBHOOK_SECRET}"
else
  SECRET=""
fi

METHODS=("updateBotEndpoints" "updateBotEndpoint" "setWebhook" "setWebhookEndpoint")
UPDATE_TYPE="ReceiveUpdate"

echo "Trying to register webhook: ${WEBHOOK_URL}"
echo "Token: ${TOKEN:0:6}...${TOKEN: -4}"

attempt() {
  local method="$1"
  local body="$2"
  local endpoint="https://botapi.rubika.ir/v3/${TOKEN}/${method}"
  echo "-> ${method}"
  curl -sS -X POST "${endpoint}" \
    -H "Content-Type: application/json" \
    -d "${body}" || return 3
}

for method in "${METHODS[@]}"; do
  body="{\"url\":\"${WEBHOOK_URL}\",\"type\":\"${UPDATE_TYPE}\""
  if [[ -n "${SECRET}" ]]; then
    body+=",\"secret\":\"${SECRET}\""
  fi
  body+="}"

  response="$(attempt "${method}" "${body}")" || continue
  echo "${response}"

  if echo "${response}" | grep -qiE '"ok"[[:space:]]*:[[:space:]]*true|"success"[[:space:]]*:[[:space:]]*true|"status"[[:space:]]*:[[:space:]]*200|\"status\"[[:space:]]*:[[:space:]]*\"OK\"|"result"[[:space:]]*:[[:space:]]*true'; then
    echo "Webhook registration success with method=${method}"
    exit 0
  fi
done

echo "Webhook registration did not return an obvious success response. Check payload/method from Rubika docs."
echo "Tried methods: ${METHODS[*]}"
exit 2
