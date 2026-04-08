# AGENTS.md

本文件补充 Agent 平台相关的行为约束。排版工作流和验证清单见 SKILL.md。

## 输出路径规则

- 默认输出到 Markdown 同级 `wechat output/`，不要多嵌套一层目录
- Windows：不要输出 `/tmp/` 路径，用真实本地路径或 `127.0.0.1` 地址
- 给结果时把本地服务地址和本地文件地址都说清楚

## 主题兼容性规则

- 已有主题 ID 是兼容敏感的，不要改名
- `minimal-flex` 是唯一支持 variant 控制（accent / heading-align / divider-style / strong-style）的主题
- 画廊的「极简」分组只展示 `minimal-flex` 一个入口，不列出多个 minimal 子主题

## 样式选择持久化

- 优先读写 `selected-style.json`（结构化，含 variant 信息）
- 保持 `selected-theme.txt` 向后兼容（只含主题 ID）
- 两个文件位于系统临时目录 `wechat-format/` 下

## 发布规则

- 不要改动微信 API 行为，除非任务明确要求
- `publish.py` 需要 `config.json` 中的 `wechat` 配置，纯排版可不填

## 入口文件

| 文件 | 用途 |
|------|------|
| `scripts/format.py` | Markdown → 微信兼容 HTML |
| `scripts/publish.py` | 排版结果 → 公众号草稿箱 |
| `templates/gallery.html` | 主题画廊选择器 |
| `templates/preview.html` | 单主题预览 |
| `themes/*.json` | 主题定义文件 |
