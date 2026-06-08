#!/usr/bin/env python3
"""Render PDF pages to PNG previews for visual inspection and optional OCR."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def import_pdf_writer():
    for module_name in ("pypdf", "PyPDF2"):
        try:
            module = __import__(module_name)
            return module.PdfReader, module.PdfWriter
        except Exception:
            continue
    raise RuntimeError("Install pypdf/PyPDF2 or pass a Python environment where one is available.")


def import_pdfium():
    try:
        import pypdfium2 as pdfium

        return pdfium
    except Exception:
        return None


def ensure_pdfium(deps_dir: Path | None, setup: bool):
    pdfium = import_pdfium()
    if pdfium:
        return pdfium, "pypdfium2 found"
    if not setup:
        return None, "pypdfium2 not found"
    if deps_dir is None:
        return None, "--setup requires --deps-dir"
    deps_dir.mkdir(parents=True, exist_ok=True)
    proc = run([sys.executable, "-m", "pip", "install", "--target", str(deps_dir), "pypdfium2"])
    if proc.returncode != 0:
        return None, proc.stderr.strip() or proc.stdout.strip()
    sys.path.insert(0, str(deps_dir))
    return import_pdfium(), "pypdfium2 installed"


def parse_pages(spec: str, total: int) -> list[int]:
    if not spec:
        return list(range(1, total + 1))
    pages: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            start = int(start_text)
            end = int(end_text)
            pages.extend(range(start, end + 1))
        else:
            pages.append(int(part))
    return sorted({page for page in pages if 1 <= page <= total})


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    # Keep QuickLook away from Python-specific environment variables; qlmanage
    # can fail under inherited sandbox metadata even when it still renders.
    env = {key: value for key, value in os.environ.items() if not key.startswith("PYTHON")}
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=env, text=True, capture_output=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render PDF pages to PNG previews.")
    parser.add_argument("pdf", help="PDF file")
    parser.add_argument("--pages", default="", help="Page spec, e.g. 1,3-5. Defaults to all pages.")
    parser.add_argument("--output-dir", default="", help="Output directory. Defaults to <pdf stem>-pages beside the PDF.")
    parser.add_argument("--deps-dir", default="", help="Optional Python dependency directory containing pypdfium2/PyPDF2.")
    parser.add_argument("--setup", action="store_true", help="Install pypdfium2 into --deps-dir if missing.")
    parser.add_argument("--size", type=int, default=1800, help="QuickLook thumbnail size")
    parser.add_argument("--scale", type=float, default=2.5, help="pypdfium2 render scale")
    parser.add_argument("--ocr", action="store_true", help="Run tesseract OCR if available")
    parser.add_argument("--lang", default="chi_sim+eng", help="Tesseract language spec")
    parser.add_argument("--format", choices=["json", "text"], default="text")
    args = parser.parse_args()

    pdf_path = Path(args.pdf).expanduser()
    out_dir = Path(args.output_dir).expanduser() if args.output_dir else pdf_path.with_suffix("").with_name(pdf_path.stem + "-pages")
    report: dict[str, object] = {"pdf": str(pdf_path), "output_dir": str(out_dir), "pages": []}

    if args.deps_dir:
        deps_dir = Path(args.deps_dir).expanduser()
        sys.path.insert(0, str(deps_dir))
    else:
        deps_dir = None

    if not pdf_path.exists():
        report["status"] = "error"
        report["error"] = f"PDF not found: {pdf_path}"
    else:
        try:
            out_dir.mkdir(parents=True, exist_ok=True)

            tesseract = shutil.which("tesseract") if args.ocr else None
            pdfium, pdfium_status = ensure_pdfium(deps_dir, args.setup)
            report["pdfium_status"] = pdfium_status

            if pdfium:
                doc = pdfium.PdfDocument(str(pdf_path))
                selected_pages = parse_pages(args.pages, len(doc))
                report["backend"] = "pypdfium2"
                for page_no in selected_pages:
                    image_path = out_dir / f"{pdf_path.stem}_page_{page_no}.png"
                    page = doc[page_no - 1]
                    bitmap = page.render(scale=args.scale)
                    bitmap.to_pil().save(image_path)
                    page_report = {
                        "page": page_no,
                        "pdf": "",
                        "image": str(image_path),
                        "render_returncode": 0,
                        "render_stderr": "",
                        "image_exists": image_path.exists(),
                    }

                    if tesseract and image_path.exists():
                        ocr_base = out_dir / f"{pdf_path.stem}_page_{page_no}_ocr"
                        ocr_proc = run([tesseract, str(image_path), str(ocr_base), "-l", args.lang])
                        text_path = ocr_base.with_suffix(".txt")
                        page_report.update(
                            {
                                "ocr_returncode": ocr_proc.returncode,
                                "ocr_text": str(text_path),
                                "ocr_text_exists": text_path.exists(),
                                "ocr_stderr": ocr_proc.stderr.strip(),
                            }
                        )

                    report["pages"].append(page_report)
            else:
                if not shutil.which("qlmanage"):
                    raise RuntimeError("pypdfium2 and qlmanage are both unavailable; cannot render PDF previews.")
                PdfReader, PdfWriter = import_pdf_writer()
                reader = PdfReader(str(pdf_path))
                selected_pages = parse_pages(args.pages, len(reader.pages))
                report["backend"] = "qlmanage"
                for page_no in selected_pages:
                    one_page_pdf = out_dir / f"{pdf_path.stem}_page_{page_no}.pdf"
                    writer = PdfWriter()
                    writer.add_page(reader.pages[page_no - 1])
                    with one_page_pdf.open("wb") as handle:
                        writer.write(handle)

                    proc = run(["qlmanage", "-t", "-s", str(args.size), "-o", str(out_dir), str(one_page_pdf)])
                    image_path = out_dir / f"{one_page_pdf.name}.png"
                    page_report = {
                        "page": page_no,
                        "pdf": str(one_page_pdf),
                        "image": str(image_path),
                        "render_returncode": proc.returncode,
                        "render_stderr": proc.stderr.strip(),
                        "image_exists": image_path.exists(),
                    }

                    if tesseract and image_path.exists():
                        ocr_base = out_dir / f"{pdf_path.stem}_page_{page_no}_ocr"
                        ocr_proc = run([tesseract, str(image_path), str(ocr_base), "-l", args.lang])
                        text_path = ocr_base.with_suffix(".txt")
                        page_report.update(
                            {
                                "ocr_returncode": ocr_proc.returncode,
                                "ocr_text": str(text_path),
                                "ocr_text_exists": text_path.exists(),
                                "ocr_stderr": ocr_proc.stderr.strip(),
                            }
                        )

                    report["pages"].append(page_report)

            missing_images = [page for page in report["pages"] if not page.get("image_exists")]
            if missing_images and len(missing_images) == len(report["pages"]):
                report["status"] = "error"
                report["error"] = "No page images were rendered."
            elif missing_images:
                report["status"] = "partial"
                report["error"] = f"{len(missing_images)} page image(s) failed to render."
            else:
                report["status"] = "ok"
            report["ocr_available"] = bool(tesseract)
            report["ocr_requested"] = args.ocr
        except Exception as exc:
            report["status"] = "error"
            report["error"] = str(exc)

    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    if report.get("status") not in {"ok", "partial"}:
        print("PDF rendering failed.", file=sys.stderr)
        print(report.get("error", "Unknown error"), file=sys.stderr)
        sys.exit(1)

    for page in report["pages"]:
        print(f"Page {page['page']}: {page['image']}")
    if args.ocr and not report.get("ocr_available"):
        print("OCR requested but tesseract is not installed; rendered page images only.")


if __name__ == "__main__":
    main()
