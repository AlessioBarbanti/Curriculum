# Curriculum Vitae — Alessio Barbanti

My CV, written in LaTeX: one page, readable by applicant tracking systems (ATS), built and checked with a single command.

**[Download the latest PDF](https://github.com/AlessioBarbanti/Curriculum/releases/latest/download/Alessio_Barbanti_CV.pdf)**

<p align="center"><img src="docs/preview.png" alt="Preview of the CV" width="720"></p>

## What's inside

- **ATS-friendly PDF.** The text layer matches what is printed: ligatures are disabled (`fi` stays two letters), icons are hidden from text extraction, and the file is PDF/A-1b.
- **Checked build.** `scripts/build.py` fails if the CV spills onto a second page or if any text crosses the margins or overlaps other text, and shows which text.
- **Review agents.** Two [Claude Code](https://claude.com/claude-code) subagents review the CV: one for content, one for style.

## Structure

```
src/cv.tex             header, section order, footer
src/sections/          one file per section: experience, education, projects
src/cv.cls             layout and macros: \cvexperience, \cveducation, \cvproject, \cvtag
scripts/build.py       build, checks, preview and release
scripts/test_build.py  tests for the log checks in build.py
docs/preview.png       the preview above, refreshed by scripts/build.py
.claude/agents/        review agents
```

## Build

Needs Python 3 (standard library only), pdfLaTeX from TeX Live and `pdftoppm`. On Ubuntu, also under WSL on Windows:

```bash
sudo apt install --no-install-recommends texlive-latex-extra texlive-fonts-recommended texlive-fonts-extra poppler-utils
```

Then:

```bash
scripts/build.py          # from Windows: wsl scripts/build.py
```

```
Pages: 1
Past the margins: none
PDF: build/cv.pdf
```

The exit code is `0` when everything is fine. Otherwise the script prints the LaTeX error with file and line, the page count, or the overflowing text and by how much it overflows.

After changing `build.py`, run its tests with `python3 scripts/test_build.py`.

## Publishing a new version

Commit and push the changes, then:

```bash
scripts/build.py --release
```

This creates a GitHub release named after today's date with `Alessio_Barbanti_CV.pdf` attached. The download link above always points to the latest release. It needs the [GitHub CLI](https://cli.github.com/); under WSL the Windows `gh.exe` works as well.

## Review agents

In Claude Code, from this folder:

- `cv-revisore` reviews the content: impact, relevance, consistency, missing sections.
- `cv-stile` reviews the writing: grammar, typos, consistent formatting, plain wording.

Both only read the files and propose changes as ready-to-paste LaTeX. Their prompts are in Italian, like the CV.

## Credits

The layout started from [techResume](https://github.com/alexcalabrese/techResume) by Alex Calabrese, a customized version of [AltaCV](https://github.com/liantze/AltaCV) by LianTze Lim.

## License

- `src/cv.cls`: [LPPL 1.3c](https://www.latex-project.org/lppl/lppl-1-3c/) or later, as a derivative of AltaCV.
- `scripts/` and `.claude/agents/`: MIT.
- The CV itself (`src/cv.tex`, `src/sections/`, the preview and the released PDFs): © Alessio Barbanti, all rights reserved.

Details in [LICENSE](LICENSE).
