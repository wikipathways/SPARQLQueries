# Testing Patterns

**Analysis Date:** 2026-03-06

## Test Framework

**Runner:** None

No test framework is configured. There are no test files, no test configuration, and no test dependencies in the repository.

## Test File Organization

**Location:** Not applicable - no tests exist.

**Naming:** Not applicable.

## Current Validation

The only automated validation is the CI pipeline in `.github/workflows/extractRQs.yml`, which:

1. Runs on push to `master` and on `workflow_dispatch`
2. Executes `scripts/transformDotTtlToDotSparql.py` to extract SPARQL from `.ttl` files
3. Commits any resulting `.rq` file changes back to the repo

This provides implicit validation that `.ttl` files are parseable RDF (the `rdflib` parser will fail on invalid Turtle syntax), but does not validate:
- SPARQL query syntax correctness
- Query execution against the endpoint
- Expected result shapes or values
- Standalone `.rq` files (only `.ttl` files are processed)

## Run Commands

```bash
# No test commands exist. The CI extraction can be run locally:
pip install rdflib && python scripts/transformDotTtlToDotSparql.py
```

## What Could Be Tested

**SPARQL Syntax Validation:**
- Parse all `.rq` files to verify they are syntactically valid SPARQL
- Tool: `rdflib` or a dedicated SPARQL parser like `pyparsing` with SPARQL grammar
- Scope: All 90 `.rq` files

**TTL File Validation:**
- Parse all `.ttl` files to verify valid Turtle syntax
- Verify required SHACL properties are present (`rdfs:comment`, `sh:select`, `schema:target`, `schema:keywords`)
- Scope: 4 `.ttl` files currently

**Query Execution Smoke Tests:**
- Execute each query against `https://sparql.wikipathways.org/sparql` and verify non-error response
- Would require network access and a live endpoint
- Risk: endpoint data changes over time, so result assertions would be fragile

**Prefix Consistency:**
- Verify that queries using prefixes without explicit `PREFIX` declarations only use prefixes available at the WikiPathways SPARQL endpoint
- Could be a static analysis check

## Coverage

**Requirements:** None enforced.

**Current state:** 0% - no tests exist.

## Test Types

**Unit Tests:** Not used.

**Integration Tests:** Not used.

**E2E Tests:** Not used.

**Linting/Static Analysis:** Not used. No `.eslintrc`, `.prettierrc`, or equivalent configuration exists for SPARQL or Python files.

## Recommendations for Adding Tests

If tests are added, consider:

1. **SPARQL syntax validation** using Python's `rdflib.plugins.sparql.prepareQuery`:
```python
from rdflib.plugins.sparql import prepareQuery
import glob

for rq_file in glob.glob("**/*.rq", recursive=True):
    with open(rq_file) as f:
        query = f.read()
    try:
        prepareQuery(query)
    except Exception as e:
        print(f"FAIL: {rq_file}: {e}")
```

2. **TTL structure validation** ensuring SHACL properties:
```python
from rdflib import Graph, Namespace

SH = Namespace("http://www.w3.org/ns/shacl#")
SCHEMA = Namespace("https://schema.org/")

for ttl_file in glob.glob("**/*.ttl", recursive=True):
    g = Graph().parse(ttl_file)
    # Check sh:select or sh:ask or sh:construct exists
    assert any(g.triples((None, SH.select, None))) or \
           any(g.triples((None, SH.ask, None))) or \
           any(g.triples((None, SH.construct, None)))
```

3. **File organization tests** verifying naming conventions and directory structure compliance.

---

*Testing analysis: 2026-03-06*
