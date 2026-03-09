#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RULES_PATH="$SCRIPT_DIR/../rule-library/content-compliance-rules-v0.2.yaml"
SAMPLES_PATH="$SCRIPT_DIR/sample-inputs.json"
STATUS_PATH="$SCRIPT_DIR/check-status.json"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --rules)
      RULES_PATH="$2"
      shift 2
      ;;
    --samples)
      SAMPLES_PATH="$2"
      shift 2
      ;;
    --status-out)
      STATUS_PATH="$2"
      shift 2
      ;;
    *)
      echo "Unknown arg: $1"
      echo "Usage: $0 [--rules <path>] [--samples <path>] [--status-out <path>]"
      exit 2
      ;;
  esac
done

python3 "$SCRIPT_DIR/rule_hit_runner.py" \
  --strict-yaml \
  --rules "$RULES_PATH" \
  --samples "$SAMPLES_PATH" \
  --status-out "$STATUS_PATH"

echo "[OK] strict YAML check and sample regression finished"
echo "[OK] status json: $STATUS_PATH"
