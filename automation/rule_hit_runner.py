#!/usr/bin/env python3
import hashlib
import json
from datetime import datetime
from pathlib import Path


SEVERITY_RANK = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
ACTION_RANK = {"reject": 0, "restrict": 1, "downgrade": 2, "revise": 3, "pass": 4}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def has_allowlist(text: str, allowlist_terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in allowlist_terms)


def has_negation_near(text: str, start_idx: int, negation_terms: list[str], window: int = 8) -> bool:
    left = max(0, start_idx - window)
    scope = text[left:start_idx].lower()
    return any(term.lower() in scope for term in negation_terms)


def extract_evidence(text: str, start_idx: int, pattern: str, span: int = 14) -> str:
    end_idx = start_idx + len(pattern)
    left = max(0, start_idx - span)
    right = min(len(text), end_idx + span)
    return text[left:right]


def match_rules(text: str, rules: list[dict]) -> list[dict]:
    hits = []
    lowered = text.lower()

    for rule in rules:
        patterns = rule.get("patterns", [])
        if not patterns:
            continue

        allowlist_terms = rule.get("allowlist_terms", [])
        if allowlist_terms and has_allowlist(text, allowlist_terms):
            continue

        negation_terms = rule.get("negation_terms", [])

        for pattern in patterns:
            idx = lowered.find(pattern.lower())
            if idx < 0:
                continue

            if negation_terms and has_negation_near(text, idx, negation_terms):
                continue

            hits.append(
                {
                    "rule_id": rule["rule_id"],
                    "severity": rule["severity"],
                    "action": rule["action"],
                    "pattern": pattern,
                    "reason_code": rule.get("reason_code", "UNSPECIFIED"),
                    "fix_suggestion": rule.get("fix_suggestion", ""),
                    "evidence_snippet": extract_evidence(text, idx, pattern),
                }
            )
            break

    return hits


def decide(hit_rules: list[dict]):
    if not hit_rules:
        return {
            "risk_level": "P3",
            "decision": "pass",
            "hit_rule_ids": [],
            "reason_codes": [],
            "fix_suggestions": [],
            "evidence_snippet": "-",
        }

    top_severity = min(hit_rules, key=lambda x: SEVERITY_RANK[x["severity"]])["severity"]
    same_level = [h for h in hit_rules if h["severity"] == top_severity]
    final = min(same_level, key=lambda x: ACTION_RANK[x["action"]])

    hit_ids = [h["rule_id"] for h in hit_rules]
    reason_codes = [h["reason_code"] for h in hit_rules]
    fix_suggestions = [h["fix_suggestion"] for h in hit_rules if h["fix_suggestion"]]
    evidence = " | ".join(f"{h['rule_id']}:{h['evidence_snippet']}" for h in hit_rules)
    return {
        "risk_level": top_severity,
        "decision": final["action"],
        "hit_rule_ids": hit_ids,
        "reason_codes": reason_codes,
        "fix_suggestions": fix_suggestions,
        "evidence_snippet": evidence,
    }


def to_markdown(results: list[dict]) -> str:
    total = len(results)
    restricted = sum(1 for r in results if r["decision"] in {"reject", "restrict"})
    passed = sum(1 for r in results if r["decision"] == "pass")
    hit_count = sum(1 for r in results if r["hit_rule_ids"])
    restrict_rate = (restricted / total * 100) if total else 0
    pass_rate = (passed / total * 100) if total else 0
    hit_rate = (hit_count / total * 100) if total else 0

    lines = [
        "# 规则命中样本运行报告",
        "",
        f"- 样本总数: {total}",
        f"- 命中规则样本数: {hit_count} ({hit_rate:.1f}%)",
        f"- 限制/拒绝样本数: {restricted} ({restrict_rate:.1f}%)",
        f"- 放行样本数: {passed} ({pass_rate:.1f}%)",
        "",
        "| content_id | hit_rule_ids | reason_codes | risk_level | decision | evidence_snippet |",
        "|---|---|---|---|---|---|",
    ]
    for row in results:
        ids = ",".join(row["hit_rule_ids"]) if row["hit_rule_ids"] else "-"
        reason_codes = ",".join(row["reason_codes"]) if row["reason_codes"] else "-"
        lines.append(
            f"| {row['content_id']} | {ids} | {reason_codes} | {row['risk_level']} | {row['decision']} | {row['evidence_snippet']} |"
        )
    lines.append("")
    return "\n".join(lines)


def to_review_records(results: list[dict]) -> list[dict]:
    now = datetime.now().isoformat(timespec="seconds")
    records = []
    for row in results:
        records.append(
            {
                "case_id": f"AUTO-{row['content_id']}",
                "content_id": row["content_id"],
                "reviewer": "auto-rule-engine",
                "review_time": now,
                "hit_rule_ids": row["hit_rule_ids"],
                "reason_codes": row["reason_codes"],
                "risk_level": row["risk_level"],
                "decision": row["decision"],
                "fix_suggestions": row["fix_suggestions"],
                "evidence_snippet": row["evidence_snippet"],
                "action_taken": "pending_manual_confirmation",
                "recheck_required": row["decision"] != "pass",
                "notes": "generated_from_rule_hit_runner",
            }
        )
    return records


def render_review_records_markdown(records: list[dict]) -> str:
    lines = ["# 审核记录清单（自动生成）", ""]
    for record in records:
        lines.extend(
            [
                f"## {record['case_id']}",
                f"- content_id: {record['content_id']}",
                f"- reviewer: {record['reviewer']}",
                f"- review_time: {record['review_time']}",
                f"- hit_rule_ids: {', '.join(record['hit_rule_ids']) if record['hit_rule_ids'] else '-'}",
                f"- reason_codes: {', '.join(record['reason_codes']) if record['reason_codes'] else '-'}",
                f"- risk_level: {record['risk_level']}",
                f"- decision: {record['decision']}",
                f"- fix_suggestions: {'；'.join(record['fix_suggestions']) if record['fix_suggestions'] else '-'}",
                f"- evidence_snippet: {record['evidence_snippet']}",
                f"- action_taken: {record['action_taken']}",
                f"- recheck_required: {record['recheck_required']}",
                f"- notes: {record['notes']}",
                "",
            ]
        )
    return "\n".join(lines)


def append_review_log(log_path: Path, records: list[dict]) -> None:
    existing_keys = set()
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8").splitlines():
            marker = "record_key="
            if marker in line:
                existing_keys.add(line.split(marker, 1)[1].strip())

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [f"## {now} 自动追加", ""]
    appended = 0
    for record in records:
        raw_key = "|".join(
            [
                record["content_id"],
                record["decision"],
                ",".join(sorted(record["hit_rule_ids"])),
                ",".join(sorted(record["reason_codes"])),
            ]
        )
        record_key = hashlib.sha1(raw_key.encode("utf-8")).hexdigest()[:12]
        if record_key in existing_keys:
            continue

        lines.append(
            "- "
            + f"{record['case_id']} | {record['content_id']} | {record['risk_level']} | {record['decision']}"
            + f" | reason_codes={','.join(record['reason_codes']) if record['reason_codes'] else '-'}"
            + f" | hit_rule_ids={','.join(record['hit_rule_ids']) if record['hit_rule_ids'] else '-'}"
            + f" | record_key={record_key}"
        )
        appended += 1
    lines.append("")

    if appended == 0:
        return

    with log_path.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    base = Path(__file__).resolve().parent
    rules_path = base.parent / "rule-library" / "content-compliance-rules-v0.2.yaml"
    samples_path = base / "sample-inputs.json"
    report_path = base / "sample-run-report.md"
    records_path = base / "sample-review-records.json"
    records_md_path = base / "sample-review-records.md"
    review_log_path = base.parent / "review-log.md"

    rules_doc = load_json(rules_path)
    samples = load_json(samples_path)

    results = []
    for sample in samples:
        hit_rules = match_rules(sample["text"], rules_doc["rules"])
        final = decide(hit_rules)
        results.append({"content_id": sample["content_id"], **final})

    review_records = to_review_records(results)

    report_path.write_text(to_markdown(results), encoding="utf-8")
    records_path.write_text(json.dumps(review_records, ensure_ascii=False, indent=2), encoding="utf-8")
    records_md_path.write_text(render_review_records_markdown(review_records), encoding="utf-8")
    append_review_log(review_log_path, review_records)

    print(f"Report generated: {report_path}")
    print(f"Review records generated: {records_path}")
    print(f"Review records markdown generated: {records_md_path}")
    print(f"Review log appended: {review_log_path}")


if __name__ == "__main__":
    main()
