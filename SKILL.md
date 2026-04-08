---
name: xiaohu-wechat-format
description: "Markdown 转微信公众号排版 HTML，支持主题画廊可视化选择和一键推送草稿箱。当用户说'排版''微信排版''格式化文章''format'或给出文章要求转公众号格式时使用。不处理封面生成（用 xiaohu-wechat-cover）、不处理评论管理。"
---

# xiaohu-wechat-format

公众号一键排版技能。把 Markdown / 纯文本转成微信公众号兼容的内联样式 HTML，AI 自动理解内容结构并增强排版，可视化选择主题后一键复制粘贴到微信后台。可选推送草稿箱。

## 适用场景

- 用户给出 Markdown 或纯文本文件路径，要求转公众号格式
- 用户说"排版""微信排版""格式化文章""format""把这篇转成微信格式"
- 用户说"推送""发公众号"（排版 + 推送联动）
- `/format 文件路径` 命令

## 不适用场景

- 只要生成封面图 → 使用 `xiaohu-wechat-cover` 子技能
- 评论管理 / 自动回复 → 不属于本技能（`scripts/comment_reply.py` 是独立工具）
- 要写文章内容（而非排版已有内容）→ 不是排版工具的职责

## 输入

**必须**：
- 文章来源：Markdown 文件路径 或 纯文本内容

**可选**：
- 主题名（默认打开画廊让用户选）
- 输出目录（默认为文章同级 `wechat output/`）
- Obsidian Vault 路径（用于解析 `![[image]]` wikilink 图片）
- 推送意图（是否同时推送到公众号草稿箱）

## 配置

首次使用需创建 `config.json`（从 `config.example.json` 复制后编辑）。

- `vault_root`：Obsidian Vault 根目录（可选，排版用）
- `settings.default_theme`：默认主题
- `wechat.app_id` / `wechat.app_secret`：仅推送时需要
- `config.json` 已在 `.gitignore` 中，不会被提交

## 脚本目录

`{baseDir}` = 本 SKILL.md 所在目录。

| 脚本 | 用途 |
|------|------|
| `scripts/format.py` | 排版：Markdown → 微信兼容 HTML |
| `scripts/publish.py` | 推送：HTML → 公众号草稿箱 |

> `scripts/comment_reply.py` 和 `scripts/generate.py` 是独立工具，不属于排版工作流。

## 工作流

### 第 1 步：确认文章

1. 如果用户给了文件路径，直接读取
2. 如果没给路径，问用户要文章路径
3. 读取文章内容，确认标题和字数

### 第 1.5 步：结构化预处理（仅在需要时）

读取文章后，检测 Markdown 结构完整度，决定是否需要 AI 结构化预处理。

**检测**：扫描全文，统计 `##` 标题、`**加粗**`、`- 列表`、`> 引用`、`` `代码` `` 等格式标记数量。

**判断**：
- 有 `##` 标题且格式标记合理 → **跳过**，直接进入第 2 步
- 缺少标题或几乎没有格式标记 → **执行结构化**

**结构化规则（底线：只加标记，不改内容）**：
1. 识别逻辑段落转换点，插入 `##` 标题（从内容中提炼，不编造）
2. 确保段落间有空行，长段落在语义转换处拆分
3. 识别并列内容加 `- ` 或 `1. ` 标记
4. 识别关键词、产品名加 `**加粗**`
5. 清理多余空行、修正缩进、统一标点
6. **不改措辞**：不调语序、不增删内容、不润色文字

**保存**：结构化后保存为系统临时目录下 `wechat-format/xxx-structured.md`，告知用户已自动补充结构。

### 第 2 步：AI 内容分析 + 自动套格式

分析文章内容结构（类型、元素、节奏），在 Markdown 层面自动套用排版容器：

| 内容特征 | 容器 | 说明 |
|----------|------|------|
| `**名字：**` 交替出现 | `:::dialogue[标题]` | 对话气泡，格式 `名字: 内容` |
| 3 张以上连续图片 | `:::gallery[标题]` | 横向滚动浏览 |
| 超长图片/流程图 | `:::longimage[标题]` | 固定高度纵向滚动 |
| 核心观点/金句 | `> [!important]` / `> [!tip]` / `> [!warning]` / `> [!callout]` | 一篇 1-3 处即可，不过度使用 |
| 章节转换 | `---` | 分隔符 |
| 图片说明 | `*说明文字*` | 图片后紧跟的斜体 |

处理完成后，保存为 `wechat-format/xxx-enhanced.md`。

### 第 2.5 步：推荐主题

根据内容分析推荐 3 个最适合的主题：

| 内容类型 | 推荐主题 |
|----------|----------|
| 深度长文/分析 | newspaper, magazine, ink |
| 科技产品/AI 工具 | bytedance, github, sspai |
| 访谈/对话体 | terracotta, coffee-house, mint-fresh |
| 教程/操作指南 | github, sspai, bytedance |
| 文艺/随笔 | terracotta, sunset-amber, lavender-dream |
| 活力/速报 | sports, bauhaus, chinese |

推荐主题通过 `--recommend` 参数传给脚本，在画廊中高亮显示。

### 第 3 步：打开主题画廊（默认）

```bash
python3 {baseDir}/scripts/format.py \
  --input "文章路径.md" \
  --gallery \
  --recommend newspaper magazine ink
```

输出默认写到文章同级 `wechat output/`。画廊用用户的**真实文章**渲染所有主题，用户点按钮切换预览，选中后一键复制到剪贴板。

### 第 3 步（备选）：直接指定主题

```bash
python3 {baseDir}/scripts/format.py \
  --input "文章路径.md" \
  --theme terracotta
```

### 第 4 步：确认结果

告诉用户：
- 优先提供已测试通过的 `127.0.0.1` 预览地址
- 同时补充 `wechat output/` 下的本地文件 URI
- 画廊模式：切换主题预览，点按钮复制，粘贴到公众号后台
- 直接模式：检查预览，点「复制到微信」按钮

## 输出规范

Agent 完成排版后，必须向用户提供以下信息：

1. **两个访问地址**：本地服务地址（`http://127.0.0.1:端口/gallery.html`）和本地文件地址（`file:///路径/wechat%20output/gallery.html`）
2. **使用说明**：在画廊中选择主题 → 点复制按钮 → 粘贴到公众号后台
3. **补充提醒**：复制后在公众号后台仍可微调文字

## 验证清单

排版完成后，Agent 必须检查：
1. 浏览器预览地址可访问（`127.0.0.1` 或 `file://` 至少一个能打开）
2. **同时告知用户两个地址**（不要只报一个）
3. 输出目录下存在 `gallery.html` 或 `preview.html` + `article.html`
4. 画廊模式下显示了主题列表

推送完成后（如适用）：
1. 返回了 `media_id`
2. 告知用户去"公众号后台 → 内容管理 → 草稿箱"查看

**绝不能出现**：
- 告诉用户 `/tmp/` 路径（Windows 上无法打开）
- 漏报本地文件 URI
- 配置文件缺失时给用户裸 Python traceback
- 排版结果中出现 `<style>` 标签（微信不支持）

---

## 推送到公众号草稿箱（可选）

用户说"推送""发公众号"时执行。需要在 `config.json` 中配置 `wechat.app_id` 和 `wechat.app_secret`。

```bash
python3 {baseDir}/scripts/publish.py \
  --dir "排版输出目录" \
  --cover "封面图路径（可选）"
```

也支持从 Markdown 直接推送（自动排版再推）：

```bash
python3 {baseDir}/scripts/publish.py \
  --input "文章.md" \
  --theme terracotta
```

## 封面图生成（可选）

排版完成后，用户说"配封面""生成封面"时，参见 `cover/SKILL.md` 子技能的完整工作流。

---

## 参考：可用主题

### 主干主题（9 个）

| 主题 | ID | 风格 |
|------|----|------|
| 赤陶 | terracotta | 暖橙色，满底圆角标题 |
| 字节蓝 | bytedance | 蓝青渐变，科技现代 |
| 中国风 | chinese | 朱砂红，古典雅致 |
| 报纸 | newspaper | 纽约时报风，严肃深度 |
| GitHub | github | 开发者风，浅色代码块 |
| 少数派 | sspai | 中文科技媒体红 |
| 包豪斯 | bauhaus | 红蓝黄三原色，先锋几何 |
| 墨韵 | ink | 纯黑水墨，极简留白 |
| 暗夜 | midnight | 深色底+霓虹色，赛博朋克 |

### 精选风格（7 个）

sports / mint-fresh / sunset-amber / lavender-dream / coffee-house / wechat-native / magazine

### 极简可调（1 个）

`minimal-flex`：支持 7 配色 × 3 对齐 × 6 分隔线 × 2 加粗风格组合。

### 模板系列（14 个）

四种布局（简约/聚焦/精致/醒目）× 多种配色，适合批量出品。

## 参考：参数详解

**format.py**：
- `--input` / `-i`：Markdown 文件路径（必须）
- `--gallery`：打开主题画廊（推荐默认使用）
- `--theme` / `-t`：直接指定主题名（跳过画廊）
- `--output` / `-o`：输出目录（默认：Markdown 同级 `wechat output/`）
- `--vault-root`：Obsidian Vault 根目录
- `--recommend`：推荐主题 ID 列表，画廊中高亮
- `--no-open`：不自动打开浏览器
- `--format`：输出格式 wechat/html/plain

**publish.py**：
- `--dir`：排版输出目录路径（已排版好的 HTML）
- `--input`：Markdown 文件路径（自动排版再推送）
- `--cover` / `-c`：封面图路径（默认搜索目录内 `cover.*`）
- `--title` / `-t`：文章标题（默认从 HTML 提取）
- `--theme`：排版主题（仅 `--input` 模式有效）
- `--author` / `-a`：作者名（默认读 config.json）
- `--dry-run`：只排版和上传图片，不推草稿箱

## 内置排版增强

脚本自动处理：
- **CJK 间距修复**：中英文/中数字之间自动加空格
- **加粗标点修复**：`**文字，**` → `**文字**，`
- **纯内联样式**：所有 CSS 写在 `style="..."` 属性上
- **列表模拟**：`<ul>/<ol>` → `<section>` + flexbox
- **外链转脚注**：`[text](url)` → 正文 `text[1]` + 文末脚注
- **图片处理**：`![[image.jpg]]` 自动搜索 Vault 并复制
- **多类型提示框**：`[!tip]`/`[!note]`/`[!important]`/`[!warning]`/`[!caution]`
- **图说识别**：图片后斜体 → 居中灰色图说
- **对话气泡**：`:::dialogue[标题]` → 左右交替
- **图片画廊**：`:::gallery[标题]` → 横向滚动
- **长图展示**：`:::longimage[标题]` → 纵向滚动

## 注意事项

- 依赖 Python `markdown` 库（`pip install markdown`）
- 图片在预览中可见，粘贴到微信后需手动上传（或用推送功能自动上传）
- 用户对排版不满意可切换主题重新生成
