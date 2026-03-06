# Requirements: WikiPathways SPARQL Query Enrichment

**Defined:** 2026-03-06
**Core Value:** Every .rq file has proper comment headers so the SNORQL UI displays meaningful names, descriptions, and filterable categories

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Foundation

- [x] **FOUND-01**: CI extraction script preserves or emits comment headers when generating .rq from .ttl
- [x] **FOUND-02**: Controlled category vocabulary defined (matching folder topics: Metadata, Communities, Collaborations, General, Literature, Datadump, Curation, Chemistry, DSMN, Authors)
- [x] **FOUND-03**: Header conventions guide documenting format rules for title, description, category, and param headers
- [ ] **FOUND-04**: CI lint step validates that all .rq files have required headers (title, category, description)

### Metadata

- [x] **META-01**: All ~85 .rq files have `# title:` headers with clear display names
- [x] **META-02**: All ~85 .rq files have `# category:` headers using the controlled vocabulary
- [ ] **META-03**: All ~85 .rq files have `# description:` headers explaining what the query does and returns

### Parameterization

- [ ] **PARAM-01**: Queries with hardcoded species URIs have `# param:` with enum type for organism selection
- [ ] **PARAM-02**: Queries with hardcoded pathway/molecule IDs have `# param:` with string/uri type
- [ ] **PARAM-03**: Queries with hardcoded external database references have `# param:` where appropriate

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Sync

- **SYNC-01**: Metadata sync between SPARQLQueries repo and BiGCAT-UM/sparql-examples repo
- **SYNC-02**: Script to generate TTL files from enriched .rq files for SIB ecosystem

### Quality

- **QUAL-01**: SPARQL syntax validation in CI pipeline
- **QUAL-02**: Automated testing of queries against WikiPathways endpoint

## Out of Scope

| Feature | Reason |
|---------|--------|
| Merging with BiGCAT-UM/sparql-examples | Different purpose (SIB ecosystem vs SNORQL UI) |
| Migrating all queries to TTL format | .rq with comment headers is the primary format for SNORQL |
| Rewriting query logic | Focus is on adding metadata, not changing queries |
| Adding new queries | Focus is on enriching existing ones |
| Folder restructuring | Lettered prefixes serve alphabetical ordering; paths may be referenced externally |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| FOUND-01 | Phase 1: Foundation | Complete |
| FOUND-02 | Phase 1: Foundation | Complete |
| FOUND-03 | Phase 1: Foundation | Complete |
| FOUND-04 | Phase 4: Parameterization and Validation | Pending |
| META-01 | Phase 2: Titles and Categories | Complete |
| META-02 | Phase 2: Titles and Categories | Complete |
| META-03 | Phase 3: Descriptions | Pending |
| PARAM-01 | Phase 4: Parameterization and Validation | Pending |
| PARAM-02 | Phase 4: Parameterization and Validation | Pending |
| PARAM-03 | Phase 4: Parameterization and Validation | Pending |

**Coverage:**
- v1 requirements: 10 total
- Mapped to phases: 10
- Unmapped: 0

---
*Requirements defined: 2026-03-06*
*Last updated: 2026-03-06 after roadmap creation*
