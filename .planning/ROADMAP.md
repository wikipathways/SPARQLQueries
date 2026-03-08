# Roadmap: WikiPathways SPARQL Query Enrichment

## Overview

This roadmap transforms ~85 SPARQL query files from opaque camelCase filenames into a browsable, filterable, interactive query library in the SNORQL UI. Work proceeds in four phases: establish conventions and fix CI (so nothing breaks), add titles and categories (highest-impact headers), add descriptions (deeper query documentation), then parameterize interactive queries and enforce all conventions via CI lint.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Foundation** - CI pipeline fix, controlled category vocabulary, and header conventions guide
- [x] **Phase 2: Titles and Categories** - Add title and category headers to all ~85 .rq files (completed 2026-03-07)
- [ ] **Phase 3: Descriptions** - Add description headers to all 90 .rq files
- [ ] **Phase 4: Parameterization and Validation** - Add param headers to ~15-20 queries and enable CI lint for all headers

## Phase Details

### Phase 1: Foundation
**Goal**: Conventions and tooling are in place so all subsequent header work follows consistent rules and the CI pipeline does not destroy enriched headers
**Depends on**: Nothing (first phase)
**Requirements**: FOUND-01, FOUND-02, FOUND-03
**Success Criteria** (what must be TRUE):
  1. The CI extraction script generates .rq files from .ttl sources with comment headers intact (title, category, description)
  2. A controlled category vocabulary list exists mapping each folder to its canonical category name
  3. A header conventions guide exists documenting the exact format rules for title, description, category, and param headers with examples
**Plans:** 2 plans

Plans:
- [ ] 01-01-PLAN.md — CI script header preservation with TDD (FOUND-01)
- [ ] 01-02-PLAN.md — Category vocabulary and header conventions guide (FOUND-02, FOUND-03)

### Phase 2: Titles and Categories
**Goal**: The SNORQL UI displays every query with a human-readable title and a filterable category instead of raw filenames
**Depends on**: Phase 1
**Requirements**: META-01, META-02
**Success Criteria** (what must be TRUE):
  1. Every .rq file in the repository has a `# title:` header with a clear, descriptive display name
  2. Every .rq file has a `# category:` header using exactly one value from the controlled vocabulary
  3. The SNORQL UI renders the query list with readable names grouped by category
**Plans:** 3/3 plans complete

Plans:
- [ ] 02-01-PLAN.md — Header validation test suite (META-01, META-02)
- [ ] 02-02-PLAN.md — Add title and category headers to A. Metadata and B. Communities (META-01, META-02)
- [ ] 02-03-PLAN.md — Add title and category headers to C-J directories (META-01, META-02)

### Phase 3: Descriptions
**Goal**: Every query in the SNORQL UI has a description explaining what it does and what results to expect
**Depends on**: Phase 2
**Requirements**: META-03
**Success Criteria** (what must be TRUE):
  1. Every .rq file has a `# description:` header explaining what the query does and what it returns
  2. Federated queries (those using SERVICE clauses) mention federation and potential performance impact in their descriptions
**Plans:** 2/4 plans executed

Plans:
- [ ] 03-01-PLAN.md — Description test setup and CI verification (META-03)
- [ ] 03-02-PLAN.md — Add descriptions to A. Metadata (29 files) (META-03)
- [ ] 03-03-PLAN.md — Add descriptions to B. Communities and C. Collaborations (32 files, 8 federated) (META-03)
- [ ] 03-04-PLAN.md — Add descriptions to D-J directories (29 files, 1 federated) (META-03)

### Phase 4: Parameterization and Validation
**Goal**: Queries with hardcoded values become interactive in SNORQL, and a CI lint step ensures all files maintain required headers going forward
**Depends on**: Phase 3
**Requirements**: PARAM-01, PARAM-02, PARAM-03, FOUND-04
**Success Criteria** (what must be TRUE):
  1. Queries with hardcoded species URIs offer an interactive organism selection parameter via `# param:` with enum type
  2. Queries with hardcoded pathway IDs, molecule IDs, or gene names have `# param:` headers with appropriate types (string/uri)
  3. Queries with hardcoded external database references have `# param:` headers where the reference is a meaningful user choice
  4. A CI lint step runs on every push and fails if any .rq file is missing required headers (title, category, description)
**Plans**: TBD

Plans:
- [ ] 04-01: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 2/2 | Complete | 2026-03-06 |
| 2. Titles and Categories | 3/3 | Complete   | 2026-03-07 |
| 3. Descriptions | 2/4 | In Progress|  |
| 4. Parameterization and Validation | 0/? | Not started | - |
