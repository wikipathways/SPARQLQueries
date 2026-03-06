# WikiPathways SPARQL Query Enrichment

## What This Is

A collection of ~85 SPARQL queries for the WikiPathways knowledge base, served via the SNORQL UI. The queries are organized in lettered directories (A-J) by topic and target the WikiPathways SPARQL endpoint. This project enriches the repository with structured comment headers, interactive parameters, and improved metadata so the SNORQL UI can provide a better browsing and discovery experience.

## Core Value

Every `.rq` file has proper comment headers (title, description, category) so the SNORQL UI displays meaningful names, descriptions, and filterable categories instead of raw filenames.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Add `# title:` headers to all ~85 .rq files with clear, descriptive display names
- [ ] Add `# description:` headers to all .rq files explaining what each query does and returns
- [ ] Add `# category:` headers matching the folder-based topics (Metadata, Communities, Literature, Chemistry, etc.)
- [ ] Add `# param:` headers to queries with hardcoded values (species URIs, pathway IDs, PubChem IDs, gene names) to make them interactive
- [ ] Revise folder structure for SNORQL compatibility (max 2 levels of nesting, clean naming)
- [ ] Ensure .rq files generated from .ttl sources also include comment headers (update CI pipeline or TTL extraction script)
- [ ] Keep the BiGCAT-UM/sparql-examples repo separate — no merging, possible future sync

### Out of Scope

- Merging with BiGCAT-UM/sparql-examples repo — different purpose (SIB ecosystem vs SNORQL UI)
- Migrating all queries to TTL format — .rq with comment headers is the primary format for SNORQL
- Rewriting queries — focus is on adding metadata, not changing query logic
- Adding new queries — focus is on enriching existing ones

## Context

- The SNORQL UI parses `.rq` comment headers: `# title:`, `# description:`, `# category:`, and `# param:` (see Snorql-UI/EXAMPLES.md for format spec)
- Parameters use `{{name}}` placeholders in query body with pipe-separated header format: `# param: name|type|default|label`
- Supported param types: `string`, `uri`, `enum:value1,value2,...`
- SNORQL UI supports up to 2 levels of folder nesting; 3 levels max
- Currently 4 queries have `.ttl` source files; the CI pipeline (`scripts/transformDotTtlToDotSparql.py`) extracts SPARQL from TTL into `.rq` but does not carry over metadata as comment headers
- The lettered folder prefixes (A-J) serve alphabetical ordering and should be kept
- Categories should match folder topics: Metadata, Communities, Collaborations, General, Literature, Datadump, Curation, Chemistry, DSMN, Authors

## Constraints

- **Format**: Comment headers must follow the exact SNORQL UI spec (`# title:`, `# description:`, `# category:`, `# param:`)
- **Nesting**: Maximum 2 levels of folder nesting for SNORQL visibility
- **TTL coexistence**: The 4 existing TTL files and their CI pipeline must continue to work; enriched .rq files from TTL sources need a strategy for preserving headers
- **Repo separation**: BiGCAT-UM/sparql-examples remains a separate project

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Keep lettered folder prefixes | They provide alphabetical ordering in the UI | — Pending |
| Keep both repos separate | SPARQLQueries serves SNORQL UI; BiGCAT-UM serves SIB ecosystem | — Pending |
| Categories match folders | Simpler mental model; folders already represent logical groupings | — Pending |
| Add params where useful | Queries with hardcoded species, IDs, or filters benefit from interactivity | — Pending |

---
*Last updated: 2026-03-06 after initialization*
