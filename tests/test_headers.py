"""Validate that all .rq files have required header fields (title, category)."""

import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
CATEGORIES_FILE = ROOT / "categories.json"

EXCLUDED_DIRS = {".planning", ".git", ".github", "scripts", "tests"}


def find_rq_files():
    """Return sorted list of .rq file paths, excluding tests/ and other non-query dirs."""
    results = []
    for rq_file in sorted(ROOT.rglob("*.rq")):
        rel = rq_file.relative_to(ROOT)
        parts = rel.parts
        if parts and parts[0] in EXCLUDED_DIRS:
            continue
        results.append(rq_file)
    return results


def parse_header(filepath):
    """Extract header block from an .rq file.

    The header block is the consecutive sequence of lines starting with '#'
    at the top of the file, ending at the first blank line or non-comment line.
    Returns a list of header line strings (with the leading '# ' stripped where applicable).
    """
    lines = []
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            stripped = line.rstrip("\n\r")
            if stripped.startswith("#"):
                lines.append(stripped)
            else:
                break
    return lines


def load_valid_categories():
    """Return the set of valid category names from categories.json."""
    with open(CATEGORIES_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return set(data["categories"].keys())


# Collect files once at module level for parametrization
_RQ_FILES = find_rq_files()
_RQ_PARAMS = [
    pytest.param(f, id=str(f.relative_to(ROOT))) for f in _RQ_FILES
]


@pytest.mark.parametrize("rq_file", _RQ_PARAMS)
def test_all_rq_have_title(rq_file):
    """Every .rq file must have a '# title: ...' line in its header block."""
    header = parse_header(rq_file)
    title_pattern = re.compile(r"^# title: .+")
    titles = [line for line in header if title_pattern.match(line)]
    assert titles, (
        f"Missing '# title:' header in {rq_file.relative_to(ROOT)}"
    )


@pytest.mark.parametrize("rq_file", _RQ_PARAMS)
def test_all_rq_have_valid_category(rq_file):
    """Every .rq file must have a '# category: VALUE' line with a valid category."""
    header = parse_header(rq_file)
    valid = load_valid_categories()
    cat_pattern = re.compile(r"^# category: (.+)")
    categories = []
    for line in header:
        m = cat_pattern.match(line)
        if m:
            categories.append(m.group(1).strip())
    assert categories, (
        f"Missing '# category:' header in {rq_file.relative_to(ROOT)}"
    )
    for cat in categories:
        assert cat in valid, (
            f"Invalid category '{cat}' in {rq_file.relative_to(ROOT)}. "
            f"Valid categories: {sorted(valid)}"
        )


def test_titles_are_unique():
    """All title values across .rq files must be unique (no duplicates)."""
    title_pattern = re.compile(r"^# title: (.+)")
    seen = {}
    for rq_file in _RQ_FILES:
        header = parse_header(rq_file)
        for line in header:
            m = title_pattern.match(line)
            if m:
                title = m.group(1).strip()
                rel = str(rq_file.relative_to(ROOT))
                if title in seen:
                    seen[title].append(rel)
                else:
                    seen[title] = [rel]
    duplicates = {t: files for t, files in seen.items() if len(files) > 1}
    assert not duplicates, (
        f"Duplicate titles found: {duplicates}"
    )


def test_header_field_order():
    """When both title and category are present, title must appear before category."""
    title_pattern = re.compile(r"^# title: ")
    cat_pattern = re.compile(r"^# category: ")
    for rq_file in _RQ_FILES:
        header = parse_header(rq_file)
        title_idx = None
        cat_idx = None
        for i, line in enumerate(header):
            if title_pattern.match(line) and title_idx is None:
                title_idx = i
            if cat_pattern.match(line) and cat_idx is None:
                cat_idx = i
        if title_idx is not None and cat_idx is not None:
            assert title_idx < cat_idx, (
                f"In {rq_file.relative_to(ROOT)}: title (line {title_idx}) "
                f"must appear before category (line {cat_idx})"
            )


def test_blank_line_separator():
    """Files with structured header fields must have a blank line before the query body."""
    field_pattern = re.compile(r"^# (title|category|description|keywords|param): ")
    for rq_file in _RQ_FILES:
        header = parse_header(rq_file)
        # Only check files that have at least one structured header field
        has_field = any(field_pattern.match(line) for line in header)
        if not has_field:
            continue
        with open(rq_file, encoding="utf-8") as f:
            content = f.read()
        lines = content.split("\n")
        # Find end of header block (consecutive # lines at top)
        header_end = 0
        for i, line in enumerate(lines):
            if line.startswith("#"):
                header_end = i + 1
            else:
                break
        # The line immediately after the header block should be blank
        if header_end < len(lines):
            assert lines[header_end].strip() == "", (
                f"In {rq_file.relative_to(ROOT)}: expected blank line after "
                f"header block at line {header_end + 1}, got: '{lines[header_end]}'"
            )
