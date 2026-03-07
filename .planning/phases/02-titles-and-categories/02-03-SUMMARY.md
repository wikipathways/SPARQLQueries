---
phase: 02-titles-and-categories
plan: 03
subsystem: metadata
tags: [sparql, headers, title, category, snorql]

requires:
  - phase: 01-infrastructure
    provides: "CI header preservation, controlled category vocabulary, header conventions guide"
  - phase: 02-titles-and-categories plan 01
    provides: "Header validation test suite (test_headers.py)"
provides:
  - "All 90 .rq files enriched with title and category headers"
  - "Full test suite passes GREEN (183 tests)"
  - "META-01 and META-02 requirements complete"
affects: [03-descriptions, 04-ci-lint]

tech-stack:
  added: []
  patterns: ["# title: then # category: then blank line then query body"]

key-files:
  created: []
  modified:
    - "C. Collaborations/*/*.rq (7 files)"
    - "D. General/*.rq (4 files)"
    - "E. Literature/*.rq (5 files)"
    - "F. Datadump/*.rq (3 files)"
    - "G. Curation/*.rq (7 files)"
    - "H. Chemistry/*.rq (2 files)"
    - "I. DirectedSmallMoleculesNetwork (DSMN)/*.rq (4 files)"
    - "J. Authors/*.rq (4 files)"

key-decisions:
  - "Removed existing descriptive comments (e.g. #Sorting the metabolites...) and replaced with structured # title: headers"
  - "Used Data Export category for F. Datadump directory (matching categories.json vocabulary)"

patterns-established:
  - "Header enrichment: read SPARQL content to derive accurate title, assign category from directory mapping"

requirements-completed: [META-01, META-02]

duration: 25min
completed: 2026-03-07
---

# Phase 2 Plan 3: Titles and Categories for C-J Directories Summary

**Title and category headers added to all 36 remaining .rq files in directories C through J, completing 100% coverage across all 90 queries with 183 tests GREEN**

## Performance

- **Duration:** 25 min
- **Started:** 2026-03-07T07:17:22Z
- **Completed:** 2026-03-07T07:42:00Z
- **Tasks:** 2
- **Files modified:** 36

## Accomplishments
- All 36 .rq files in directories C-J enriched with `# title:` and `# category:` headers
- Combined with plan 02-02, all 90 .rq files in the repository now have structured headers
- Full test suite passes GREEN: 183 tests including title uniqueness, valid categories, field order, blank line separator
- Zero duplicate titles across all 90 files
- All category values match controlled vocabulary in categories.json

## Task Commits

Each task was committed atomically:

1. **Task 1: Add headers to C-F files (19 files)** - `65e6d8f` (feat)
2. **Task 2: Add headers to G-J files (17 files)** - `9b87668` (feat)

## Files Created/Modified

**C. Collaborations (7 files):**
- `MetaboliteInAOP-Wiki.rq` - Metabolites in AOP-Wiki
- `reactionID_mapping.rq` - MetaNetX Reaction ID Mapping
- `ONEpubchem_MANYpathways.rq` - Pathways for a PubChem Compound (MolMeDB)
- `SUBSETpathways_ONEpubchem.rq` - PubChem Compound in Pathway Subset (MolMeDB)
- `ProteinCellularLocation.rq` - Protein Cellular Location via neXtProt
- `ProteinMitochondria.rq` - Mitochondrial Proteins via neXtProt
- `molecularSimularity_Reactions.rq` - Molecular Similarity Reactions via Rhea and IDSM

**D. General (4 files):**
- `GenesofPathway.rq` - Genes of a Pathway
- `InteractionsofPathway.rq` - Interactions of a Pathway
- `MetabolitesofPathway.rq` - Metabolites of a Pathway
- `OntologyofPathway.rq` - Ontology Terms of a Pathway

**E. Literature (5 files):**
- `allPathwayswithPubMed.rq` - All Pathways with PubMed References
- `allReferencesForInteraction.rq` - All References for an Interaction
- `countRefsPerPW.rq` - Reference Count per Pathway
- `referencesForInteraction.rq` - References for an Interaction
- `referencesForSpecificInteraction.rq` - References for a Specific Interaction

**F. Datadump (3 files):**
- `CyTargetLinkerLinksetInput.rq` - CyTargetLinker Linkset Input
- `dumpOntologyAndPW.rq` - Ontology and Pathway Data Export
- `dumpPWsofSpecies.rq` - Pathways by Species Data Export

**G. Curation (7 files):**
- `countPWsMetabolitesOccurSorted.rq` - Pathways by Metabolite Occurrence Count
- `countPWsWithoutRef.rq` - Count of Pathways Without References
- `MetabolitesDoubleMappingWikidata.rq` - Metabolites with Duplicate Wikidata Mappings
- `MetabolitesNotClassified.rq` - Unclassified Metabolites
- `MetabolitesWithoutLinkWikidata.rq` - Metabolites Without Wikidata Links
- `PWsWithoutDatanodes.rq` - Pathways Without Data Nodes
- `PWsWithoutRef.rq` - Pathways Without References

**H. Chemistry (2 files):**
- `IDSM_similaritySearch.rq` - IDSM Chemical Similarity Search
- `smiles.rq` - SMILES for Metabolites

**I. DirectedSmallMoleculesNetwork (DSMN) (4 files):**
- `controlling duplicate mappings from Wikidata.rq` - Controlling Duplicate Mappings from Wikidata
- `extracting directed metabolic reactions.rq` - Extracting Directed Metabolic Reactions
- `extracting ontologies and references for metabolic reactions.rq` - Extracting Ontologies and References for Metabolic Reactions
- `extracting protein titles and identifiers for metabolic reactions.rq` - Extracting Protein Titles and Identifiers for Metabolic Reactions

**J. Authors (4 files):**
- `authorsOfAPathway.rq` - Authors of a Pathway
- `contributors.rq` - All Contributors
- `firstAuthors.rq` - First Authors of Pathways
- `pathwayCountWithAtLeastXAuthors.rq` - Pathways with Multiple Authors

## Decisions Made
- Removed existing descriptive comments at file tops (e.g., `#Sorting the metabolites...`, `#Pathways without literature references`) and replaced with structured `# title:` headers; original comment content preserved for Phase 3 description work
- Used "Data Export" category for F. Datadump directory per categories.json mapping

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All 90 .rq files have title and category headers -- ready for Phase 3 description enrichment
- Full test suite (183 tests) validates coverage, uniqueness, field order, and blank line separation
- META-01 and META-02 requirements are complete

---
*Phase: 02-titles-and-categories*
*Completed: 2026-03-07*
