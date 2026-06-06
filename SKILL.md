---
name: psych-scale-finder
description: "Locate, verify, and extract psychology scale items using a CNKI-first citation-chain workflow: authoritative Chinese source/revision papers first, their citing theses/dissertation appendices second, then specialized scale sites and foreign databases. Use when users ask for psychological questionnaires, scales, measures, items, dimensions, scoring, Chinese versions, appendix extraction, or source tracing."
---

# Psychological Scale Finder

Use this skill to trace psychology scales with a practical researcher workflow: CNKI authoritative Chinese source/revision paper search first, CNKI citing-thesis appendix search second, specialized Chinese scale sites third, and foreign databases/open sources when domestic evidence is unavailable. The goal is not just to find items, but to produce a source-grounded, permission-aware extraction that a researcher can verify.

## Operating Rules

- Prefer primary or traceable sources: thesis appendix with page number, original article/manual, official repository, or author page.
- Do not bypass paywalls, login walls, or institutional access. If a source is inaccessible, report the access limit and ask for a PDF or accessible link.
- Because CNKI thesis appendices are often the most direct route to Chinese scale items, perform a CNKI access preflight before substantive scale searching. Do not skip CNKI silently.
- Do not start by broadly collecting random theses. First try to identify an authoritative Chinese source/revision/validation paper for the scale. If such an anchor paper exists, use its CNKI citing literature (`引证文献`) to find theses/dissertations that cite the anchor and are likely to include the scale appendix.
- When CNKI skills are installed and the `chrome-devtools` MCP tools are available, use the CNKI skills for live CNKI search/detail/download work before falling back to generic web search.
- CNKI login, institutional access, and Tencent slider captchas must be handled manually by the user in Chrome. At the start of the task, ask the user to confirm they want Codex to use their CNKI/institutional access, then verify whether the session is logged in. Pause and ask the user to complete login/captcha when needed; do not attempt to bypass access controls.
- Do not preemptively stop because a scale may be copyrighted. First try to locate and verify the item source. Distinguish three things clearly: (1) internal inspection of a user-authorized/user-provided source, (2) source/page/appendix location, and (3) verbatim reproduction in the chat. Provide verbatim item text only when allowed by the source, user-provided/access-authorized context, and applicable content-sharing constraints; otherwise provide exact location, item numbers, dimensions, scoring, reverse coding, and short compliant excerpts where useful.
- Always separate **extracted text** from **inference**. Mark uncertain translations, missing reverse coding, modified item wording, and secondary citations.
- Never present a thesis appendix as the original source. Preserve the chain: thesis source -> cited Chinese adaptation -> original scale.

## CNKI Skill Integration

Use these local CNKI skills when they are available in the current Codex session:

| Task | Preferred skill |
|---|---|
| Keyword/source-paper search | `cnki-search` |
| Filtered source-paper search by field, journal, year, or source category | `cnki-advanced-search` |
| Parse an already open CNKI results page | `cnki-parse-results` |
| Sort or paginate CNKI results | `cnki-navigate-pages` |
| Extract title, authors, abstract, keywords, source, and citation metadata from a paper detail page | `cnki-paper-detail` |
| Trigger PDF/CAJ download when the user is logged in and has access | `cnki-download` |
| Export bibliographic data to Zotero/RIS/GB/T 7714 | `cnki-export` |

Operational constraints:

- If `cnki-*` skills are not visible in the available skills list, say that Codex must be restarted after installation/configuration, then continue with open web sources or user-provided files.
- If `chrome-devtools` MCP tools are not available, say the CNKI skills cannot run in this session and continue with open web/local-file fallback.
- If the browser/navigation tool required by the CNKI skill is missing, report that exact tool blocker before falling back. Do not describe the fallback result as a completed CNKI search.
- If CNKI shows `not_logged_in`, ask the user to log in through Chrome and then continue.
- If CNKI shows a captcha, ask the user to solve it manually in Chrome and then continue.
- If download is blocked by institutional access, report the title and URL, then ask the user to provide the PDF/CAJ or use an accessible institutional login.
- Do not use CNKI online reading, redirect readers, or page-by-page navigation as the primary extraction route. The primary route is always: search CNKI -> open paper detail -> download the full text to local disk -> parse/read the local file -> extract the scale.
- Prefer a real full-text PDF. If CNKI only exposes CAJ or page-range CAJ for a thesis, stop and report that local PDF extraction is blocked unless a CAJ converter/reader is available. Only use online reading or page-range downloads as a fallback after explicitly marking that PDF download failed.
- Before clicking any CNKI download link, run the download audit JavaScript in `scripts/cnki_download_audit.js` with `mcp__chrome-devtools__evaluate_script`. Use its classification to decide the next step:
  - `direct_pdf`: click/download the direct PDF link.
  - `full_caj_only`: download full CAJ, then run `scripts/caj_to_pdf.py`.
  - `page_caj_only`: download the likely appendix page range, then run `scripts/caj_to_pdf.py`.
  - `no_fulltext`: report the access/download blocker.

CNKI evidence to capture for every candidate:

- Search query, search field, filter, sort order, and result rank.
- Title, authors, source, date, citation/download counts when visible.
- CNKI detail URL.
- Whether the full text/appendix was opened, downloaded, or only metadata was visible.
- If downloaded, local file path and page/appendix number where the scale appears.
- Whether the candidate is a source paper, Chinese adaptation/validation paper, thesis appendix, or low-confidence secondary use.

## Workflow

0. **CNKI access and permission preflight**
   - State that CNKI is a primary route for Chinese scale item discovery and ask the user to confirm use of their CNKI/institutional access when the task involves a Chinese scale.
   - Check whether the current session has the required CNKI skills and browser tools. Record one of:
     - `cnki_ready`: CNKI skills and browser navigation/evaluation tools are available.
     - `cnki_login_needed`: tools are available but CNKI is not logged in.
     - `cnki_captcha`: user must solve a visible captcha.
     - `cnki_tool_blocked`: required browser/navigation tools are missing.
     - `cnki_access_blocked`: CNKI page is reachable but download/open access is denied.
   - If login or captcha is needed, pause and ask the user to complete it in Chrome, then continue from the same step.
   - If CNKI is blocked by missing tools or access, say exactly which layer failed and continue with open web/local-file fallback. The final answer must include this blocker.

1. **Normalize the request**
   - Identify the target scale name, construct, author/year, abbreviation, population, language, and whether the user wants full items, Chinese version, scoring, or source list.
   - If only a Chinese construct is given, generate English candidates before searching.

2. **Expand search queries**
   - Run `python3 scripts/expand_scale_queries.py "scale name"` when useful.
   - Keep Chinese and English names, abbreviations, construct names, author names, and likely translation variants.

3. **CNKI authoritative Chinese anchor-paper search**
   - Use `cnki-search` for broad search and `cnki-advanced-search` for filtered source-paper search when available.
   - In CNKI, use **主题** search with the scale name, construct name, English abbreviation, original author, and likely Chinese variants.
   - Prefer source categories and venues that make a paper a credible Chinese anchor: CSSCI, 北大核心, CSCD, recognized psychology/medicine/management journals, and high-citation validation/revision papers.
   - Prioritize titles like:
     - `XXX的编制`
     - `XXX量表的编制`
     - `XXX的汉化`
     - `XXX中文版`
     - `XXX的信效度检验`
     - `XXX量表的修订`
   - Use `cnki-navigate-pages` to sort by citations/downloads when useful.
   - Use `cnki-paper-detail` on high-probability source papers to extract metadata, abstract, keywords, source, and citation clues.
   - Treat a paper as an **anchor paper** only when it plausibly defines, translates, revises, or validates the Chinese version of the target scale. Extract scale name, author/year, dimensions, item count, scoring, reliability/validity, sample, original reference chain, citation/download counts, and CNKI detail URL.
   - If multiple anchor candidates exist, rank them by:
     1. direct title match to compilation/revision/Chinese version/validity;
     2. authoritative journal/source category;
     3. citation count and downstream use;
     4. completeness of dimensions, item count, scoring, and original reference chain.
   - If no credible authoritative anchor paper is found, say so explicitly, then fall back to direct thesis appendix search in Step 4B.

4. **CNKI citation-chain thesis/dissertation appendix search**
   - **Preferred route when an anchor paper exists:** open the anchor paper's CNKI detail/citation network and inspect `引证文献` / citing literature.
   - In the citing-literature list, prioritize source type **学位论文** and then titles/abstracts containing `附录`, `调查问卷`, `问卷`, `量表`, `研究工具`, `测量工具`, or the target scale/construct name.
   - Sort citing literature by relevance, citations, or downloads when useful. The best candidates are theses/dissertations that cite the anchor paper and use the same construct in empirical research.
   - Use `cnki-paper-detail` to inspect candidate citing theses. Capture the anchor-paper relationship: anchor title, anchor CNKI URL, citing thesis title, result rank, source type, citation/download counts, and why the thesis is likely to contain an appendix.
   - Use `cnki-download` only after the user is logged in and has download permission. Download the full thesis before extraction whenever possible.
   - If CNKI citation-network navigation is unavailable in the current toolset, use a fallback query strategy based on the anchor paper:
     - exact anchor title + `学位论文`
     - exact anchor title + `附录`
     - anchor author + scale name + `调查问卷`
     - scale name + anchor author/year + `硕士论文` / `博士论文`
   - **4B fallback when no anchor paper exists or citation route fails:** use direct thesis searches such as `量表名 附录`, `量表名 调查问卷`, `变量名 量表 学位论文`, `变量名 问卷 附录`. Mark this route as lower confidence than the anchor-citation route.
   - If the live CNKI interface supports it, use **高级检索 -> 句子检索** and limit document type to **学位论文**. If the installed `cnki-advanced-search` skill cannot set these exact controls, search with explicit keywords (`学位论文`, `硕士论文`, `博士论文`, `附录`, `调查问卷`) and filter candidates by source type in the result list.

5. **Download-first local extraction**
   - Attempt local full-text download before any reader-based extraction.
   - First audit the CNKI detail page download links:
     ```bash
     # Use this file's function body with mcp__chrome-devtools__evaluate_script.
     scripts/cnki_download_audit.js
     ```
   - Prefer direct PDF download. After triggering download, verify that a new local PDF appears in the browser download directory or another known local path.
   - If a PDF was downloaded, immediately run local extraction:
     ```bash
     python3 scripts/extract_scale_sections.py path/to/paper.pdf --scale "Scale Name"
     ```
   - If the PDF text extraction is incomplete, visually inspect the local PDF pages containing `附录`, `调查问卷`, `量表`, `测量项目`, `问卷题项`, `Appendix`, `Scale`, or the target scale name.
   - If CNKI provides only CAJ or page-range CAJ, convert the local CAJ file to PDF before extraction:
     ```bash
     python3 scripts/caj_to_pdf.py path/to/paper.caj --output path/to/paper.pdf --setup
     ```
   - If `scripts/caj_to_pdf.py` reports missing dependencies that cannot be installed or compiled in the current environment, report the CAJ file path and exact blocker instead of continuing to jump through CNKI reader pages.
   - If the converted PDF is image-only or text extraction returns no likely sections, render the relevant pages for visual/OCR inspection:
     ```bash
     python3 scripts/render_pdf_pages.py path/to/paper.pdf --pages 1-5 --output-dir path/to/rendered-pages --setup --deps-dir .psych-scale-finder-cache/pdf-render-deps
     ```
     If `tesseract` is available, add `--ocr`; otherwise inspect the rendered page images directly.
   - Use CNKI online reading, redirect readers, or page-range downloads only as fallback when:
     - direct PDF download failed;
     - CAJ cannot be converted locally; and
     - the fallback path is likely to expose the needed appendix faster.
   - Open or extract downloaded theses and inspect:
     - **文献综述**: measurement-tool names, history/evolution, basic information, and cited source papers.
     - **研究工具/研究设计**: item count, dimensions, scoring, reverse-coded items, reliability/validity.
     - **参考文献**: source articles or original scale publications.
     - **附录/调查问卷**: concrete item wording.
   - Compare multiple theses. Some appendices only show partial scales or contain loose translations.

6. **Specialized Chinese scale sites**
   - Search these after CNKI, or use them to discover source-paper names and citation clues:
     - 心理学网: `https://xinlixue.cn/`
     - SUP 量表库: `https://www.suplb.cn/index.php?s=news&c=search&keyword=`
     - OBHRM百科: `http://www.obhrm.net/首页`
   - Use these sites as leads unless they clearly provide original source details. Verify with CNKI/source literature before finalizing.
   - SUP may support scale requests, but user-contributed results need independent verification.
   - OBHRM often includes source literature, reliability/validity, items, scoring, and sometimes Word downloads; use its references to trace source papers.

7. **Foreign and institutional database fallback**
   - If domestic sources do not provide reliable items or Chinese versions, search original foreign literature and measure repositories.
   - Include ProQuest series full-text databases when available through a university library: `https://search.proquest.com/index`.
   - Also check official/open repositories such as IPIP, PsyToolkit, OSF, author/institution pages, PhenX, PROMIS/HealthMeasures, and APA PsycTests metadata.
   - Do not bypass institutional login requirements; report access limits and ask for a user-provided PDF if needed.

8. **General browser/social search as low-confidence fallback**
   - Search `XXX问卷`, `XXX量表`, `XXX scale items`, `XXX questionnaire`.
   - Treat search-engine snippets, forums, social media, and reposted documents as low-confidence leads. Use them only to identify possible source names or citations.

9. **Collect candidate sources**
   - Record title, author, year, institution/journal, URL/DOI, access status, and why it likely contains the scale.
   - For CNKI anchor papers, record source category/journal authority, query/filter, result rank, citation/download counts, detail URL, and why it qualifies or does not qualify as an anchor.
   - For CNKI citing theses, record the anchor paper they cite, citation-network route or fallback query, result rank, detail URL, and download status.
   - Prefer downloadable PDFs or HTML with visible appendix text.
   - If multiple citing theses contain the same scale, compare wording and citations instead of trusting the first hit.

10. **Extract candidate appendix sections**
   - For local PDFs or text files, run:
     ```bash
     python3 scripts/extract_scale_sections.py path/to/paper.pdf --scale "Scale Name"
     ```
   - Inspect pages containing `附录`, `调查问卷`, `量表`, `测量项目`, `问卷题项`, `Appendix`, `Scale`, or the target scale name.
   - Keep page numbers. If PDF extraction is messy, visually inspect the relevant pages when layout matters.

11. **Reconstruct scale structure**
   - Extract item text, item numbering, dimensions/subscales, reverse-coded items, response anchors, scoring method, sample/population, and citation lines.
   - Detect warning signs: missing items, paraphrased items, deleted items, renamed dimensions, mixed scales, machine translation, or items copied from another secondary thesis.

## Output Format

Use this structure unless the user asks otherwise. Prefer the user's researcher-friendly five-part format:

```markdown
## 1. 量表具体内容

- 量表：...
- 来源：...
- 对象：...
- 题项：...
- 计分：...
- 反向题：...

| No. | 维度 | 题项原文 | 反向 |
|---:|---|---|---|
| 1 | ... | ... | 否 |

The default goal is to find and present the original item wording, because researchers need copy-ready scale content. Do not paraphrase items as the main deliverable unless verbatim reproduction is blocked.

If exact item text is available and can be shared under the Operating Rules and content-sharing constraints, label the column `题项原文`.
If exact item text is visible in a source but cannot be fully reproduced in the chat, do not replace it with broad paraphrases. Instead:
- keep the item table focused on dimensions, item numbers, reverse coding, and any short compliant excerpt if useful;
- add an `原文定位` note with the exact source, appendix/page, section title, and how to find the original item text quickly;
- state clearly that the original wording was found but cannot be fully transcribed in the chat.
If exact item text is not found, explain what was found and what source should be checked next.

## 2. 量表维度计分

每个维度可以取对应题项的平均分，或按原文要求计算总分：

| 维度 | 题号 | 计分 |
|---|---|---|
| ... | ... | 平均分/总分 |
| 总体... | ... | 总平均分或总分 |

Include response anchors, reverse-coded items, deleted items, whether higher scores indicate higher construct level, and whether the scale uses mean scores or sum scores.

## 3. 数据来源

1. 官方源/原始源头：...
2. 国内权威期刊锚点论文（编制/汉化/修订/信效度）：...
3. 锚点论文的引证硕博论文附录来源：...
4. 量表网站/其他线索：...

For each source, include title, author, year, journal/institution, page or appendix when available, URL/DOI/access status, and why it is useful. Keep the source chain explicit: citing thesis appendix -> authoritative Chinese anchor paper -> original scale.

For CNKI sources, also include:
- CNKI skill used (`cnki-search`, `cnki-advanced-search`, `cnki-paper-detail`, `cnki-download`, etc.).
- CNKI preflight status (`cnki_ready`, `cnki_login_needed`, `cnki_captcha`, `cnki_tool_blocked`, or `cnki_access_blocked`).
- Search query/filter/sort order.
- Anchor-paper route: whether a credible authoritative journal source/revision paper was found; if yes, list title, journal/source category, citation/download counts, CNKI URL, and anchor qualification reason.
- Citing-thesis route: whether thesis candidates came from the anchor paper's `引证文献`; if yes, list anchor -> citing thesis chain and result rank.
- Result rank and citation/download counts when visible.
- Detail URL and download/open status.
- Local file path if a PDF/CAJ was downloaded or provided by the user.

## 4. 真实性快速验证

- 验证等级：A / B / C / D
- 是否看到题项原文：是/否；位置：...
- 源头链是否闭合：是/否；链条：引证硕博论文附录 -> 国内权威期刊锚点论文 -> 原始文献
- 关键一致性：题量、维度、计分、反向题、适用对象是否与源头一致
- 交叉印证：至少 1 个独立来源是否一致
- 风险提示：节选版/改写版/翻译差异/来源不可访问/版权量表/低可信转载

Use verification grades:
- **A**: original items are visible in an accessible or user-provided source, page/appendix is identified, and source chain plus at least one independent source are consistent.
- **B**: original items are visible and page/appendix is identified, but only one secondary source is available or one metadata field is incomplete.
- **C**: source chain metadata is plausible, but original items are not directly visible or only a scale-site/repost is available.
- **D**: only search snippets, uncited reposts, or inconsistent secondary sources are available.

## 5. 可直接复制到论文里的语言（仅供参考）

采用...量表（作者，年份）测查...。该量表共...道题目，包括...等...个维度。要求被试采用...点计分，从...到...回答题目。...题为反向计分。计算每个分量表题目的平均分/总分，分数越高表示...水平越高。

备注：这段文字仅作为论文写作参考，正式使用前请结合原文献、研究对象和导师/期刊要求修改。
```

If only candidates are found, keep the same five sections but replace the item table in `1. 量表具体内容` with a ranked `候选来源` table and explain why exact items are not available.

## Confidence Heuristics

- **High**: items visible in an accessible/user-provided source, page numbers captured, dimensions/scoring present, and source chain matches the original or recognized Chinese adaptation.
- **Medium**: items visible but one of dimensions, scoring, or original citation is incomplete; or multiple secondary sources disagree.
- **Low**: only metadata is found, appendix is missing, source is inaccessible, or wording appears modified without explanation.

## Script Notes

- `scripts/expand_scale_queries.py` prints Chinese and foreign query variants for search.
- `scripts/extract_scale_sections.py` extracts likely appendix/questionnaire snippets from PDF or text. It is a first-pass locator, not a final verifier.
- `scripts/cnki_download_audit.js` classifies CNKI detail-page download links before any download click, so PDF/CAJ/page-range decisions are explicit.
- `scripts/caj_to_pdf.py` wraps the `caj2pdf` toolchain, installs/checks its Python dependency path when requested, compiles `libjbigdec.so` when source files are present, and converts local CAJ files to PDF.
- `scripts/render_pdf_pages.py` splits and renders image-only PDFs into page PNGs for visual inspection or OCR fallback.
