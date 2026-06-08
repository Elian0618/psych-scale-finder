#!/usr/bin/env python3
"""Generate search queries for tracing psychology scales.

The script is intentionally heuristic and dependency-free. It expands a target
scale name into Chinese thesis-oriented queries and foreign-source fallback
queries that an agent can use with web search or academic search engines.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import OrderedDict
from urllib.parse import quote


ALIAS_FAMILIES: list[tuple[tuple[str, ...], tuple[str, ...]]] = [
    (
        ("黑暗人格", "黑暗特质", "dark personality", "dark traits"),
        (
            "黑暗三联征",
            "黑暗三联征量表",
            "黑暗十二条",
            "Dirty Dozen",
            "DD",
            "短式黑暗三联征量表",
            "Short Dark Triad",
            "SD3",
            "黑暗四联征",
            "Dark Triad",
            "Dark Tetrad",
        ),
    ),
    (
        ("光明人格", "light personality", "light triad"),
        (
            "光明人格量表",
            "光明三联征",
            "Light Triad Scale",
            "LTS",
        ),
    ),
]


def unique(items: list[str]) -> list[str]:
    seen: OrderedDict[str, None] = OrderedDict()
    for item in items:
        cleaned = re.sub(r"\s+", " ", item).strip()
        if cleaned:
            seen.setdefault(cleaned, None)
    return list(seen.keys())


def alias_variants(name: str) -> list[str]:
    lowered = name.lower()
    aliases: list[str] = []
    for triggers, family_aliases in ALIAS_FAMILIES:
        if any(trigger.lower() in lowered for trigger in triggers):
            aliases.extend(family_aliases)
    return aliases


def variants(name: str) -> list[str]:
    base = name.strip()
    parts = [base]
    parts.extend(alias_variants(base))

    for text in re.findall(r"[（(]([^）)]+)[）)]", base):
        parts.append(text.strip())

    no_paren = re.sub(r"[（(][^）)]+[）)]", " ", base).strip()
    parts.append(no_paren)

    for acronym in re.findall(r"\b[A-Z][A-Z0-9-]{1,}\b", base):
        parts.append(acronym)

    measure_words = (
        "scale",
        "questionnaire",
        "inventory",
        "survey",
        "index",
        "measure",
        "assessment",
        "量表",
        "问卷",
        "测验",
    )
    if not any(word in base.lower() for word in measure_words) and re.search(r"[A-Za-z]", base):
        parts.append(f"{base} scale")
        parts.append(f"{base} questionnaire")

    return unique(parts)


def build_queries(name: str, construct: str = "", author: str = "") -> dict[str, list[str]]:
    names = variants(name)
    seeds = names + ([construct] if construct else []) + ([author] if author else [])
    seeds = unique(seeds)

    source_suffixes = [
        "编制",
        "量表编制",
        "问卷编制",
        "汉化",
        "中文版",
        "信效度检验",
        "信度效度",
        "修订",
        "本土化",
        "测量工具",
        "测量学分析",
    ]
    cnki_source = [f"{seed} {suffix}" for seed in seeds for suffix in source_suffixes]

    cnki_sentence = []
    for seed in seeds:
        cnki_sentence.extend(
            [
                f'{seed} 和 "量表"',
                f'{seed} 和 "问卷"',
                f'{seed} 和 "附录"',
                f'{seed} 和 "调查问卷"',
                f'{seed} 和 "研究工具"',
                f'{seed} 和 "计分"',
                f'{seed} 和 "信效度"',
            ]
        )

    domestic_suffixes = [
        "附录",
        "调查问卷",
        "问卷题项",
        "量表题项",
        "硕士论文 附录",
        "博士论文 附录",
        "学位论文 问卷",
        "中文修订 信效度",
        "中文版 量表",
        "修订版 量表",
    ]
    foreign_suffixes = [
        "items",
        "questionnaire items",
        "validation",
        "appendix",
        "scoring manual",
        "original article",
        "PDF",
    ]
    repository_suffixes = [
        "site:ipip.ori.org",
        "site:osf.io",
        "site:phenxtoolkit.org",
        "site:healthmeasures.net",
        "site:psytoolkit.org",
        "APA PsycTests",
    ]
    general_suffixes = [
        "问卷",
        "量表",
        "题项",
        "PDF",
        "doc",
        "下载",
    ]

    domestic = [f"{seed} {suffix}" for seed in seeds for suffix in domestic_suffixes]
    foreign = [f"{seed} {suffix}" for seed in seeds for suffix in foreign_suffixes]
    repositories = [f"{seed} {suffix}" for seed in seeds for suffix in repository_suffixes]
    general = [f"{seed} {suffix}" for seed in seeds for suffix in general_suffixes]

    if author:
        if author.lower() not in name.lower():
            domestic.append(f"{author} {name} 附录")
            foreign.extend([f"{author} {name} original scale", f"{author} {name} measure"])
        if construct:
            domestic.append(f"{author} {construct} 问卷")

    primary_keyword = names[0] if names else name
    priority_names = unique([primary_keyword, *alias_variants(name)])[:8]
    specialized_sites = [
        f"心理学网站内搜索: {primary_keyword}",
        f"site:xinlixue.cn {primary_keyword} 量表",
        f"SUP量表库: https://www.suplb.cn/index.php?s=news&c=search&keyword={quote(primary_keyword)}",
        f"site:suplb.cn {primary_keyword} 量表",
        f"OBHRM百科首页: http://www.obhrm.net/首页",
        f"site:obhrm.net {primary_keyword} 量表",
    ]

    proquest = []
    for seed in seeds:
        proquest.extend(
            [
                f"ProQuest: {seed} scale",
                f"ProQuest: {seed} questionnaire",
                f"ProQuest: {seed} instrument",
                f"ProQuest: {seed} appendix",
            ]
        )

    source_focus_terms = []
    for seed in priority_names[:4]:
        source_focus_terms.extend(
            [
                f"{seed} 编制",
                f"{seed} 汉化",
                f"{seed} 中文版",
                f"{seed} 信效度检验",
                f"{seed} 修订",
            ]
        )
    if construct and construct != primary_keyword:
        source_focus_terms.extend(
            [
                f"{construct} 量表 编制",
                f"{construct} 量表 信效度",
            ]
        )

    thesis_focus_terms = []
    for seed in priority_names[:4]:
        thesis_focus_terms.extend(
            [
                f"{seed} 附录",
                f"{seed} 调查问卷",
                f"{seed} 量表 学位论文",
                f"{seed} 问卷 附录",
            ]
        )
    if construct and construct != primary_keyword:
        thesis_focus_terms.extend(
            [
                f"{construct} 量表 附录",
                f"{construct} 问卷 学位论文",
            ]
        )

    cnki_fast_path_commands = [
        *(f"embedded-cnki-search: {seed}" for seed in priority_names[:4]),
        f"embedded-cnki-search: {' OR '.join(source_focus_terms[:8])}",
        "optional-installed-cnki-advanced-search: 有 cnki-advanced-search 时再做 CSSCI/北大核心/CSCD 过滤；没有时用 embedded-cnki-search 多查询替代",
        f"embedded-cnki-search: {' OR '.join(thesis_focus_terms[:8])}",
        "optional-installed-cnki-navigate-pages: 有 cnki-navigate-pages 时按被引/下载排序；没有时先用第一页可见被引/下载数筛选",
        "embedded-cnki-detail: 对候选源头文、中文修订文、硕博论文逐篇抽取题名、作者、摘要、关键词、来源、参考线索",
        "mcp__chrome_devtools__evaluate_script: 在详情页运行 scripts/cnki_download_audit.js，先判断 direct_pdf / full_caj_only / page_caj_only / chapter_caj_only / online_read_only",
        "embedded-cnki-download: 仅在用户已登录且有权限时下载候选硕博论文 PDF/CAJ，用于检查研究工具和附录",
        "local-script: python3 scripts/caj_to_pdf.py path/to/paper.caj --output path/to/paper.pdf --setup",
        "local-script: python3 scripts/render_pdf_pages.py path/to/paper.pdf --pages 1-5 --output-dir rendered-pages --setup --deps-dir .psych-scale-finder-cache/pdf-render-deps",
    ]

    return {
        "cnki_fast_path_commands": unique(cnki_fast_path_commands),
        "cnki_topic_source_queries": unique(cnki_source),
        "cnki_sentence_thesis_queries": unique(cnki_sentence),
        "cnki_thesis_reading_targets": [
            "文献综述：变量测量工具名称、演变历程、基本信息、参考文献",
            "研究工具/研究设计：计分方式、题目数量、反向计分题、维度数、信效度",
            "参考文献：量表编制、汉化、修订、信效度检验源头文献",
            "附录/调查问卷：具体题目；多找几篇对照翻译和是否节选",
        ],
        "domestic_thesis_queries": unique(domestic),
        "specialized_chinese_scale_sites": unique(specialized_sites),
        "foreign_original_queries": unique(foreign),
        "proquest_queries": unique(proquest),
        "repository_queries": unique(repositories),
        "general_web_low_confidence_queries": unique(general),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Expand psychology scale search queries.")
    parser.add_argument("scale_name", help="Target scale name, Chinese or English.")
    parser.add_argument("--construct", default="", help="Optional construct keyword.")
    parser.add_argument("--author", default="", help="Optional author/year hint.")
    parser.add_argument("--format", choices=["json", "text"], default="text")
    args = parser.parse_args()

    queries = build_queries(args.scale_name, args.construct, args.author)
    if args.format == "json":
        print(json.dumps(queries, ensure_ascii=False, indent=2))
        return

    for section, values in queries.items():
        print(f"\n[{section}]")
        for value in values:
            print(value)


if __name__ == "__main__":
    main()
