"""Validate the controlled category vocabulary against the filesystem."""

import json
import os
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
CATEGORIES_FILE = ROOT / "categories.json"

EXCLUDED_DIRS = {".planning", ".git", ".github", "scripts", "tests"}


def load_categories():
    with open(CATEGORIES_FILE) as f:
        return json.load(f)


def find_rq_directories():
    """Return set of relative directory paths that contain .rq files."""
    dirs = set()
    for rq_file in ROOT.rglob("*.rq"):
        rel = rq_file.parent.relative_to(ROOT)
        # Skip excluded top-level directories
        parts = rel.parts
        if parts and parts[0] in EXCLUDED_DIRS:
            continue
        # Normalize to string with trailing slash (matching categories.json format)
        dirs.add(str(rel) + "/")
    return dirs


def all_mapped_dirs(data):
    """Return set of all directories listed across all categories."""
    result = set()
    for folders in data["categories"].values():
        result.update(folders)
    return result


def category_for_dir(data, directory):
    """Return the category name that contains the given directory."""
    for cat_name, folders in data["categories"].items():
        if directory in folders:
            return cat_name
    return None


class TestCategoriesJSON:
    def test_valid_json_and_structure(self):
        """categories.json loads without error and has the expected structure."""
        data = load_categories()
        assert "categories" in data
        assert isinstance(data["categories"], dict)
        for name, folders in data["categories"].items():
            assert isinstance(name, str)
            assert isinstance(folders, list)
            for f in folders:
                assert isinstance(f, str)
                assert f.endswith("/"), f"Folder path must end with /: {f}"

    def test_exactly_11_categories(self):
        """The vocabulary contains exactly 11 category names."""
        data = load_categories()
        assert len(data["categories"]) == 11, (
            f"Expected 11 categories, got {len(data['categories'])}: "
            f"{list(data['categories'].keys())}"
        )

    def test_all_directories_covered(self):
        """Every directory containing .rq files maps to a category."""
        data = load_categories()
        mapped = all_mapped_dirs(data)
        fs_dirs = find_rq_directories()
        unmapped = fs_dirs - mapped
        assert not unmapped, (
            f"Directories with .rq files not in any category: {sorted(unmapped)}"
        )

    def test_no_orphan_directories(self):
        """No query-containing directory is missing from the mapping."""
        data = load_categories()
        mapped = all_mapped_dirs(data)
        fs_dirs = find_rq_directories()
        # Same check as above but phrased for clarity
        for d in sorted(fs_dirs):
            assert d in mapped, f"Directory '{d}' contains .rq files but is not mapped"

    def test_datasources_maps_to_data_sources(self):
        """The datasources/ subfolder maps to 'Data Sources', not 'Metadata'."""
        data = load_categories()
        cat = category_for_dir(data, "A. Metadata/datasources/")
        assert cat == "Data Sources", (
            f"Expected 'Data Sources' but got '{cat}' for A. Metadata/datasources/"
        )
