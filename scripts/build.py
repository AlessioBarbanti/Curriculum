#!/usr/bin/env python3
"""Build the CV in Italian and English and check both: exactly one page, nothing past the margins.

When the checks pass, refresh the previews in docs/; with --release, also publish both PDFs as a GitHub release.
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

# One source (src/cv.tex), one version per language. Paths are relative to ROOT.
VERSIONS = [
    # language, LaTeX job (build/<job>.pdf), class option, preview, release file suffix
    ("it", "cv", None, "docs/preview", "_CV"),
    ("en", "cv-en", "english", "docs/preview-en", "_CV_EN"),
]


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
    today = tag = datetime.date.today().isoformat()
    n = 1
    while subprocess.run([gh, "release", "view", tag], cwd=ROOT, capture_output=True).returncode == 0:
        n += 1  # a release already exists today: a new tag, so it points at the current commit
        tag = f"{today}.{n}"
    name = re.search(r"\\name\{(.+?)\}", (ROOT / "src" / "cv.tex").read_text(encoding="utf-8")).group(1)
    assets = []
    for _, job, _, _, suffix in VERSIONS:
        asset = f"build/{name.replace(' ', '_')}{suffix}.pdf"  # the file name recruiters download
        shutil.copy(ROOT / f"build/{job}.pdf", ROOT / asset)
        assets.append(asset)
    subprocess.run([gh, "release", "create", tag, *assets, "--title", f"CV {tag}", "--notes", f"CV updated on {today}."],
                   cwd=ROOT, check=True)


def check(lang, job, option):
    """Build one language version and print its checks; True when it is fine."""
    tex = rf"\PassOptionsToClass{{{option}}}{{cv}}\input{{cv.tex}}" if option else "cv.tex"
    pdflatex = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error",
                "-output-directory=../build", f"-jobname={job}", tex]
    built = subprocess.run(pdflatex, cwd=ROOT / "src", stdout=subprocess.DEVNULL,
                           env={**os.environ, "max_print_line": "1000"}).returncode == 0

    log = (ROOT / "build" / f"{job}.log").read_bytes().decode("latin-1")
    lines = log.splitlines()
    if not built:
        print(f"[{lang}] Build failed:", *errors(lines), sep="\n")
        return False

    pages = page_count(log)
    print(f"[{lang}] Pages: {pages}" + ("" if pages == 1 else " (must fit on 1)"))
    boxes = overfull_boxes(lines)
    print(f"[{lang}] Past the margins: {len(boxes) or 'none'}", *[f"  {b}" for b in boxes], sep="\n")
    print(f"[{lang}] PDF: build/{job}.pdf")
    return pages == 1 and not boxes


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--release", action="store_true", help="publish both PDFs as a GitHub release")
    args = parser.parse_args()

    (ROOT / "build").mkdir(exist_ok=True)
    try:
        results = [check(lang, job, option) for lang, job, option, _, _ in VERSIONS]  # all, even after a failure
    except FileNotFoundError:
        sys.exit("pdflatex not found: install TeX Live (see README)")
    if not all(results):
        return 1

    (ROOT / "docs").mkdir(exist_ok=True)
    for _, job, _, preview, _ in VERSIONS:
        subprocess.run(["pdftoppm", "-png", "-r", "110", "-singlefile", f"build/{job}.pdf", preview],
                       cwd=ROOT, check=True)
    if args.release:
        release()
    return 0


if __name__ == "__main__":
    sys.exit(main())
