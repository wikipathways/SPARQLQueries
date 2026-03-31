# SPARQL Queries for WikiPathways

Example SPARQL queries for the [WikiPathways Snorql UI](http://sparql.wikipathways.org/). These queries are loaded automatically to help users explore WikiPathways RDF data and build novel queries.

## Adding a new query

1. **Pick the right directory.** Queries are organized by topic in lettered directories (A-J). Place your `.rq` file in the matching directory.

2. **Add a header.** Every `.rq` file must start with these required header fields:

   ```sparql
   # title: Genes of a Pathway
   # category: General
   # description: Lists all gene products in a given pathway, returning the pathway
   #   identifier and gene product labels.

   SELECT ...
   ```

   - `title` -- short, descriptive name
   - `category` -- must match an entry in `categories.json`
   - `description` -- what the query does (wrap long lines with `#   ` continuation indent)

   See [HEADER_CONVENTIONS.md](HEADER_CONVENTIONS.md) for full details, including optional fields like `keywords` and `param`.

3. **Alternative: TTL format.** You can also write a `.ttl` (Turtle/RDF) file using the SHACL `sh:SPARQLExecutable` pattern. The CI pipeline will auto-generate the corresponding `.rq` file on merge to `master`. If a `.ttl` source exists, do not edit the `.rq` file directly.

## License

[GPLv3](LICENSE)
