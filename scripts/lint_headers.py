"""CI lint script: validates required headers on all .rq query files."""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXCLUDED_DIRS = {".planning", ".git", ".github", "scripts", "tests"}

REQUIRED_FIELDS = ["title", "category", "description"]
FIELD_PATTERNS = {
    field: re.compile(rf"^# {field}: .+") for field in REQUIRED_FIELDS
}


def find_rq_files():
    """Return sorted list of .rq file paths, excluding non-query directories."""
    results = []
    for rq_file in sorted(ROOT.rglob("*.rq")):
        rel = rq_file.relative_to(ROOT)
        parts = rel.parts
        if parts and parts[0] in EXCLUDED_DIRS:
            continue
        results.append(rq_file)
    return results


def parse_header(filepath):
    """Extract consecutive comment lines from the top of an .rq file."""
    lines = []
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            stripped = line.rstrip("\n\r")
            if stripped.startswith("#"):
                lines.append(stripped)
            else:
                break
    return lines


def lint_file(filepath):
    """Check a single .rq file for required header fields.

    Returns a list of error strings (empty if file passes).
    """
    header = parse_header(filepath)
    rel_path = filepath.relative_to(ROOT)
    errors = []
    for field in REQUIRED_FIELDS:
        pattern = FIELD_PATTERNS[field]
        if not any(pattern.match(line) for line in header):
            errors.append(f"{rel_path}: missing '# {field}:' header")
    return errors


def main():
    """Lint all .rq files and report results."""
    rq_files = find_rq_files()
    all_errors = []
    for rq_file in rq_files:
        all_errors.extend(lint_file(rq_file))

    if all_errors:
        for error in all_errors:
            print(f"ERROR: {error}")
        sys.exit(1)
    else:
        print(f"OK: {len(rq_files)} files passed lint check")
        sys.exit(0)


if __name__ == "__main__":
    main()
