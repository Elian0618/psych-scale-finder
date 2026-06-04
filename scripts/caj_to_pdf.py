#!/usr/bin/env python3
"""Convert local CNKI CAJ files to PDF through the caj2pdf toolchain.

This wrapper keeps the workflow deterministic:
- find or clone caj2pdf;
- ensure PyPDF2 is importable from a local dependency directory;
- compile libjbigdec.so when source files are available;
- run caj2pdf show/convert and report structured status.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


REPO_URL = "https://github.com/caj2pdf/caj2pdf.git"


def run(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=env, text=True, capture_output=True)


def default_tool_dir() -> Path:
    return Path.cwd() / ".psych-scale-finder-cache" / "caj2pdf"


def ensure_repo(tool_dir: Path, setup: bool) -> tuple[bool, str]:
    if (tool_dir / "caj2pdf").exists():
        return True, "caj2pdf repo found"
    if not setup:
        return False, f"caj2pdf not found at {tool_dir}; rerun with --setup or pass --caj2pdf-dir"
    tool_dir.parent.mkdir(parents=True, exist_ok=True)
    proc = run(["git", "clone", REPO_URL, str(tool_dir)])
    if proc.returncode != 0:
        return False, proc.stderr.strip() or proc.stdout.strip()
    return True, "caj2pdf repo cloned"


def ensure_pypdf2(deps_dir: Path, setup: bool) -> tuple[bool, str]:
    sys.path.insert(0, str(deps_dir))
    try:
        import PyPDF2  # noqa: F401

        return True, "PyPDF2 found"
    except Exception:
        pass

    if not setup:
        return False, f"PyPDF2 not importable; rerun with --setup or install it into {deps_dir}"

    deps_dir.mkdir(parents=True, exist_ok=True)
    proc = run([sys.executable, "-m", "pip", "install", "--target", str(deps_dir), "PyPDF2"])
    if proc.returncode != 0:
        return False, proc.stderr.strip() or proc.stdout.strip()

    sys.path.insert(0, str(deps_dir))
    try:
        import PyPDF2  # noqa: F401

        return True, "PyPDF2 installed"
    except Exception as exc:
        return False, f"PyPDF2 install completed but import failed: {exc}"


def ensure_jbigdec(tool_dir: Path) -> tuple[bool, str]:
    lib_path = tool_dir / "libjbigdec.so"
    if lib_path.exists():
        return True, "libjbigdec.so found"

    cc = shutil.which("cc") or shutil.which("clang") or shutil.which("gcc")
    if not cc:
        return False, "No C compiler found for libjbigdec.so"

    sources = [tool_dir / "lib" / "jbigdec.cc", tool_dir / "lib" / "JBigDecode.cc"]
    missing = [str(path) for path in sources if not path.exists()]
    if missing:
        return False, "Missing libjbigdec sources: " + ", ".join(missing)

    proc = run([cc, "-Wall", "-fPIC", "--shared", "-o", str(lib_path), *(str(path) for path in sources)])
    if proc.returncode != 0:
        return False, proc.stderr.strip() or proc.stdout.strip()
    return True, "libjbigdec.so compiled"


def caj2pdf_env(deps_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(deps_dir) if not existing else f"{deps_dir}{os.pathsep}{existing}"
    return env


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a local CNKI CAJ file to PDF.")
    parser.add_argument("input", help="Local .caj file")
    parser.add_argument("--output", "-o", required=True, help="Output PDF path")
    parser.add_argument("--caj2pdf-dir", default="", help="Existing caj2pdf repo directory")
    parser.add_argument("--deps-dir", default="", help="Local Python dependency directory")
    parser.add_argument("--setup", action="store_true", help="Clone caj2pdf and install PyPDF2 if missing")
    parser.add_argument("--format", choices=["json", "text"], default="text")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser()
    output_path = Path(args.output).expanduser()
    tool_dir = Path(args.caj2pdf_dir).expanduser() if args.caj2pdf_dir else default_tool_dir()
    deps_dir = Path(args.deps_dir).expanduser() if args.deps_dir else tool_dir / ".deps"

    report: dict[str, object] = {
        "input": str(input_path),
        "output": str(output_path),
        "caj2pdf_dir": str(tool_dir),
        "deps_dir": str(deps_dir),
        "steps": [],
    }

    if not input_path.exists():
        report["status"] = "error"
        report["error"] = f"Input file not found: {input_path}"
    else:
        for label, ok_msg in [
            ("repo", ensure_repo(tool_dir, args.setup)),
            ("pypdf2", ensure_pypdf2(deps_dir, args.setup)),
            ("jbigdec", ensure_jbigdec(tool_dir)),
        ]:
            ok, message = ok_msg
            report["steps"].append({"step": label, "ok": ok, "message": message})
            if not ok:
                report["status"] = "error"
                report["error"] = message
                break
        else:
            show_proc = run([sys.executable, str(tool_dir / "caj2pdf"), "show", str(input_path)], cwd=tool_dir, env=caj2pdf_env(deps_dir))
            report["show"] = {"returncode": show_proc.returncode, "stdout": show_proc.stdout.strip(), "stderr": show_proc.stderr.strip()}
            if show_proc.returncode != 0:
                report["status"] = "error"
                report["error"] = show_proc.stderr.strip() or show_proc.stdout.strip()
            else:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                conv_proc = run(
                    [sys.executable, str(tool_dir / "caj2pdf"), "convert", str(input_path), "-o", str(output_path)],
                    cwd=tool_dir,
                    env=caj2pdf_env(deps_dir),
                )
                report["convert"] = {
                    "returncode": conv_proc.returncode,
                    "stdout": conv_proc.stdout.strip(),
                    "stderr": conv_proc.stderr.strip(),
                }
                if conv_proc.returncode != 0:
                    report["status"] = "error"
                    report["error"] = conv_proc.stderr.strip() or conv_proc.stdout.strip()
                else:
                    report["status"] = "ok"
                    report["output_exists"] = output_path.exists()
                    report["output_size"] = output_path.stat().st_size if output_path.exists() else 0

    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    if report.get("status") == "ok":
        print(f"Converted CAJ to PDF: {output_path}")
        if report.get("show", {}).get("stdout"):
            print(report["show"]["stdout"])
    else:
        print("CAJ conversion failed.", file=sys.stderr)
        print(report.get("error", "Unknown error"), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
