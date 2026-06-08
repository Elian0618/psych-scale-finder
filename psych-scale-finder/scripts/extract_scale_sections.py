#!/usr/bin/env python3
"""Locate likely scale/questionnaire appendix sections in PDF or text files."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable


KEYWORDS = [
    "附录",
    "调查问卷",
    "正式问卷",
    "问卷题项",
    "量表题项",
    "测量题项",
    "测量项目",
    "量表",
    "问卷",
    "Appendix",
    "Questionnaire",
    "Scale",
    "Measure",
    "Items",
]


def read_pdf(path: Path) -> list[tuple[int, str]]:
    errors: list[str] = []

    for module_name in ("pypdf", "PyPDF2"):
        try:
            module = __import__(module_name)
            reader = module.PdfReader(str(path))
            pages = []
            for index, page in enumerate(reader.pages, start=1):
                pages.append((index, page.extract_text() or ""))
            return pages
        except Exception as exc:  # pragma: no cover - depends on environment
            errors.append(f"{module_name}: {exc}")

    try:
        proc = subprocess.run(
            ["pdftotext", "-layout", str(path), "-"],
            check=True,
            text=True,
            capture_output=True,
        )
        chunks = re.split(r"\f+", proc.stdout)
        return [(index, text) for index, text in enumerate(chunks, start=1)]
    except Exception as exc:  # pragma: no cover - depends on environment
        errors.append(f"pdftotext: {exc}")

    raise RuntimeError("Could not extract PDF text. Install pypdf/PyPDF2 or pdftotext. " + " | ".join(errors))


def read_text(path: Path) -> list[tuple[int, str]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    chunks = re.split(r"\f+|\n\s*第\s*\d+\s*页\s*\n", text)
    if len(chunks) <= 1:
        return [(1, text)]
    return [(index, chunk) for index, chunk in enumerate(chunks, start=1)]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def score_page(text: str, scale_terms: Iterable[str]) -> int:
    hay = text.lower()
    score = 0
    for keyword in KEYWORDS:
        if keyword.lower() in hay:
            score += 2
    for term in scale_terms:
        term = term.strip().lower()
        if term and term in hay:
            score += 4
    if re.search(r"^\s*(\d+|[A-Z])[\.\、]\s*\S+", text, re.M):
        score += 2
    if re.search(r"(非常不同意|非常同意|strongly disagree|strongly agree|Likert|李克特)", text, re.I):
        score += 2
    return score


def make_scale_terms(scale: str) -> list[str]:
    terms = [scale]
    terms.extend(re.findall(r"[（(]([^）)]+)[）)]", scale))
    terms.append(re.sub(r"[（(][^）)]+[）)]", " ", scale))
    terms.extend(re.findall(r"\b[A-Z]{2,}\b", scale))
    return sorted({normalize(term) for term in terms if normalize(term)}, key=len, reverse=True)


def window(pages: list[tuple[int, str]], idx: int, radius: int) -> str:
    start = max(0, idx - radius)
    end = min(len(pages), idx + radius + 1)
    parts = []
    for page_no, text in pages[start:end]:
        parts.append(f"\n--- page {page_no} ---\n{text}")
    return "\n".join(parts)


def locate(path: Path, scale: str = "", max_results: int = 8, radius: int = 0) -> list[dict[str, object]]:
    suffix = path.suffix.lower()
    pages = read_pdf(path) if suffix == ".pdf" else read_text(path)
    scale_terms = make_scale_terms(scale) if scale else []

    ranked = []
    for idx, (page_no, text) in enumerate(pages):
        page_score = score_page(text, scale_terms)
        if page_score <= 0:
            continue
        snippet_text = window(pages, idx, radius) if radius else text
        ranked.append(
            {
                "page": page_no,
                "score": page_score,
                "snippet": normalize(snippet_text)[:2400],
            }
        )

    ranked.sort(key=lambda item: (-int(item["score"]), int(item["page"])))
    return ranked[:max_results]


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract likely scale appendix sections from PDF/text.")
    parser.add_argument("path", help="PDF, TXT, or Markdown file.")
    parser.add_argument("--scale", default="", help="Target scale name for scoring.")
    parser.add_argument("--max-results", type=int, default=8)
    parser.add_argument("--radius", type=int, default=0, help="Include neighboring pages around hits.")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    args = parser.parse_args()

    path = Path(args.path).expanduser()
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(2)

    results = locate(path, args.scale, args.max_results, args.radius)
    if args.format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    if not results:
        print("No likely appendix/questionnaire sections found.")
        return

    for result in results:
        print(f"## Page {result['page']} | score {result['score']}\n")
        print(result["snippet"])
        print()


if __name__ == "__main__":
    main()
