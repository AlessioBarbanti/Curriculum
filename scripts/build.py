#!/usr/bin/env python3
"""Build the CV into build/cv.pdf and check it: exactly one page, nothing past the margins.

When the checks pass, refresh docs/preview.png; with --release, also publish the PDF as a GitHub release.
Usage: scripts/build.py [--release]   (from Windows: wsl scripts/build.py)   exit code 0 = all good
"""
import argparse
import datetime
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # the repository, one level above scripts/
LOG = ROOT / "build" / "cv.log"
PDF = "build/cv.pdf"  # paths relative to ROOT


def utf8(line):
    """The log is read as latin1; lines quoting the source (UTF-8) are re-decoded."""
    return line.encode("latin-1").decode("utf-8", "replace")


def errors(lines):
    """LaTeX errors with file and line, plus the two lines of context TeX prints after them.
    TeX gives paths relative to src/, where it runs: they are shown relative to the repository."""
    found = []
    for i, line in enumerate(lines):
        if re.match(r"\S+\.(tex|cls):\d+: ", line):
            found += ["src/" + utf8(line).removeprefix("./")] + [utf8(l) for l in lines[i + 1:i + 3]]
    return found


def page_count(log):
    match = re.search(r"Output written on .*?\((\d+) pages?", log)
    return int(match.group(1)) if match else 0


def overfull_boxes(lines):
    """Overfull = text past the margins or overlapping. The next log line shows the text involved,
    T1-encoded, which matches latin1 for accented letters."""
    found = []
    for i, line in enumerate(lines):
        match = re.match(r"Overfull \\[hv]box \((\S+) too \w+\) (.*)", line)
        if match:
            text = lines[i + 1] if i + 1 < len(lines) else ""
            text = " ".join(re.sub(r"\\\S+/\S+ |\[\]", "", text).split())
            found.append(f"+{match.group(1)} {match.group(2)}: {text}")
    return found


def release():
    gh = shutil.which("gh") or shutil.which("gh.exe")  # in WSL the Windows gh.exe works too
    if not gh:
        sys.exit("gh not found: install the GitHub CLI")
    tag = datetime.date.today().isoformat()
    name = re.search(r"\\name\{(.+?)\}", (ROOT / "src" / "cv.tex").read_text(encoding="utf-8")).group(1)
    asset = f"build/{name.replace(' ', '_')}_CV.pdf"  # the file name recruiters download
    shutil.copy(ROOT / PDF, ROOT / asset)
    create = [gh, "release", "create", tag, asset, "--title", f"CV {tag}", "--notes", f"CV updated on {tag}."]
    if subprocess.run(create, cwd=ROOT).returncode != 0:  # today's release exists: replace its PDF
        subprocess.run([gh, "release", "upload", tag, asset, "--clobber"], cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--release", action="store_true", help="publish the PDF as a GitHub release")
    args = parser.parse_args()

    (ROOT / "build").mkdir(exist_ok=True)
    pdflatex = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error",
                "-output-directory=../build", "cv.tex"]
    try:
        built = subprocess.run(pdflatex, cwd=ROOT / "src", stdout=subprocess.DEVNULL,
                               env={**os.environ, "max_print_line": "1000"}).returncode == 0
    except FileNotFoundError:
        sys.exit("pdflatex not found: install TeX Live (see README)")

    log = LOG.read_bytes().decode("latin-1")
    lines = log.splitlines()
    if not built:
        print("Build failed:", *errors(lines), sep="\n")
        return 1

    pages = page_count(log)
    print(f"Pages: {pages}" + ("" if pages == 1 else " (must fit on 1)"))
    boxes = overfull_boxes(lines)
    print(f"Past the margins: {len(boxes) or 'none'}", *[f"  {b}" for b in boxes], sep="\n")
    print(f"PDF: {PDF}")
    if pages != 1 or boxes:
        return 1

    (ROOT / "docs").mkdir(exist_ok=True)
    subprocess.run(["pdftoppm", "-png", "-r", "110", "-singlefile", PDF, "docs/preview"],
                   cwd=ROOT, check=True)
    if args.release:
        release()
    return 0


if __name__ == "__main__":
    sys.exit(main())
