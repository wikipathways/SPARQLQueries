# Architecture

**Analysis Date:** 2026-03-06

## Pattern Overview

**Overall:** Static query library with CI-driven code generation

**Key Characteristics:**
- Repository is a flat collection of SPARQL queries organized by topic, not a runnable application
- Dual-format system: `.ttl` files (source of truth with metadata) generate `.rq` files (raw SPARQL) via CI
- Queries target the WikiPathways SPARQL endpoint at `https://sparql.wikipathways.org/sparql`
- Consumed by the [WikiPathways Snorql UI](http://sparql.wikipathways.org/) for automated loading

## Layers

**Query Content Layer (`.rq` files):**
- Purpose: Store raw SPARQL queries ready for execution
- Location: All lettered directories (`A. Metadata/` through `J. Authors/`)
- Contains: 90 `.rq` files with raw SPARQL SELECT/CONSTRUCT/ASK queries
- Depends on: Nothing (standalone queries) or generated from `.ttl` files
- Used by: WikiPathways Snorql UI

**Metadata Layer (`.ttl` files):**
- Purpose: Wrap SPARQL queries with RDF metadata (description, keywords, target endpoint)
- Location: `A. Metadata/metadata.ttl`, `A. Metadata/prefixes.ttl`, `A. Metadata/linksets.ttl`, `B. Communities/AOP/allPathways.ttl`
- Contains: 4 Turtle/RDF files using SHACL vocabulary (`sh:SPARQLSelectExecutable`)
- Depends on: Nothing
- Used by: CI pipeline to generate corresponding `.rq` files

**Build/CI Layer:**
- Purpose: Extract raw SPARQL from `.ttl` metadata wrappers into `.rq` files
- Location: `scripts/transformDotTtlToDotSparql.py`, `.github/workflows/extractRQs.yml`
- Contains: Python extraction script and GitHub Actions workflow
- Depends on: `rdflib` Python package
- Used by: GitHub Actions on push to `master`

## Data Flow

**TTL-to-RQ Generation (CI):**

1. Developer creates or edits a `.ttl` file containing SPARQL wrapped in SHACL metadata
2. Push to `master` triggers `.github/workflows/extractRQs.yml`
3. Workflow runs `scripts/transformDotTtlToDotSparql.py` which:
   - Finds all `**/*.ttl` files recursively via `glob`
   - Parses each with `rdflib.Graph`
   - Extracts SPARQL from `sh:select`, `sh:ask`, or `sh:construct` predicates
   - Writes extracted query to a `.rq` file with the same basename
4. Workflow auto-commits any new/changed `.rq` files back to `master`

**Direct RQ Authoring (majority of queries):**

1. Developer creates a `.rq` file directly in the appropriate lettered directory
2. No CI processing needed; file is immediately available
3. 86 of 90 `.rq` files follow this pattern (no corresponding `.ttl`)

**Query Consumption (external):**

1. WikiPathways Snorql UI loads `.rq` files from this repository
2. Queries are executed against `https://sparql.wikipathways.org/sparql`

## Key Abstractions

**TTL Query Wrapper:**
- Purpose: Annotate SPARQL queries with machine-readable metadata
- Examples: `A. Metadata/metadata.ttl`, `B. Communities/AOP/allPathways.ttl`
- Pattern: Each `.ttl` file declares a `sh:SPARQLExecutable` / `sh:SPARQLSelectExecutable` resource with:
  - `rdfs:comment` - Human-readable description (English)
  - `sh:select` (or `sh:ask`/`sh:construct`) - The actual SPARQL query as a string literal
  - `schema:target` - The SPARQL endpoint URL
  - `schema:keywords` - Categorization keywords
  - `ex:` namespace prefix pointing to `https://bigcat-um.github.io/sparql-examples/WikiPathways/`

**Community Tag Pattern:**
- Purpose: Filter pathways by community using ontology tags
- Examples: `B. Communities/AOP/allPathways.rq`, `B. Communities/COVID19/allPathways.rq`
- Pattern: `?pathway wp:ontologyTag cur:<CommunityName>` where community names include `AOP`, `COVID19`, `RareDiseases`, `Lipids`, `IEM`, `CIRM`, `Reactome`, `WormBase`

**Federated Query Pattern:**
- Purpose: Join WikiPathways data with external SPARQL endpoints
- Examples: `C. Collaborations/neXtProt/ProteinMitochondria.rq`, `H. Chemistry/IDSM_similaritySearch.rq`, `C. Collaborations/smallMolecules_Rhea_IDSM/molecularSimularity_Reactions.rq`
- Pattern: Uses `SERVICE <external-endpoint-url> { ... }` to query remote SPARQL endpoints (neXtProt, IDSM/ChEBI, Rhea, LIPID MAPS)

## Entry Points

**CI Entry Point:**
- Location: `.github/workflows/extractRQs.yml`
- Triggers: Push to `master` branch, or manual `workflow_dispatch`
- Responsibilities: Run Python extraction script, auto-commit generated `.rq` files

**Extraction Script:**
- Location: `scripts/transformDotTtlToDotSparql.py`
- Triggers: Called by CI workflow or run manually (`python scripts/transformDotTtlToDotSparql.py`)
- Responsibilities: Parse all `.ttl` files, extract SPARQL, write `.rq` files

## Error Handling

**Strategy:** Minimal -- the extraction script has no explicit error handling

**Patterns:**
- CI workflow checks `git diff --exit-code --staged` to avoid empty commits
- No validation of SPARQL syntax in generated `.rq` files
- No testing framework; queries are validated by manual execution against the endpoint

## Cross-Cutting Concerns

**Logging:** Print statements in extraction script (`print("file: " + fn)`)
**Validation:** None automated; relies on SPARQL endpoint to reject malformed queries
**Authentication:** None; the WikiPathways SPARQL endpoint is public

---

*Architecture analysis: 2026-03-06*
