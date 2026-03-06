# Codebase Concerns

**Analysis Date:** 2026-03-06

## Tech Debt

**Only 4 of 90 queries use the TTL metadata format:**
- Issue: The project defines a dual-format system (`.ttl` source-of-truth with CI-generated `.rq`) but only 4 queries have `.ttl` files: `A. Metadata/prefixes.ttl`, `A. Metadata/metadata.ttl`, `A. Metadata/linksets.ttl`, `B. Communities/AOP/allPathways.ttl`. The remaining 86 `.rq` files have no structured metadata (description, keywords, target endpoint).
- Files: `A. Metadata/prefixes.ttl`, `A. Metadata/metadata.ttl`, `A. Metadata/linksets.ttl`, `B. Communities/AOP/allPathways.ttl`
- Impact: Queries lack machine-readable descriptions, keywords, and endpoint annotations. The Snorql UI cannot programmatically display query metadata for 96% of queries. Discoverability and documentation are severely limited.
- Fix approach: Incrementally create `.ttl` wrappers for all `.rq` files, following the existing SHACL `sh:SPARQLSelectExecutable` template. Prioritize by directory (start with `D. General/`, `E. Literature/`, then community queries).

**All 4 TTL files use the same `ex:metadata` subject IRI:**
- Issue: Every `.ttl` file declares its query as `ex:metadata a sh:SPARQLExecutable`, regardless of actual content. `prefixes.ttl` describes prefix listing, `linksets.ttl` describes linksets, `allPathways.ttl` describes AOP pathways -- yet all use the identifier `ex:metadata`.
- Files: `A. Metadata/prefixes.ttl` (line 7), `A. Metadata/metadata.ttl` (line 7), `A. Metadata/linksets.ttl` (line 7), `B. Communities/AOP/allPathways.ttl` (line 7)
- Impact: If these TTL files were ever loaded into a single graph, the triples would collide/merge. The subject IRI should be unique per query (e.g., `ex:prefixes`, `ex:linksets`, `ex:aop-allPathways`).
- Fix approach: Give each TTL file a unique `ex:` identifier matching the query name.

**Inconsistent PREFIX declarations across queries:**
- Issue: 70 of 90 `.rq` files omit PREFIX declarations entirely, relying on the WikiPathways SPARQL endpoint to have `wp:`, `dc:`, `dcterms:`, `rdfs:`, `rdf:`, `skos:`, `void:`, `pav:`, `cur:`, `gpml:` pre-registered. The other 20 files declare some or all prefixes explicitly. This means queries are not portable to other SPARQL clients.
- Files: All files in `A. Metadata/datacounts/`, `A. Metadata/datasources/`, `A. Metadata/species/`, `B. Communities/` (most), `D. General/`, `E. Literature/`, `F. Datadump/`, `G. Curation/` (most)
- Impact: Queries fail when run outside the WikiPathways Snorql UI or Blazegraph endpoint. Copy-pasting a query into a generic SPARQL tool produces errors. Testing queries independently is impossible without knowing which prefixes to add.
- Fix approach: Add explicit PREFIX declarations to all `.rq` files. At minimum, each query should declare every prefix it uses.

**Non-standard `fn:substring` XPath function used instead of SPARQL `SUBSTR`:**
- Issue: Seven queries use `fn:substring()` which is an XPath/XQuery function, not standard SPARQL 1.1. This is a Blazegraph-specific extension.
- Files: `F. Datadump/CyTargetLinkerLinksetInput.rq`, `A. Metadata/datasources/WPforChemSpider.rq`, `A. Metadata/datasources/WPforHMDB.rq`, `A. Metadata/datasources/WPforNCBI.rq`, `A. Metadata/datasources/WPforEnsembl.rq`, `A. Metadata/datasources/WPforHGNC.rq`, `A. Metadata/datasources/WPforPubChemCID.rq`
- Impact: These queries are locked to Blazegraph. If the WikiPathways endpoint migrates to another triplestore (Virtuoso, Fuseki, GraphDB), these queries break.
- Fix approach: Replace `fn:substring(?var, N)` with the standard SPARQL `SUBSTR(STR(?var), N)`.

**`AOP/allPathways.ttl` has wrong `schema:keywords`:**
- Issue: The AOP allPathways TTL declares `schema:keywords "prefix", "namespace"` which was copy-pasted from `prefixes.ttl`. The keywords should be "AOP", "pathway" or similar.
- Files: `B. Communities/AOP/allPathways.ttl` (line 21)
- Impact: Incorrect metadata if keywords are ever used for search/filtering.
- Fix approach: Change keywords to `"AOP", "pathway"`.

## Known Bugs

**Potential SPARQL syntax error in `countRefsPerPW.rq`:**
- Symptoms: The query uses `SELECT DISTINCT ?pathway COUNT(?pubmed) AS ?numberOfReferences` which may fail on strict SPARQL parsers -- the aggregate `COUNT(?pubmed)` should be wrapped in parentheses as `(COUNT(?pubmed) AS ?numberOfReferences)`.
- Files: `E. Literature/countRefsPerPW.rq` (line 1)
- Trigger: Running the query on a standards-compliant SPARQL 1.1 endpoint.
- Workaround: Blazegraph may accept this non-standard syntax, but it should be corrected.

**`### Part N: ###` markdown headers used as SPARQL comments:**
- Symptoms: All 4 files in `I. DirectedSmallMoleculesNetwork (DSMN)/` use `### Part 1: ###` style comments. In SPARQL, `#` begins a comment, so `### Part 1: ###` works as a comment, but the `###` syntax suggests the author may have intended markdown formatting. This is cosmetic but confusing.
- Files: `I. DirectedSmallMoleculesNetwork (DSMN)/extracting directed metabolic reactions.rq`, `I. DirectedSmallMoleculesNetwork (DSMN)/controlling duplicate mappings from Wikidata.rq`, `I. DirectedSmallMoleculesNetwork (DSMN)/extracting protein titles and identifiers for metabolic reactions.rq`, `I. DirectedSmallMoleculesNetwork (DSMN)/extracting ontologies and references for metabolic reactions.rq`
- Trigger: Not a runtime bug, but misleading for anyone reading the queries.
- Workaround: None needed for functionality; standardize comment style for readability.

## Security Considerations

**CI pipeline commits directly to master with `git push`:**
- Risk: The GitHub Actions workflow in `.github/workflows/extractRQs.yml` uses `git add .`, `git commit`, and `git push` directly to the `master` branch without branch protection or PR review. A malformed `.ttl` file could cause the CI to overwrite `.rq` files with corrupted content.
- Files: `.github/workflows/extractRQs.yml` (lines 25-35)
- Current mitigation: The workflow only runs on push to master and uses `git diff --exit-code --staged` to skip if no changes.
- Recommendations: Add SPARQL syntax validation before committing. Consider using a PR-based workflow instead of direct push. The `git add .` on line 28 stages ALL files, not just generated `.rq` files, which could accidentally commit unintended files.

**`git add .` in CI is overly broad:**
- Risk: The CI runs `git add .` which stages everything in the working directory, not just the generated `.rq` files.
- Files: `.github/workflows/extractRQs.yml` (line 28)
- Current mitigation: The checkout should only contain repo files, but any CI artifact or temp file could be committed.
- Recommendations: Replace `git add .` with `git add '*.rq'` or use `git add` targeting specific generated files.

## Performance Bottlenecks

**Federated queries with no timeout or result limits:**
- Problem: Several queries use `SERVICE` clauses to federate across external SPARQL endpoints (IDSM, LIPID MAPS, neXtProt, AOP-Wiki, MolMeDB, MetaNetX, Rhea) without any `LIMIT` or timeout control.
- Files: `H. Chemistry/IDSM_similaritySearch.rq`, `C. Collaborations/smallMolecules_Rhea_IDSM/molecularSimularity_Reactions.rq`, `C. Collaborations/neXtProt/ProteinCellularLocation.rq`, `C. Collaborations/neXtProt/ProteinMitochondria.rq`, `C. Collaborations/MolMeDB/ONEpubchem_MANYpathways.rq`, `C. Collaborations/MolMeDB/SUBSETpathways_ONEpubchem.rq`, `B. Communities/Lipids/LIPIDMAPS_Federated.rq`, `C. Collaborations/MetaNetX/reactionID_mapping.rq`, `C. Collaborations/AOP-Wiki/MetaboliteInAOP-Wiki.rq`
- Cause: External SERVICE endpoints may be slow, down, or return large result sets.
- Improvement path: Add comments documenting expected query time. Consider adding `LIMIT` clauses for exploratory queries.

**Similarity search queries with commented-out cutoffs:**
- Problem: `C. Collaborations/smallMolecules_Rhea_IDSM/molecularSimularity_Reactions.rq` has `sachem:cutoff` lines commented out (lines 31, 36), meaning the similarity search returns ALL results with no threshold, potentially returning massive result sets.
- Files: `C. Collaborations/smallMolecules_Rhea_IDSM/molecularSimularity_Reactions.rq` (lines 31, 36)
- Cause: Cutoff was disabled for testing and never re-enabled.
- Improvement path: Uncomment the cutoff lines or set an appropriate default.

## Fragile Areas

**Hardcoded pathway identifiers in "general" example queries:**
- Files: `D. General/GenesofPathway.rq` (hardcoded `WP1560`), `D. General/MetabolitesofPathway.rq` (hardcoded `WP1560`), `D. General/OntologyofPathway.rq` (hardcoded `WP1560`), `D. General/InteractionsofPathway.rq` (hardcoded `WP1425`), `H. Chemistry/IDSM_similaritySearch.rq` (hardcoded `WP4225`), `C. Collaborations/smallMolecules_Rhea_IDSM/molecularSimularity_Reactions.rq` (hardcoded `WP4225`), `C. Collaborations/MetaNetX/reactionID_mapping.rq` (hardcoded `WP5275`), `C. Collaborations/MolMeDB/SUBSETpathways_ONEpubchem.rq` (hardcoded `WP4224`, `WP4225`, `WP4571`), `E. Literature/referencesForInteraction.rq` (hardcoded `WP5200`), `E. Literature/referencesForSpecificInteraction.rq` (hardcoded `WP5200`), `E. Literature/allReferencesForInteraction.rq` (hardcoded `WP5200`), `J. Authors/authorsOfAPathway.rq` (hardcoded `WP4846`)
- Why fragile: If any of these pathways are removed or renamed in WikiPathways, the example queries return empty results with no indication of why.
- Safe modification: Use `VALUES` clauses with comments indicating the ID is an example. Some queries already do this well (e.g., `GenesofPathway.rq` has `#Replace "WP1560" with WP ID of interest`), but the approach is inconsistent.
- Test coverage: No validation exists to check whether hardcoded pathway IDs still exist in the endpoint.

**Hardcoded `substr` offsets for IRI parsing:**
- Files: `H. Chemistry/IDSM_similaritySearch.rq` (line 11: `substr(str(?chebioSrc),32)`), `A. Metadata/datasources/WPforChemSpider.rq` (`fn:substring(?csId,36)`), `A. Metadata/datasources/WPforHMDB.rq` (`fn:substring(?hmdbId,29)`), `A. Metadata/datasources/WPforNCBI.rq` (`fn:substring(?ncbiGeneId,33)`), and similar
- Why fragile: The numeric offsets (29, 32, 33, 34, 36, 37, 46) are hardcoded to specific IRI base lengths. If identifier.org or any data source changes their URL scheme, these break silently (returning truncated or shifted strings).
- Safe modification: Use `REPLACE` or `STRAFTER` functions which are more robust, e.g., `STRAFTER(STR(?hmdbId), "http://identifiers.org/hmdb/")`.

**Spaces in directory and file names:**
- Files: `B. Communities/CIRM Stem Cell Pathways/`, `B. Communities/Inborn Errors of Metabolism/`, `I. DirectedSmallMoleculesNetwork (DSMN)/`, and all files within containing spaces in their names
- Why fragile: Spaces and parentheses in paths cause issues with shell scripts, CI tools, and URL encoding. The CI workflow must handle these carefully. Any new tooling (linting, testing) must quote all paths.
- Safe modification: Renaming would break the Snorql UI loading mechanism. Document the requirement to quote paths in any tooling.

## Scaling Limits

**No automated testing of query validity:**
- Current capacity: 90 queries, manually verified.
- Limit: As queries grow in number, there is no way to verify they parse correctly or return expected results.
- Scaling path: Add a CI step that parses each `.rq` file with a SPARQL parser (e.g., `rdflib` or Apache Jena's `arq --syntax`) to catch syntax errors before deployment.

## Dependencies at Risk

**External federated SPARQL endpoints:**
- Risk: Nine queries depend on external SPARQL endpoints (IDSM, LIPID MAPS, neXtProt, AOP-Wiki, MolMeDB, MetaNetX) that may change URLs, go offline, or modify their schemas without notice.
- Impact: Federated queries silently return empty or incorrect results.
- Migration plan: No alternative exists for federation. Document known endpoint URLs and monitor availability. Consider caching results for critical queries.

**Blazegraph-specific features:**
- Risk: The WikiPathways endpoint uses Blazegraph, and several queries rely on Blazegraph extensions (`fn:substring`, implicit prefix registration). Blazegraph is no longer actively maintained.
- Impact: Migration to another triplestore would require updating these queries.
- Migration plan: Convert `fn:substring` to standard SPARQL `SUBSTR`. Add explicit PREFIX declarations to all queries.

## Missing Critical Features

**No query validation or linting in CI:**
- Problem: The CI pipeline (`scripts/transformDotTtlToDotSparql.py`) only extracts SPARQL from TTL files. It does not validate that any `.rq` file (generated or hand-written) contains valid SPARQL syntax.
- Blocks: Cannot catch syntax errors before they reach the Snorql UI.

**No README or inline documentation for most queries:**
- Problem: The root `README.md` is a single line. Individual query files have no consistent documentation pattern. Some have inline SPARQL comments, most have none.
- Blocks: New contributors cannot understand query purpose or expected results without reading the SPARQL and understanding the WikiPathways data model.

## Test Coverage Gaps

**No tests exist for any queries:**
- What's not tested: All 90 SPARQL queries have zero automated testing -- no syntax validation, no smoke tests against the endpoint, no expected-result checks.
- Files: All `.rq` files across all directories.
- Risk: Broken queries (syntax errors, wrong prefixes, deprecated predicates) are only discovered when a user runs them manually.
- Priority: High. At minimum, add SPARQL syntax parsing validation in CI for all `.rq` files.

**CI script has no error handling:**
- What's not tested: `scripts/transformDotTtlToDotSparql.py` has no try/except blocks. If a `.ttl` file is malformed, the script crashes and the CI fails silently without helpful output.
- Files: `scripts/transformDotTtlToDotSparql.py`
- Risk: A typo in a `.ttl` file causes the entire extraction pipeline to fail with a Python traceback.
- Priority: Medium. Add error handling with descriptive messages per file.

---

*Concerns audit: 2026-03-06*
