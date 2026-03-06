# Technology Stack

**Analysis Date:** 2026-03-06

## Languages

**Primary:**
- SPARQL 1.1 - All query files (90 `.rq` files across directories A-J)
- RDF/Turtle - SHACL-wrapped query metadata (4 `.ttl` files)

**Secondary:**
- Python 3.11 - CI extraction script (`scripts/transformDotTtlToDotSparql.py`)
- YAML - GitHub Actions workflow (`.github/workflows/extractRQs.yml`)

## Runtime

**Environment:**
- Python 3.11 (CI only, not required for query authoring)
- No local runtime needed for `.rq` files; queries execute against remote SPARQL endpoints

**Package Manager:**
- pip (CI only, no `requirements.txt` present)
- No lockfile

## Frameworks

**Core:**
- SHACL (Shapes Constraint Language) - Used in `.ttl` files to wrap SPARQL queries as `sh:SPARQLExecutable` / `sh:SPARQLSelectExecutable` instances
- schema.org vocabulary - Used in `.ttl` files for `schema:target` (endpoint) and `schema:keywords` metadata

**Testing:**
- None detected

**Build/Dev:**
- GitHub Actions - CI pipeline for TTL-to-RQ extraction

## Key Dependencies

**Critical:**
- `rdflib` (Python) - Parses `.ttl` files and extracts SPARQL via SPARQL-over-RDF query in `scripts/transformDotTtlToDotSparql.py`

**Infrastructure:**
- `actions/checkout@v4` - GitHub Actions checkout
- `actions/setup-python@v5` - Python setup in CI

## Configuration

**Environment:**
- No environment variables required
- No `.env` files present
- No secrets needed; all SPARQL endpoints are public

**Build:**
- `.github/workflows/extractRQs.yml` - CI workflow triggered on push to `master` or manual `workflow_dispatch`
- No `pyproject.toml`, `setup.py`, `requirements.txt`, or `package.json`

## Platform Requirements

**Development:**
- Any text editor for `.rq` and `.ttl` files
- Optional: Python 3.11 + `rdflib` to run TTL extraction locally (`pip install rdflib && python scripts/transformDotTtlToDotSparql.py`)
- A SPARQL client (e.g., browser at http://sparql.wikipathways.org/) to test queries

**Production:**
- Queries are loaded by the WikiPathways Snorql UI at http://sparql.wikipathways.org/
- Deployment is the git repository itself; the Snorql UI reads `.rq` files

## Dual-Format Query System

**Source of truth:** `.ttl` files (only 4 exist currently)
- `A. Metadata/metadata.ttl`
- `A. Metadata/prefixes.ttl`
- `A. Metadata/linksets.ttl`
- `B. Communities/AOP/allPathways.ttl`

**Generated files:** `.rq` files extracted from `.ttl` by CI pipeline. Do NOT edit `.rq` files that have a corresponding `.ttl`.

**Standalone queries:** The remaining 86+ `.rq` files have no `.ttl` source and are edited directly.

## RDF Vocabularies Used

Queries use these WikiPathways-specific prefixes (typically declared implicitly by the endpoint):
- `wp:` - `http://vocabularies.wikipathways.org/wp#` (pathway types, gene products, metabolites, interactions)
- `dc:` - `http://purl.org/dc/elements/1.1/` (titles, identifiers)
- `dcterms:` - `http://purl.org/dc/terms/` (isPartOf, identifier, license)
- `void:` - VOID dataset descriptions
- `pav:` - Provenance, Authoring and Versioning
- `cur:` - `http://vocabularies.wikipathways.org/wp#Curation:` (community/curation ontology tags)
- `rdfs:` - labels, subclass relationships
- `foaf:` - author names

## License

GPL-3.0 (`LICENSE`)

---

*Stack analysis: 2026-03-06*
