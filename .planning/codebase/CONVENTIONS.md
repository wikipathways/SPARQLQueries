# Coding Conventions

**Analysis Date:** 2026-03-06

## Dual-Format Query System

Queries exist in two formats. The `.ttl` (Turtle/RDF) files are the source of truth when present; `.rq` files are either auto-generated from `.ttl` by CI, or hand-written standalone files.

- Only 4 queries currently have `.ttl` sources: `prefixes.ttl`, `metadata.ttl`, `linksets.ttl` (in `A. Metadata/`), and `allPathways.ttl` (in `B. Communities/AOP/`).
- All other `.rq` files are hand-written and edited directly.
- Never edit a `.rq` file if a corresponding `.ttl` exists. Edit the `.ttl` instead.

## Naming Patterns

**Directories:**
- Use lettered prefixes with dot-space separator: `A. Metadata`, `B. Communities`, `C. Collaborations`, etc.
- Subdirectories use descriptive names: `datacounts`, `datasources`, `species`, `AOP`, `COVID19`
- Community names use their proper casing: `RareDiseases`, `WormBase`, `Inborn Errors of Metabolism`

**Files (.rq - standalone queries):**
- Use camelCase: `countPathways.rq`, `averageDatanodes.rq`, `GenesofPathway.rq`
- Prefix with action verb when counting/listing: `count*`, `average*`, `all*`, `dump*`
- Use `WPfor` prefix for datasource queries: `WPforHMDB.rq`, `WPforNCBI.rq`, `WPforEnsembl.rq`
- Some files use spaces in names (DSMN directory): `extracting directed metabolic reactions.rq` - avoid this pattern for new files

**Files (.ttl - RDF-wrapped queries):**
- Use same base name as corresponding `.rq`: `metadata.ttl` -> `metadata.rq`

**SPARQL Variables:**
- Use `?camelCase` for variables: `?pathway`, `?geneProduct`, `?pathwayCount`, `?DataNodeLabel`
- Inconsistent casing exists: `?PathwayTitle` vs `?pathwayName` vs `?title` - prefer `?camelCase` for new queries
- Use `?pathwayRes` for pathway resource URIs, `?wpid` for WikiPathways identifiers
- Use descriptive suffixes: `?titleLit` for literal values, `?pathwayCount` for aggregates

## SPARQL Query Style

**PREFIX declarations:**
- Most queries (67 of 90) rely on endpoint-predefined prefixes and omit PREFIX declarations
- When PREFIX is needed, declare at the top of the file before SELECT/ASK/CONSTRUCT
- Common implicit prefixes available at the endpoint: `wp:`, `dc:`, `dcterms:`, `void:`, `pav:`, `cur:`, `rdfs:`, `skos:`, `rdf:`, `gpml:`, `fn:`
- Casing is inconsistent (`PREFIX` vs `prefix`) - use uppercase `PREFIX` for new queries
- Spacing after prefix name is inconsistent (`PREFIX wp:` with space vs `PREFIX rh:<...>` without) - use a space after the colon for new queries

**SELECT clause:**
- Use `SELECT DISTINCT` by default to avoid duplicate rows
- Use `str(?variable)` to extract string values from literals: `(str(?title) as ?PathwayTitle)`
- Use `fn:substring(?var, offset)` or `SUBSTR(STR(?var), pos)` for extracting substrings from URIs
- Use `COUNT`, `AVG`, `MIN`, `MAX` for aggregation queries
- Use `GROUP_CONCAT` for concatenating grouped values: `(GROUP_CONCAT(DISTINCT ?wikidata;separator=", ") AS ?results)`

**WHERE clause formatting:**
- Opening brace on same line as WHERE: `WHERE {`
- Use 2-4 space indentation inside WHERE blocks (inconsistent, but indent at least 2 spaces)
- Chain triple patterns with semicolons for same subject:
  ```sparql
  ?pathway wp:ontologyTag cur:COVID19 ;
           a wp:Pathway ;
           dc:title ?title .
  ```
- Use period `.` to terminate triple pattern groups
- Use `OPTIONAL { }` for non-required fields
- Use `FILTER` for string matching: `FILTER regex(...)`, `FILTER(contains(...))`
- Use `FILTER NOT EXISTS { }` for negation patterns

**Comments:**
- Use `#` for SPARQL comments
- Place descriptive comment at top of file when purpose is not obvious from filename
- Use `#Replace "WP1560" with WP ID of interest` style inline comments for parameterized values
- Use `### Part N: ###` style section headers in complex multi-part queries (see `I. DirectedSmallMoleculesNetwork (DSMN)/`)

**Federated queries (SERVICE):**
- Use `SERVICE <endpoint-url> { ... }` for cross-endpoint federation
- Common federated endpoints:
  - neXtProt: `<https://api.nextprot.org/sparql>`
  - IDSM/ChEBI: `<https://idsm.elixir-czech.cz/sparql/endpoint/chebi>`
  - LIPID MAPS: `<https://lipidmaps.org/sparql>`
  - Rhea: `<https://sparql.rhea-db.org/sparql>`

**Query termination:**
- End queries with `ORDER BY` when results should be sorted
- Use `LIMIT` when sampling or restricting results
- No trailing newline requirement (inconsistent across files)

## TTL File Conventions

**Structure for .ttl query wrappers:**
```turtle
@prefix ex: <https://bigcat-um.github.io/sparql-examples/WikiPathways/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix schema: <https://schema.org/> .
@prefix sh: <http://www.w3.org/ns/shacl#> .

ex:metadata a sh:SPARQLExecutable,
       sh:SPARQLSelectExecutable ;
    rdfs:comment "Description of what the query does."@en ;
    sh:prefixes _:sparql_examples_prefixes ;
    sh:select """SPARQL QUERY HERE""" ;
    schema:target <https://sparql.wikipathways.org/sparql> ;
    schema:keywords "keyword1", "keyword2" .
```

**Required elements in .ttl files:**
- Always include all 5 `@prefix` declarations (ex, rdf, rdfs, schema, sh)
- Use `ex:metadata` as the subject (even across different files - this is the current pattern)
- Type as both `sh:SPARQLExecutable` and `sh:SPARQLSelectExecutable` (for SELECT queries)
- Include `rdfs:comment` with `@en` language tag
- Include `schema:target` pointing to `<https://sparql.wikipathways.org/sparql>`
- Include `schema:keywords` with comma-separated quoted strings

## Python Script Conventions

**Single script:** `scripts/transformDotTtlToDotSparql.py`

**Style:**
- No function decomposition (single procedural script)
- Uses `rdflib` for RDF parsing
- Uses `glob.glob` with `recursive=True` for file discovery
- Uses f-strings for string formatting
- Uses `print()` for progress output
- No error handling (assumes all .ttl files are valid)
- No type hints, no docstrings

## Import Organization

Not applicable - SPARQL queries use PREFIX declarations instead of imports. For the single Python script, imports are at the top: stdlib first (`os`, `glob`), then third-party (`rdflib`).

## Error Handling

**SPARQL queries:** No error handling. Queries rely on the SPARQL endpoint to handle malformed queries or missing data. Use `OPTIONAL { }` to gracefully handle missing triples.

**Python script:** No try/except blocks. Script will crash on invalid TTL files or missing directories.

## Comments

**When to Comment in .rq files:**
- Add a comment when the filename alone does not explain the query purpose
- Add inline comments for hardcoded values that users should customize (e.g., pathway IDs)
- Add section comments (`### Part N: ###`) for complex multi-section queries
- Use comments to mark commented-out alternative filters

**When NOT to Comment:**
- Simple queries where the filename is self-explanatory (e.g., `countPathways.rq`)

## Common WikiPathways Ontology Patterns

**Pathway identification:**
```sparql
?pathway a wp:Pathway .
?pathway dcterms:identifier "WP1560" .
?pathway dc:title ?title .
```

**Community filtering:**
```sparql
?pathway wp:ontologyTag cur:COVID19 .
?pathway wp:ontologyTag cur:AOP .
?pathway wp:ontologyTag cur:IEM .
?pathway wp:ontologyTag cur:AnalysisCollection .
?pathway wp:ontologyTag cur:Reactome_Approved .
```

**Data node types:**
```sparql
?node a wp:GeneProduct .
?node a wp:Protein .
?node a wp:Metabolite .
?node a wp:DataNode .
```

**Identifier bridging (BridgeDb):**
```sparql
?metabolite wp:bdbHmdb ?hmdbId .
?metabolite wp:bdbChEBI ?chebiId .
?metabolite wp:bdbWikidata ?wikidataId .
?metabolite wp:bdbLipidMaps ?lipidMapsId .
?gene wp:bdbEntrezGene ?ncbiGeneId .
?gene wp:bdbHgncSymbol ?geneName .
?gene wp:bdbEnsembl ?ensemblId .
```

**Relationship patterns:**
```sparql
?node dcterms:isPartOf ?pathway .
?interaction wp:participants ?participants .
?interaction wp:source ?source .
?interaction wp:target ?target .
```

---

*Convention analysis: 2026-03-06*
