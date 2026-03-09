# 规则命中样本运行报告

- 样本总数: 5
- 命中规则样本数: 2 (40.0%)
- 限制/拒绝样本数: 2 (40.0%)
- 放行样本数: 3 (60.0%)

| content_id | hit_rule_ids | reason_codes | risk_level | decision | evidence_snippet |
|---|---|---|---|---|---|
| S-001 | CR-004 | MEDICAL_ABSOLUTE_CLAIM | P1 | restrict | CR-004:这个产品包治百病，100%有效，今天下单 |
| S-002 | - | - | P3 | pass | - |
| S-003 | CR-005,CR-007 | FINANCIAL_RETURN_GUARANTEE,INCOMPLETE_AD_DISCLOSURE | P1 | restrict | CR-005:保本高收益项目，稳赚不赔，私信领取名额。 | CR-007:保本高收益项目，稳赚不赔，私信领取名额。 |
| S-004 | - | - | P3 | pass | - |
| S-005 | - | - | P3 | pass | - |
