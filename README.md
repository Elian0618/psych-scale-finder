# Codex Skill：Psych Scale Finder【心理量表追踪器】

![Codex Skill](https://img.shields.io/badge/Codex-Skill-blue)
![CNKI First](https://img.shields.io/badge/workflow-CNKI--first-1769AA)
![Python](https://img.shields.io/badge/scripts-Python%20%7C%20JavaScript-green)
![Status](https://img.shields.io/badge/status-research--assistant-orange)

![Psych Scale Finder Overview](assets/psych-scale-finder-overview.png)

> **权限声明：** 本项目是一个本地 Codex skill，不提供知网账号、不绕过登录、不破解验证码、不代替机构授权。使用者需要自行拥有 CNKI/学校/机构访问权限。所有检索、下载和抽取动作都应在用户授权的浏览器会话或用户提供的本地文件中完成。

> **使用声明：** 本 skill 的目标是帮助研究者追踪心理量表来源、定位硕博论文附录、核对维度与计分方式。正式用于论文、问卷施测或发表前，请回到原始文献、中文修订文献或授权版本再次核验。

## 一句话介绍

**Psych Scale Finder** 是一个帮你找心理量表的 Codex skill：先查知网源头文献和硕博论文附录，再核对中文修订、量表网站和原始英文文献，最后输出可验证的量表结构、题项定位、计分方式和真实性等级。

## 为什么需要它？

找心理量表经常不是“搜一下量表名”这么简单。

你可能遇到过这些问题：

- **痛点一：量表名字混乱。** 同一个量表可能有中文名、英文名、缩写、旧译名、修订版、简版，搜错一个词就漏掉关键来源。
- **痛点二：题项藏在硕博论文附录里。** 正文只写“采用某某量表”，真正题项在附录，附录又可能是 PDF、CAJ 或图片页。
- **痛点三：二手转载不可靠。** 量表网站、论坛、文档转载常常缺少原始出处、维度、反向题、计分方式，甚至混入改写题项。
- **痛点四：知网流程容易断。** 登录、验证码、机构权限、下载链接、CAJ 转 PDF、PDF 抽取，每一步都可能卡住。

别急！您的专属心理量表追踪器 `Psych Scale Finder` 已就位。

它会像一个研究助理一样，先帮你把检索路线铺开，再逐步确认：这个量表到底是哪一个版本？源头文献在哪里？中文修订是谁做的？硕博论文附录有没有完整题项？题号、维度、反向计分和计分范围是否一致？

## 核心功能

- **知网优先检索**：优先查 CNKI 源头论文、中文修订/信效度论文、硕博论文附录。
- **登录预检**：开始找中文量表前，先确认 CNKI skill、浏览器工具、登录状态、验证码和下载权限。
- **查询扩展**：自动扩展中文名、英文名、缩写、变量名、作者名、附录关键词。
- **附录定位**：从 PDF/文本中定位“附录、调查问卷、量表、测量项目、问卷题项”等关键段落。
- **CAJ/PDF 辅助处理**：提供 CAJ 转 PDF、PDF 页面渲染和本地抽取脚本。
- **真实性验证**：记录来源链、访问状态、页码/附录位置、题量、维度、计分和风险点。
- **研究者报告**：输出量表内容、维度计分、数据来源、验证等级和论文写作参考语。

## 安装方式

推荐使用一键安装脚本。它会同时安装：

- `psych-scale-finder`
- 依赖的 `cnki-*` 系列 skills
- `chrome-devtools` MCP 配置

```bash
git clone https://github.com/Elian0618/psych-scale-finder.git
cd psych-scale-finder
bash install.sh
```

然后重启 Codex，或新开一个线程，让 skill 和 MCP 配置刷新。

> 注意：安装脚本只负责配置工具链，不提供 CNKI 账号或机构权限。CNKI 登录、学校图书馆认证和验证码仍需用户本人在 Chrome 中完成。

## 使用示例

```text
[$psych-scale-finder] 帮我找职业紧张感量表（22题版）
```

```text
[$psych-scale-finder] 找一下中文版心理资本量表，最好有题项、维度和计分方式。
```

```text
[$psych-scale-finder] 我有一篇硕士论文 PDF，帮我检查附录里有没有完整问卷题项。
```

## 仓库内容

```text
SKILL.md                         # skill 主说明与工作流
agents/openai.yaml               # Codex/OpenAI agent metadata
scripts/expand_scale_queries.py  # 生成中英文检索式
scripts/extract_scale_sections.py# 从 PDF/文本中定位量表段落
scripts/cnki_download_audit.js   # 审计 CNKI 下载链接类型
scripts/caj_to_pdf.py            # CAJ 转 PDF 辅助脚本
scripts/render_pdf_pages.py      # PDF 页面渲染/OCR 辅助脚本
```

## 重要边界

本 skill 不会绕过付费墙、登录墙、机构权限或验证码。CNKI 登录、学校图书馆认证和验证码处理都必须由用户本人完成。

如果 CNKI 无法使用，skill 会明确报告卡点，例如：`cnki_login_needed`、`cnki_captcha`、`cnki_tool_blocked` 或 `cnki_access_blocked`，而不会把普通网页搜索伪装成“已经查过知网”。
