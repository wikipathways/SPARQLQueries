# Codebase Structure

**Analysis Date:** 2026-03-06

## Directory Layout

```
SPARQLQueries/
├── A. Metadata/              # Dataset metadata, prefixes, species counts, datasource queries
│   ├── datacounts/           # Aggregate count queries (pathways, proteins, metabolites, etc.)
│   ├── datasources/          # Queries filtering by external data source (HMDB, Ensembl, etc.)
│   └── species/              # Per-species count and listing queries
├── B. Communities/           # Community-specific pathway queries
│   ├── AOP/                  # Adverse Outcome Pathways
│   ├── CIRM Stem Cell Pathways/
│   ├── COVID19/
│   ├── Inborn Errors of Metabolism/
│   ├── Lipids/
│   ├── RareDiseases/
│   ├── Reactome/
│   └── WormBase/
├── C. Collaborations/        # Cross-database federated queries
│   ├── AOP-Wiki/
│   ├── MetaNetX/
│   ├── MolMeDB/
│   ├── neXtProt/
│   └── smallMolecules_Rhea_IDSM/
├── D. General/               # Generic per-pathway queries (genes, metabolites, interactions, ontology)
├── E. Literature/            # PubMed references and citation queries
├── F. Datadump/              # Bulk data export queries
├── G. Curation/              # Data quality and curation audit queries
├── H. Chemistry/             # Chemical structure queries (SMILES, similarity search)
├── I. DirectedSmallMoleculesNetwork (DSMN)/  # Directed metabolic network extraction queries
├── J. Authors/               # Author and contributor queries
├── scripts/                  # Build tooling
│   └── transformDotTtlToDotSparql.py  # TTL-to-RQ extraction script
├── .github/
│   └── workflows/
│       └── extractRQs.yml   # CI workflow for TTL-to-RQ generation
├── CLAUDE.md                 # AI assistant guidance
├── README.md                 # Project description
└── LICENSE                   # GPL-3.0
```

## Directory Purposes

**`A. Metadata/`:**
- Purpose: Queries about the WikiPathways dataset itself (metadata, prefixes, linksets)
- Contains: `.rq` and `.ttl` files, plus three subdirectories for datacounts, datasources, and species
- Key files: `metadata.ttl`, `prefixes.ttl`, `linksets.ttl` (3 of the 4 TTL source files live here)

**`B. Communities/`:**
- Purpose: Queries scoped to specific WikiPathways community portals
- Contains: 8 subdirectories, one per community; most have `allPathways.rq` and `allProteins.rq`
- Key files: `AOP/allPathways.ttl` (the only TTL file outside `A. Metadata/`)

**`C. Collaborations/`:**
- Purpose: Federated queries that join WikiPathways with external SPARQL endpoints
- Contains: 5 subdirectories for partner databases (neXtProt, AOP-Wiki, MetaNetX, MolMeDB, Rhea/IDSM)
- Key files: `neXtProt/ProteinMitochondria.rq` (uses `SERVICE` for federated querying)

**`D. General/`:**
- Purpose: Common per-pathway queries reusable across any pathway
- Contains: 4 `.rq` files for genes, metabolites, interactions, and ontology of a given pathway
- Key files: `GenesofPathway.rq`, `MetabolitesofPathway.rq`

**`E. Literature/`:**
- Purpose: PubMed reference and citation queries
- Contains: 5 `.rq` files

**`F. Datadump/`:**
- Purpose: Bulk data export queries for downstream tools
- Contains: 3 `.rq` files (CyTargetLinker input, species dumps, ontology dumps)

**`G. Curation/`:**
- Purpose: Data quality auditing queries (missing references, unclassified metabolites, etc.)
- Contains: 7 `.rq` files

**`H. Chemistry/`:**
- Purpose: Chemical structure queries using SMILES and similarity search
- Contains: 2 `.rq` files; `IDSM_similaritySearch.rq` uses federated IDSM/ChEBI endpoint

**`I. DirectedSmallMoleculesNetwork (DSMN)/`:**
- Purpose: Extraction queries for building directed small molecule metabolic networks
- Contains: 4 `.rq` files with spaces in filenames

**`J. Authors/`:**
- Purpose: Author and contributor queries
- Contains: 4 `.rq` files

**`scripts/`:**
- Purpose: Build tooling for TTL-to-RQ extraction
- Contains: 1 Python script (`transformDotTtlToDotSparql.py`)

## Key File Locations

**Entry Points:**
- `.github/workflows/extractRQs.yml`: CI pipeline entry point
- `scripts/transformDotTtlToDotSparql.py`: Build script for generating `.rq` from `.ttl`

**Configuration:**
- `.github/workflows/extractRQs.yml`: CI configuration
- `CLAUDE.md`: AI assistant project guidance

**TTL Source Files (4 total):**
- `A. Metadata/metadata.ttl`: Dataset metadata query with description
- `A. Metadata/prefixes.ttl`: Prefix/namespace listing query
- `A. Metadata/linksets.ttl`: Linkset listing query
- `B. Communities/AOP/allPathways.ttl`: AOP community pathways query

**Core Logic:**
- `scripts/transformDotTtlToDotSparql.py`: The only executable code in the repo

## Naming Conventions

**Files:**
- `.rq` files: camelCase or PascalCase, descriptive names: `countPathwaysPerSpecies.rq`, `GenesofPathway.rq`, `WPforHMDB.rq`
- `.ttl` files: Match the basename of their corresponding `.rq` file: `metadata.ttl` produces `metadata.rq`
- Some files use spaces in names (only in `I. DirectedSmallMoleculesNetwork (DSMN)/`): `extracting directed metabolic reactions.rq`
- Prefix pattern for datasource queries: `WPfor<SourceName>.rq` (e.g., `WPforEnsembl.rq`, `WPforHMDB.rq`)

**Directories:**
- Top-level: Lettered prefix with descriptive name: `A. Metadata`, `B. Communities`, etc.
- Subdirectories: PascalCase or descriptive names: `datacounts`, `datasources`, `COVID19`, `RareDiseases`
- Community directories match WikiPathways community portal names

## Where to Add New Code

**New Query (standalone):**
- Create a `.rq` file in the appropriate lettered directory
- Use camelCase for the filename
- Include necessary PREFIX declarations at the top of the query if not using common prefixes

**New Query (with metadata):**
- Create a `.ttl` file following the SHACL pattern from `A. Metadata/metadata.ttl`
- Include `rdfs:comment`, `sh:select` (or `sh:ask`/`sh:construct`), `schema:target`, and `schema:keywords`
- CI will auto-generate the `.rq` file on push to `master`
- Do NOT manually create a `.rq` file if a `.ttl` exists; it will be overwritten

**New Community:**
- Create a subdirectory under `B. Communities/` named after the community
- Add `allPathways.rq` and `allProteins.rq` as baseline queries (follow existing pattern using `wp:ontologyTag cur:<CommunityTag>`)

**New Collaboration (federated queries):**
- Create a subdirectory under `C. Collaborations/` named after the partner database
- Use `SERVICE <endpoint-url> { ... }` for federated SPARQL queries

**New Topic Category:**
- Create a new lettered directory following the sequence (next would be `K. <TopicName>/`)
- Follow the `Letter. Name` convention with a space after the period

## Special Directories

**`scripts/`:**
- Purpose: Build tooling (Python)
- Generated: No
- Committed: Yes

**`.github/workflows/`:**
- Purpose: CI/CD pipeline definitions
- Generated: No
- Committed: Yes

**`.planning/`:**
- Purpose: Project planning and analysis documents
- Generated: Yes (by tooling)
- Committed: Varies

---

*Structure analysis: 2026-03-06*
