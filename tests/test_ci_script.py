"""Tests for the CI TTL-to-SPARQL extraction script with header preservation."""

import os
import shutil
import sys

import pytest

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")

# Add project root to path so we can import the script module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.transformDotTtlToDotSparql import extract_header, process_ttl_file


def _copy_fixture(src_name, dst_dir, dst_name=None):
    """Copy a fixture file into a temp directory."""
    dst_name = dst_name or src_name
    src = os.path.join(FIXTURES, src_name)
    dst = os.path.join(dst_dir, dst_name)
    shutil.copy2(src, dst)
    return dst


class TestHeaderPreservation:
    """Test 1: Header block is preserved when .rq is regenerated from .ttl."""

    def test_preserves_existing_headers(self, tmp_path):
        ttl = _copy_fixture("sample.ttl", tmp_path)
        rq = _copy_fixture("sample_with_header.rq", tmp_path, "sample.rq")

        process_ttl_file(str(ttl))

        content = open(rq, encoding="utf-8").read()
        assert content.startswith("# title: Sample Query\n")
        assert "# category: Metadata" in content
        assert "# description: A test query." in content
        # SPARQL should be the new one from the TTL, not the old one
        assert "SELECT ?x WHERE { ?x a ?type }" in content
        assert "SELECT ?old" not in content


class TestNoHeader:
    """Test 2: .rq with no headers stays headerless after regeneration."""

    def test_no_phantom_header_injected(self, tmp_path):
        ttl = _copy_fixture("sample.ttl", tmp_path)
        _copy_fixture("sample_no_header.rq", tmp_path, "sample.rq")

        process_ttl_file(str(ttl))

        content = open(os.path.join(tmp_path, "sample.rq"), encoding="utf-8").read()
        assert not content.startswith("#")
        assert "SELECT ?x WHERE { ?x a ?type }" in content


class TestNoExistingRq:
    """Test 3: When no .rq exists, one is created with just SPARQL."""

    def test_creates_rq_from_scratch(self, tmp_path):
        ttl = _copy_fixture("sample.ttl", tmp_path)
        rq_path = os.path.join(tmp_path, "sample.rq")
        assert not os.path.exists(rq_path)

        process_ttl_file(str(ttl))

        assert os.path.exists(rq_path)
        content = open(rq_path, encoding="utf-8").read()
        assert "SELECT ?x WHERE { ?x a ?type }" in content
        assert not content.startswith("#")


class TestSparqlCorrectness:
    """Test 4: Extracted SPARQL matches expected output (regression test)."""

    def test_exact_sparql_extraction(self, tmp_path):
        ttl = _copy_fixture("sample.ttl", tmp_path)

        process_ttl_file(str(ttl))

        content = open(os.path.join(tmp_path, "sample.rq"), encoding="utf-8").read()
        assert content.strip() == "SELECT ?x WHERE { ?x a ?type }"


class TestBlankLineSeparator:
    """Test 5: Exactly one blank line separates header block from SPARQL."""

    def test_single_blank_line_between_header_and_sparql(self, tmp_path):
        ttl = _copy_fixture("sample.ttl", tmp_path)
        _copy_fixture("sample_with_header.rq", tmp_path, "sample.rq")

        process_ttl_file(str(ttl))

        content = open(os.path.join(tmp_path, "sample.rq"), encoding="utf-8").read()
        # Split on the last header line
        lines = content.split("\n")
        # Find the transition from header to SPARQL
        header_end = -1
        for idx, line in enumerate(lines):
            if line.startswith("#"):
                header_end = idx
        # Line after last header should be blank, then SPARQL
        assert lines[header_end + 1] == "", "Expected blank line after header"
        assert lines[header_end + 2].startswith("SELECT"), "Expected SPARQL after blank line"


class TestErrorGuard:
    """Test 6: Empty TTL (no SPARQL query) does not overwrite existing .rq."""

    def test_does_not_overwrite_on_empty_sparql(self, tmp_path):
        ttl = _copy_fixture("sample_empty.ttl", tmp_path)
        rq_path = os.path.join(tmp_path, "sample_empty.rq")
        # Create a pre-existing .rq with content
        with open(rq_path, "w") as f:
            f.write("SELECT ?existing WHERE { ?existing a ?type }\n")

        process_ttl_file(str(ttl))

        content = open(rq_path, encoding="utf-8").read()
        assert "SELECT ?existing" in content, "Existing .rq should not be overwritten"
