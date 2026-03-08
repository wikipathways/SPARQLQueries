# Header Conventions Guide

Definitive reference for `.rq` file header format in the WikiPathways SPARQL query collection. All enrichment work (Phases 2-4) must follow these rules.

## Header Format Overview

- Headers are comment lines (`#`) at the **top** of `.rq` files
- The header block ends at the **first blank line**
- One blank line separates headers from the SPARQL query body
- Fields use the format `# field: value`

## Field Order

Headers must appear in this order:

```
# title: [value]
# category: [value]
# description: [value]
# description: [continued value if multi-line]
# keywords: [optional, comma-separated]
# param: [optional, pipe-delimited]
```

**Required fields:** `title`, `category`, `description`
**Optional fields:** `keywords`, `param`

## Field Specifications

### `# title:` (required)

One line. Clear, human-readable display name for the SNORQL UI.

- Derived from query purpose, not the filename
- Use title case
- Keep concise (under ~60 characters)

| Good                              | Bad                      |
|-----------------------------------|--------------------------|
| `# title: All Pathways for Species` | `# title: allPathwaysBySpecies` |
| `# title: Gene-Pathway Associations` | `# title: query1`       |

### `# category:` (required)

One line. Exactly one value from the controlled vocabulary in `categories.json`.

Valid values: Metadata, Data Sources, Communities, Collaborations, General, Literature, Data Export, Curation, Chemistry, DSMN, Authors.

The category is determined by the query's directory location. See `categories.json` for the directory-to-category mapping.

### `# description:` (required)

Explains what the query does and what results to expect.

**Single-line:**
```
# description: Lists all pathways in the WikiPathways database.
```

**Multi-line:** Repeat the `# description:` prefix on each continuation line. This is required because the SNORQL parser collects all lines matching the `# description:` prefix. Bare continuation lines (e.g., `#   continued text`) are NOT captured by the UI.

```
# description: Lists all pathways tagged with the AOP community.
# description: Returns pathway identifiers, titles, and organism.
```

**Federated queries** (those containing `SERVICE` clauses) should mention federation and potential performance impact:
```
# description: Retrieves compound mappings from MetaNetX via federation.
# description: Uses a federated SERVICE call; may be slow depending on endpoint availability.
```

### `# keywords:` (optional, future)

Comma-separated values on one line. NOT currently rendered by the SNORQL UI but included for future compatibility.

```
# keywords: pathways, species, metadata
```

### `# param:` (optional, Phase 4)

Pipe-delimited format for parameterized queries:

```
# param: name | type | defaultValue | label
```

**Supported types:**
- `string` -- free-text input
- `uri` -- expects a URI value
- `enum:val1,val2,val3` -- dropdown selection

Multiple parameters use multiple `# param:` lines.

## SNORQL Parser Behavior

The SNORQL parser scans **all lines** in the file for field-prefixed patterns, not just leading lines. This means:

1. `# title:`, `# category:`, `# description:`, and `# param:` prefixes must **only** appear in the header block
2. Inline SPARQL comments elsewhere in the file must **not** use these exact prefixes
3. Use alternative phrasing for inline comments (e.g., `# Note: this filters by species` instead of `# description: this filters by species`)

## Existing Comments Handling

During enrichment (Phase 2+):

- **Descriptive comments** at the top of `.rq` files should be interpreted and absorbed into `# description:` headers
- **Inline usage hints** (e.g., `# Replace "WP1560" with WP ID of interest`) remain as inline comments BELOW the header block; they are not folded into the description
- **Existing `# title:` or `# description:` lines** that already follow the conventions are kept as-is

## TTL Metadata Mapping

For queries with `.ttl` source files, the following mapping applies. This is documented for future reference; TTL metadata extraction is NOT implemented in Phase 1.

| TTL Field          | Header Field      | Notes                                      |
|--------------------|-------------------|--------------------------------------------|
| `rdfs:label`       | `# title:`        | If present; otherwise derive from filename |
| `rdfs:comment`     | `# description:`  | May need splitting into multiple lines     |
| `schema:keywords`  | `# keywords:`     | NOT mapped to `# category:`                |
| (folder location)  | `# category:`     | Always derived from directory, never TTL   |

## Complete Examples

### Example 1: Minimal query (title + category + description)

```sparql
# title: All Pathways
# category: General
# description: Returns all pathways in the WikiPathways database with their titles and organisms.

SELECT DISTINCT ?pathway ?title ?organism
WHERE {
  ?pathway a wp:Pathway ;
           dc:title ?title ;
           wp:organismName ?organism .
}
ORDER BY ?title
```

### Example 2: Multi-line description

```sparql
# title: AOP Community Pathways
# category: Communities
# description: Lists all pathways tagged with the Adverse Outcome Pathway (AOP) community.
# description: Returns pathway identifiers, titles, and last revision dates.
# description: Useful for tracking AOP-related content in WikiPathways.

SELECT ?pathway ?title ?date
WHERE {
  ?pathway a wp:Pathway ;
           dc:title ?title ;
           dcterms:subject cur:AOP ;
           pav:lastRefreshedOn ?date .
}
ORDER BY DESC(?date)
```

### Example 3: Parameterized query (Phase 4)

```sparql
# title: Pathways by Species
# category: General
# description: Returns all pathways for a given species.
# param: species | enum:Homo sapiens,Mus musculus,Rattus norvegicus,... | Homo sapiens | Species

SELECT ?pathway ?title
WHERE {
  ?pathway a wp:Pathway ;
           dc:title ?title ;
           wp:organismName "{{species}}" .
}
ORDER BY ?title
```

---

*Reference document for WikiPathways SPARQL query header enrichment.*
*Controlled category vocabulary: see `categories.json`.*
