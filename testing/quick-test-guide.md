# 合规小助手快速测试指南

## 1) 准备输入
将 `testing/test-cases-v1.json` 复制为：

- `automation/sample-inputs.json`

## 2) 执行审核
在仓库根目录运行：

```bash
python3 automation/rule_hit_runner.py
```

## 3) 查看输出
- 运行报告：`automation/sample-run-report.md`
- 审核记录(JSON)：`automation/sample-review-records.json`
- 审核记录(MD)：`automation/sample-review-records.md`
- 历史台账：`review-log.md`

## 4) 预期现象
- T-001、T-002 应被限制（高风险）
- T-003、T-004、T-006 通常放行
- T-005 依规则可能触发营销类提醒
