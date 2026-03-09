# 规则库 YAML 化升级说明（v0.2）

## 变更摘要
- 规则文件 `rule-library/content-compliance-rules-v0.2.yaml` 已切换为标准 YAML 结构。
- 规则加载默认使用 `yaml.safe_load`。
- 保留 JSON 回退兼容（迁移期使用），并新增严格模式：`--strict-yaml`。

## 运行方式
1. 安装依赖：
   - `cd output/compliance-assistant/automation`
   - `python3 -m pip install -r requirements.txt`
2. 常规运行（兼容模式）：
   - `python3 rule_hit_runner.py`
3. 校验运行（严格模式，推荐用于 CI 或发版前检查）：
   - `python3 rule_hit_runner.py --strict-yaml`

## 升级注意事项
- 若规则 YAML 存在缩进、冒号或列表语法错误，严格模式会直接失败并返回错误。
- 兼容模式下 YAML 失败会尝试 JSON 回退，适合存量迁移，但不建议长期依赖。
- 建议在团队流程中将 `--strict-yaml` 作为规则发布前的必跑检查。
