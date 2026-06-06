# AI Agent Skill：Psych Scale Finder【心理量表追踪器】

![AI Agent Skill](https://img.shields.io/badge/AI%20Agent-Skill-blue)
![CNKI First](https://img.shields.io/badge/workflow-CNKI--first-1769AA)
![Python](https://img.shields.io/badge/scripts-Python%20%7C%20JavaScript-green)
![Status](https://img.shields.io/badge/status-research--assistant-orange)

![Uploading ChatGPT Image 2026年6月5日 11_24_08.png…]()

> **权限声明：** 本项目是一个本地 AI agent skill，不提供知网账号、不绕过登录、不破解验证码、不代替机构授权。使用者需要自行拥有 CNKI/学校/机构访问权限。所有检索、下载和抽取动作都应在用户授权的浏览器会话或用户提供的本地文件中完成。

> **使用声明：** 本 skill 的目标是帮助研究者追踪心理量表来源、定位硕博论文附录、核对维度与计分方式。正式用于论文、问卷施测或发表前，请回到原始文献、中文修订文献或授权版本再次核验。

## 一句话介绍

**Psych Scale Finder** 是一个帮 AI agent 找心理量表的研究工作流：先查知网源头文献和硕博论文附录，再核对中文修订、量表网站和原始英文文献，最后输出可验证的量表结构、题项定位、计分方式和真实性等级。

它不是普通关键词搜索，而是把“找量表”拆成一套可复用的 agent 操作流程：检索、下载审计、附录定位、本地抽取、来源链闭合和风险标注。

## 为什么需要它？

找心理量表经常不是“搜一下量表名”这么简单。

你可能遇到过这些问题：

- **痛点一：量表名字混乱。** 同一个量表可能有中文名、英文名、缩写、旧译名、修订版、简版，搜错一个词就漏掉关键来源。
- **痛点二：题项藏在硕博论文附录里。** 正文只写“采用某某量表”，真正题项在附录，附录又可能是 PDF、CAJ 或图片页。
- **痛点三：二手转载不可靠。** 量表网站、论坛、文档转载常常缺少原始出处、维度、反向题、计分方式，甚至混入改写题项。

别急！您的专属心理量表追踪器 `Psych Scale Finder` 已就位。

它会像一个研究助理一样，先帮你把检索路线铺开，再逐步确认：这个量表到底是哪一个版本？源头文献在哪里？中文修订是谁做的？硕博论文附录有没有完整题项？题号、维度、反向计分和计分范围是否一致？

## 核心功能

- **知网优先检索**：优先查 CNKI 源头论文、中文修订/信效度论文、硕博论文附录。
- **登录预检**：开始找中文量表前，先确认 CNKI 工具、浏览器工具、登录状态、验证码和下载权限。
- **查询扩展**：自动扩展中文名、英文名、缩写、变量名、作者名、附录关键词。
- **附录定位**：从 PDF/文本中定位“附录、调查问卷、量表、测量项目、问卷题项”等关键段落。
- **CAJ/PDF 辅助处理**：提供 CAJ 转 PDF、PDF 页面渲染和本地抽取脚本。
- **真实性验证**：记录来源链、访问状态、页码/附录位置、题量、维度、计分和风险点。
- **研究者报告**：输出量表内容、维度计分、数据来源、验证等级和论文写作参考语。

## 适用的 AI Agent 环境

只要你的 AI agent 能做到下面几件事，就可以使用这个 skill：

- 能读取 `SKILL.md` 作为任务说明或系统提示；
- 能运行本地 Python / JavaScript 脚本；
- 能读取用户提供的 PDF、CAJ、文本或截图；
- 能控制浏览器，或接入类似 `chrome-devtools` 的浏览器工具；
- 能使用用户本人已经登录和授权的 CNKI/机构访问环境。

如果 agent 没有浏览器控制能力，它仍然可以使用本 skill 的本地文件抽取和报告生成部分，但不能实时检索知网或下载硕博论文。

## 快速安装

一键安装脚本会同时安装：

- `psych-scale-finder`
- 依赖的 `cnki-*` 系列 skills
- `chrome-devtools` MCP 配置

```bash
git clone https://github.com/Elian0618/psych-scale-finder.git
cd psych-scale-finder
bash install.sh
```

安装后请重启你的本地 agent 环境，或新开一个会话，让 skill 和 MCP 配置刷新。

> 注意：安装脚本只负责配置工具链，不提供 CNKI 账号或机构权限。CNKI 登录、学校图书馆认证和验证码仍需用户本人在 Chrome 中完成。

## 通用接入方式

如果你的 agent 不使用一键安装脚本，可以手动接入：

1. 把 `SKILL.md` 放进 agent 的 system prompt、developer prompt、knowledge base 或 skill registry。
2. 把 `scripts/` 目录挂载给 agent，并允许它运行其中的 Python/JavaScript 脚本。
3. 如果需要知网实时检索，额外配置 CNKI 相关 skills 和浏览器控制工具。
4. 让 agent 在执行前先读取并遵守 `SKILL.md` 的 CNKI 预检、下载优先、本地抽取和验证报告流程。

推荐给 agent 的启动提示：

```text
Before searching for any psychological scale, read and follow SKILL.md in this repository.
Use the scripts directory for query expansion, CNKI download auditing, PDF/CAJ handling, and appendix extraction.
Always report CNKI access status and source-chain confidence.
```

## 使用示例

复制下面任意一句给你的 AI agent：

```text
使用 psych-scale-finder，帮我找职业紧张感量表（22题版）。
```

```text
使用 psych-scale-finder，找一下中文版心理资本量表，最好有题项、维度和计分方式。
```

```text
使用 psych-scale-finder，帮我核对这个量表的题项、维度、反向题和计分方式是否可靠。
```

## 仓库内容

```text
psych-scale-finder/
├── SKILL.md
├── README.md
├── install.sh
├── agents/
│   └── openai.yaml
├── assets/
│   └── psych-scale-finder-overview.png
└── scripts/
    ├── expand_scale_queries.py
    ├── extract_scale_sections.py
    ├── cnki_download_audit.js
    ├── caj_to_pdf.py
    └── render_pdf_pages.py
```

文件说明：

```text
SKILL.md
  skill 主说明与完整工作流。

install.sh
  一键安装 psych-scale-finder、CNKI 依赖 skills 和浏览器 MCP 配置。

agents/openai.yaml
  agent metadata，可供支持 agent/skill registry 的环境读取。

assets/psych-scale-finder-overview.png
  项目主页展示图。

scripts/expand_scale_queries.py
  生成中文、英文、缩写、附录关键词等检索式。

scripts/extract_scale_sections.py
  从 PDF 或文本中定位可能包含量表的段落。

scripts/cnki_download_audit.js
  审计 CNKI 详情页下载链接类型。

scripts/caj_to_pdf.py
  将本地 CAJ 文件转换为 PDF 的辅助脚本。

scripts/render_pdf_pages.py
  将 PDF 页面渲染为图片，用于视觉检查或 OCR 辅助。
```

## 重要边界

本 skill 不会绕过付费墙、登录墙、机构权限或验证码。CNKI 登录、学校图书馆认证和验证码处理都必须由用户本人完成。

如果 CNKI 无法使用，skill 会明确报告卡点，例如：`cnki_login_needed`、`cnki_captcha`、`cnki_tool_blocked` 或 `cnki_access_blocked`，而不会把普通网页搜索伪装成“已经查过知网”。

