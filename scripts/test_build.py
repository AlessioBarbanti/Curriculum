"""Checks for the log parsing in build.py, on lines taken from real pdflatex logs. Run: python3 scripts/test_build.py"""
from build import errors, overfull_boxes, page_count


def test_page_count():
    assert page_count("Output written on /mnt/c/cv/build/cv.pdf (1 page, 147195 bytes).") == 1
    assert page_count("Output written on build/cv.pdf (4 pages, 210345 bytes).") == 4
    assert page_count("No pages of output.") == 0


def test_overfull_boxes():
    # The log is decoded as latin1, so "\xe0" is the T1 "à" as TeX writes it.
    lines = [
        "Overfull \\hbox (73.13916pt too wide) detected at line 4",
        "\\T1/lato-TLF/b/n/9 Laurea Magistrale \\T1/lato-TLF/m/n/9 Universit\xe0 di Bologna []",
        "Underfull \\hbox (badness 10000) in paragraph at lines 19--19",
        " []",
    ]
    assert overfull_boxes(lines) == ["+73.13916pt detected at line 4: Laurea Magistrale Università di Bologna"]


def test_errors():
    # Paths are relative to src/, where TeX runs. The source line TeX quotes is UTF-8:
    # "\xc3\xa0" is "à" read as latin1.
    lines = [
        "(./sections/education.tex",
        "./sections/education.tex:4: Undefined control sequence.",
        "l.4 \\cveducazione{Universit\xc3\xa0}",
        "",
        "Here is how much of TeX's memory you used:",
    ]
    assert errors(lines) == [
        "src/sections/education.tex:4: Undefined control sequence.",
        "l.4 \\cveducazione{Università}",
        "",
    ]
    assert errors(["cv.tex:7: Missing } inserted.", "l.7", ""])[0] == "src/cv.tex:7: Missing } inserted."


if __name__ == "__main__":
    test_page_count()
    test_overfull_boxes()
    test_errors()
    print("ok")
