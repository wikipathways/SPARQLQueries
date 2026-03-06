# External Integrations

**Analysis Date:** 2026-03-06

## Primary SPARQL Endpoint

**WikiPathways:**
- Endpoint: `https://sparql.wikipathways.org/sparql`
- Purpose: Primary data source for all queries; contains RDF representation of WikiPathways biological pathway data
- Auth: None (public endpoint)
- UI: http://sparql.wikipathways.org/ (Snorql interface that loads these `.rq` files)
- Declared in `.ttl` files via `schema:target <https://sparql.wikipathways.org/sparql>`

## Federated SPARQL Endpoints

Several queries use SPARQL 1.1 `SERVICE` clauses to federate across external SPARQL endpoints. These are called at query execution time from the WikiPathways endpoint.

**IDSM/ELIXIR Czech (Chemical similarity search):**
- Endpoint: `https://idsm.elixir-czech.cz/sparql/endpoint/chebi`
- Purpose: Chemical structure similarity search using Sachem engine against ChEBI compounds
- Used in:
  - `H. Chemistry/IDSM_similaritySearch.rq`
  - `C. Collaborations/smallMolecules_Rhea_IDSM/molecularSimularity_Reactions.rq`
- Vocabularies: `sachem:`, `sso:` (SemanticScience)

**IDSM/ELIXIR Czech (MolMeDB):**
- Endpoint: `https://idsm.elixir-czech.cz/sparql/endpoint/molmedb`
- Purpose: Molecular membrane database queries for PubChem compound-pathway mappings
- Used in:
  - `C. Collaborations/MolMeDB/ONEpubchem_MANYpathways.rq`
  - `C. Collaborations/MolMeDB/SUBSETpathways_ONEpubchem.rq`

**LIPID MAPS:**
- Endpoint: `https://lipidmaps.org/sparql`
- Purpose: Lipid classification data; maps LIPID MAPS categories to WikiPathways metabolites
- Used in:
  - `B. Communities/Lipids/LIPIDMAPS_Federated.rq`
- Vocabularies: `chebi:` (OBO)

**neXtProt:**
- Endpoint: `https://api.nextprot.org/sparql`
- Purpose: Human protein knowledge base; retrieves cellular location and mitochondrial protein data
- Used in:
  - `C. Collaborations/neXtProt/ProteinCellularLocation.rq`
  - `C. Collaborations/neXtProt/ProteinMitochondria.rq`
- Vocabularies: neXtProt RDF namespace (`:` prefix = `http://nextprot.org/rdf#`)

**AOP-Wiki (BiGCaT):**
- Endpoint: `https://aopwiki.rdf.bigcat-bioinformatics.org/sparql/`
- Purpose: Adverse Outcome Pathway wiki; links WikiPathways metabolites to AOP stressors
- Used in:
  - `C. Collaborations/AOP-Wiki/MetaboliteInAOP-Wiki.rq`
- Vocabularies: `aopo:` (AOP ontology), `cheminf:` (chemical informatics)

**MetaNetX:**
- Endpoint: `https://rdf.metanetx.org/sparql/`
- Purpose: Metabolic reaction network cross-references; maps WikiPathways reactions to Rhea/MetaNetX IDs
- Used in:
  - `C. Collaborations/MetaNetX/reactionID_mapping.rq`
- Vocabularies: `mnx:`, `rhea:`

**Rhea (commented out):**
- Endpoint: `https://sparql.rhea-db.org/sparql` (currently commented out in code)
- Purpose: Biochemical reaction database
- Referenced in:
  - `C. Collaborations/smallMolecules_Rhea_IDSM/molecularSimularity_Reactions.rq` (lines 40-43, commented)

## External Identifier Systems

Queries reference these external identifier namespaces (not federated, but used for URI construction and cross-linking):

- **ChEBI:** `http://purl.obolibrary.org/obo/CHEBI_` - Chemical entities of biological interest
- **PubChem CID:** Via `wp:bdbPubChem` bridge DB links
- **NCBI Gene:** `http://identifiers.org/ncbigene/`
- **Ensembl:** Via `wp:bdbEnsembl` bridge DB links
- **HGNC:** Via `wp:bdbHgnc` bridge DB links
- **HMDB:** Via `wp:bdbHmdb` bridge DB links
- **ChemSpider:** Via `wp:bdbChemspider` bridge DB links
- **LIPID MAPS:** `https://identifiers.org/lipidmaps/`
- **Wikidata:** `http://www.wikidata.org/prop/direct/` (used in curation queries)
- **PubMed:** `http://www.ncbi.nlm.nih.gov/pubmed/`
- **CAS:** `http://identifiers.org/cas/`

## Data Storage

**Databases:**
- No local database; all data lives in the remote WikiPathways SPARQL triplestore
- Connection: Public HTTP SPARQL endpoint, no credentials

**File Storage:**
- Local filesystem only (git repository of `.rq` and `.ttl` files)

**Caching:**
- None

## Authentication & Identity

**Auth Provider:**
- Not applicable; all SPARQL endpoints are public and require no authentication

## Monitoring & Observability

**Error Tracking:**
- None

**Logs:**
- None (queries are static files)

## CI/CD & Deployment

**Hosting:**
- GitHub (source repository)
- WikiPathways Snorql UI at http://sparql.wikipathways.org/ (consumes queries)

**CI Pipeline:**
- GitHub Actions (`.github/workflows/extractRQs.yml`)
- Trigger: Push to `master` branch or manual `workflow_dispatch`
- Steps:
  1. Checkout repository
  2. Setup Python 3.11
  3. `pip install rdflib`
  4. Run `python scripts/transformDotTtlToDotSparql.py`
  5. Auto-commit generated `.rq` files back to `master` if changes detected

**Deployment Model:**
- Git-based; the Snorql UI reads queries from the repository
- CI auto-commits generated `.rq` files, so the repository is always up to date

## Environment Configuration

**Required env vars:**
- None

**Secrets location:**
- None required; no secrets in this repository

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

---

*Integration audit: 2026-03-06*
