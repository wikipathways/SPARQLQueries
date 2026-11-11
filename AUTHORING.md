# Writing and changing example queries

Each example is one Turtle (`.ttl`) file: the SPARQL query plus its metadata, in the
format of [SIB's sparql-examples](https://github.com/sib-swiss/sparql-examples) with a
few extra terms from the [Snorql vocabulary](https://w3id.org/snorql/ns). The query
editor at <https://sparql.wikipathways.org/> reads them (through the published index,
see below), and so can any other tool that understands SIB's format.

## Identifiers

Every example has a permanent identifier, `WPQ` followed by a number (`WPQ036`). Its IRI
is `https://sparql.wikipathways.org/.well-known/sparql-examples/WPQ036`, and links to the
editor use it: `https://sparql.wikipathways.org/?example=WPQ036`.

- The identifier never changes and is never reused. You can rename the file or move it to
  another folder at any time; links keep working.
- For a new example, take the next free number:
  `python <Snorql-UI>/tools/examples/snorql_examples.py next-id` (or look at the highest
  number in use and add one; CI rejects duplicates).
- Folders are only for keeping the files tidy. Where an example appears in the editor's
  tree is set by its category (`dcterms:subject`), see `categories.ttl`.

## Template

```turtle
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix param: <https://w3id.org/snorql/param#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix schema: <https://schema.org/> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix snorql: <https://w3id.org/snorql/ns#> .
@prefix spex: <https://purl.expasy.org/sparql-examples/ontology#> .
@prefix wpcat: <https://sparql.wikipathways.org/.well-known/sparql-examples/category/> .
@prefix wpq: <https://sparql.wikipathways.org/.well-known/sparql-examples/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

wpq:WPQ086 a sh:SPARQLExecutable, sh:SPARQLSelectExecutable ;
    dcterms:identifier "WPQ086" ;
    rdfs:label "Genes of a Pathway"@en ;
    rdfs:comment "Lists all gene products in a given pathway."@en ;
    schema:version "1.0.0" ;
    dcterms:created "2026-11-11"^^xsd:date ;
    dcterms:creator <https://orcid.org/0000-0000-0000-0000> ;
    dcterms:license <https://www.gnu.org/licenses/gpl-3.0.html> ;
    dcterms:subject wpcat:General ;
    schema:keywords "gene", "pathway" ;
    schema:target <https://sparql.wikipathways.org/sparql> ;
    snorql:expect [ snorql:minResults 1 ] ;
    sh:parameter [
        a sh:Parameter ;
        sh:path param:pathwayId ;
        sh:name "Pathway ID" ;
        sh:defaultValue "WP1560" ;
        sh:datatype xsd:string ;
        snorql:autocomplete "pathway" ;
        sh:order 1
    ] ;
    sh:select """PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX wp: <http://vocabularies.wikipathways.org/wp#>

SELECT DISTINCT ?gene ?label WHERE {
  VALUES ?pathwayId { "WP1560" }
  ?pathway a wp:Pathway ; dcterms:identifier ?pathwayId .
  ?gene a wp:GeneProduct ; dcterms:isPartOf ?pathway ; rdfs:label ?label .
}""" .
```

## Fields

| Field | Required | What it holds |
|---|---|---|
| `dcterms:identifier` | yes | `WPQnnn`; the subject IRI must be `wpq:` + the same identifier |
| `rdfs:label` | yes | Title shown in the editor, with `@en` |
| `rdfs:comment` | yes | What the query does and returns, with `@en` |
| `schema:version` | yes | `MAJOR.MINOR.PATCH`, see [Versions](#versions) |
| `dcterms:created` | yes | Date the example was first written |
| `dcterms:creator` | yes | Who wrote it: ORCID IRI, or a profile page if there is no ORCID |
| `dcterms:contributor` | no | Others who changed it |
| `dcterms:license` | yes | The repository's licence, GPL-3.0 |
| `dcterms:subject` | yes | Category from `categories.ttl` (more than one is fine) |
| `schema:target` | yes | The SPARQL endpoint the query is for |
| `sh:select` / `sh:ask` / `sh:construct` / `spex:describe` | yes | The query, with all the PREFIX lines it uses |
| `schema:keywords` | no | Search terms |
| `spex:federatesWith` | if `SERVICE` is used | One per endpoint called with `SERVICE` |
| `schema:educationalLevel` | no | `beginner`, `intermediate` or `advanced` |
| `dcterms:references` | no | Paper or tutorial that explains or uses the query |
| `prov:wasDerivedFrom` | no | Where the query was adapted from |
| `snorql:expect` | no | Expected results with the default values, e.g. `[ snorql:minResults 1 ]`; checked weekly |
| `snorql:alias` | no | Old path of the example, so old `?example=<path>` links keep working |

Every creator and contributor IRI needs a name in `contributors.ttl`. Add yourself there
in the same pull request as your first example.

Inside the `"""..."""` of the query, a backslash must be doubled (`\\d` for a regex `\d`),
and `"""` cannot appear.

## Parameters

A parameter is a value the user can change in the editor (a pathway, a species). The
query must still run as it is, so it binds the variable to the default value in a single
`VALUES` block; the editor replaces the value in that block.

```turtle
    sh:parameter [
        a sh:Parameter ;
        sh:path param:species ;          # name in links (?species=...) and the variable ?species
        sh:name "Species" ;              # label in the editor
        sh:defaultValue "Homo sapiens" ;
        sh:datatype xsd:string ;         # the value is a string ...
        snorql:autocomplete "species" ;  # ... with suggestions from the editor's "species" list
        sh:order 1
    ] ;
```

and in the query `VALUES ?species { "Homo sapiens" }` next to the triple patterns that use
`?species`.

- **IRI values:** use `sh:nodeKind sh:IRI` and a template, e.g.
  `snorql:valueTemplate "https://identifiers.org/wikipathways/{value}"`. The user types
  `WP1560`; the `VALUES` block holds `<https://identifiers.org/wikipathways/WP1560>`.
- **A fixed list:** one `snorql:option [ rdf:value "DataNode" ; rdfs:label "Data Nodes" ; sh:order 1 ]`
  per allowed value (combine with a template for class or property names, e.g.
  `"http://vocabularies.wikipathways.org/wp#{value}"`).
- **A different variable name:** `snorql:variable "pathway"` when the `VALUES` block binds
  `?pathway` but the parameter is called `pathwayId`.
- Names `example`, `ref`, `version`, `endpoint` and `q` are taken by the editor's links.
- Where the `VALUES` block sits matters to Virtuoso: put it next to the patterns that use the
  variable, after any `SERVICE` call in the same group (Virtuoso rejects a `VALUES` block
  before a `SERVICE` call), and inside a subquery when the variable is used there.

## Versions

Each example has its own version. Raise it in every pull request that changes the example;
CI checks this.

- **PATCH** (1.0.0 → 1.0.1): metadata only (title, description, keywords, category, ...).
- **MINOR** (1.0.1 → 1.1.0): the query or its parameters changed, same result columns.
- **MAJOR** (1.1.0 → 2.0.0): the result columns changed, or the query answers a different question.

The editor can show every published version of an example, and a link can pin one:
`?example=WPQ036&version=1.0.0`. Collection releases (tags `vYYYY.MM`) freeze the whole set.

## Removing an example

Don't delete the file: identifiers must keep resolving. Mark it deprecated and say why,
and point to a replacement if there is one:

```turtle
    owl:deprecated true ;
    dcterms:isReplacedBy wpq:WPQ040 ;
```

The editor hides deprecated examples from the tree but still opens them from links, with a
notice.

## Checking your change

CI runs these on every pull request. To run them yourself, with a checkout of
[Snorql-UI](https://github.com/wikipathways/Snorql-UI) next to this one:

```bash
pip install -r ../Snorql-UI/tools/examples/requirements.txt
python ../Snorql-UI/tools/examples/snorql_examples.py check
python ../Snorql-UI/tools/examples/snorql_examples.py versions --base origin/master
python ../Snorql-UI/tools/examples/snorql_examples.py live --only WPQ036   # run against the endpoint
```

## What CI publishes

On every push to `master`, CI rebuilds the `examples-index` branch:

- `index.json`: all examples with their metadata and queries (what the editor loads);
- `history.json` and `versions/<id>/<version>.json`: every published version;
- `sparql-examples.ttl`: all examples in one Turtle file;
- `rq/`: plain `.rq` files with the old comment header, for tools that read those.

Don't edit that branch; it is replaced on every push.
