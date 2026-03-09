# 规则命中样本运行报告

- 样本总数: 7
- 命中规则样本数: 3 (42.9%)
- 限制/拒绝样本数: 3 (42.9%)
- 放行样本数: 4 (57.1%)
- 严格YAML模式: ON

| content_id | text_version | rule_version | hit_rule_ids | reason_codes | risk_level | decision | evidence_snippet |
|---|---|---|---|---|---|---|---|
| S-001 | v1 | 0.2 | CR-004 | MEDICAL_ABSOLUTE_CLAIM | P1 | restrict | CR-004:这个产品包治百病，100%有效，今天下单 |
| S-002 | v1 | 0.2 | - | - | P3 | pass | - |
| S-003 | v1 | 0.2 | CR-005,CR-007 | FINANCIAL_RETURN_GUARANTEE,INCOMPLETE_AD_DISCLOSURE | P1 | restrict | CR-005:保本高收益项目，稳赚不赔，私信领取名额。 | CR-007:保本高收益项目，稳赚不赔，私信领取名额。 |
| S-004 | v1 | 0.2 | - | - | P3 | pass | - |
| S-005 | v1 | 0.2 | - | - | P3 | pass | - |
| S-006 | v1 | 0.2 | CR-005,CR-007 | FINANCIAL_RETURN_GUARANTEE,INCOMPLETE_AD_DISCLOSURE | P1 | restrict | CR-005:加入会员稳赚不赔，限时优惠。 | CR-007:加入会员稳赚不赔，限时优惠。 |
| S-006 | v2 | 0.2 | - | - | P3 | pass | - |
