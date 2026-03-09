# Automation Quick Start

## Environment
- Python 3.10+
- Install dependencies:
  - `python3 -m pip install -r output/compliance-assistant/automation/requirements.txt`

## Run Rule Engine
- Standard mode (YAML preferred, JSON fallback):
  - `python3 output/compliance-assistant/automation/rule_hit_runner.py`
- Strict mode (YAML parse must pass):
  - `python3 output/compliance-assistant/automation/rule_hit_runner.py --strict-yaml`

## One-Command Check
- Run strict YAML validation + sample regression:
  - `bash output/compliance-assistant/automation/run_checks.sh`
- Run with custom rules/samples and custom status output:
  - `bash output/compliance-assistant/automation/run_checks.sh --rules <rules.yaml> --samples <samples.json> --status-out <status.json>`

## Outputs
- Report: `output/compliance-assistant/automation/sample-run-report.md`
- Review records JSON: `output/compliance-assistant/automation/sample-review-records.json`
- Review records Markdown: `output/compliance-assistant/automation/sample-review-records.md`
- Review log append: `output/compliance-assistant/review-log.md`
- Check status JSON: `output/compliance-assistant/automation/check-status.json`
  - Success: `ok=true`, with `summary` metrics and empty `error_code` / `error_message`
  - Failure: `ok=false`, with `error_code` (`FILE_NOT_FOUND` / `INVALID_JSON` / `RULE_PARSE_ERROR` / `INVALID_RULE_SCHEMA` / `UNKNOWN_ERROR`) and `error_message`

## Troubleshooting
- `ModuleNotFoundError: No module named 'yaml'`
  - Reinstall deps with requirements.txt.
- YAML parsing failed in strict mode
  - Check indentation, list syntax, and duplicate keys in rule YAML.
