# SPARQL Queries for WikiPathways

Example SPARQL queries for the [WikiPathways SPARQL editor](https://sparql.wikipathways.org/).
They help people explore the WikiPathways RDF and start their own queries.

Each example is a Turtle file with the query and its metadata (title, description,
version, creators, category, parameters), in the format of
[SIB's sparql-examples](https://github.com/sib-swiss/sparql-examples). Every example has a
permanent identifier and IRI, for example
[`WPQ036`](https://sparql.wikipathways.org/?example=WPQ036) is
`https://sparql.wikipathways.org/.well-known/sparql-examples/WPQ036`. Files can be moved
and renamed without breaking links.

- [AUTHORING.md](AUTHORING.md): how to write or change an example, and how versions work.
- `categories.ttl`: the categories that make up the editor's tree.
- `contributors.ttl`: names of creators and contributors.
- `collection.ttl`: the collection itself.

On every push to `master`, CI publishes the `examples-index` branch, which the editor
reads; it also holds every past version of every example and plain `.rq` copies.

The examples used to be `.rq` files; the last commit with them is `fed6a2d`, which also has
the scripts that converted them. Old links to an `.rq` path still open the right example, and
the `rq/` folder of the `examples-index` branch has generated `.rq` copies for tools that read
that format.

## License

[GPLv3](LICENSE)
