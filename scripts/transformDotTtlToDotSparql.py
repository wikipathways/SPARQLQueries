import os
import glob
from rdflib import Graph


def extract_header(filepath):
    """Extract the leading comment-line header block from an .rq file.

    Reads consecutive lines starting with '#' from the top of the file,
    stopping at the first blank line or first non-comment line. Returns
    the header lines joined with a trailing newline (the blank separator),
    or an empty string if no header is found or the file does not exist.
    """
    if not os.path.exists(filepath):
        return ""

    header_lines = []
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            stripped = line.rstrip("\n")
            if stripped.startswith("#"):
                header_lines.append(stripped)
            else:
                break

    if header_lines:
        return "\n".join(header_lines) + "\n"
    return ""


def process_ttl_file(ttl_path):
    """Parse a .ttl file and write the extracted SPARQL to a .rq file.

    If the .rq file already exists and has a comment header block, that
    header is preserved above the regenerated SPARQL content. If the TTL
    contains no SPARQL query, the .rq file is not touched.
    """
    rq_path = ttl_path[:-4] + ".rq"
    fn = os.path.basename(ttl_path)[:-4]
    print("file: " + fn)

    header = extract_header(rq_path)

    g = Graph()
    g.parse(ttl_path)

    knows_query = """prefix sh: <http://www.w3.org/ns/shacl#>
SELECT DISTINCT ?query ?sparql
WHERE {
    ?query sh:select | sh:ask | sh:construct ?sparql .
}"""

    qres = g.query(knows_query)
    sparql_content = ""
    for row in qres:
        sparql_content += str(row.sparql)

    if not sparql_content.strip():
        print(f"  WARNING: No SPARQL found in {ttl_path}, skipping .rq write")
        return

    with open(rq_path, "w", encoding="utf-8") as sparql_file:
        if header:
            sparql_file.write(header + "\n")
        sparql_file.write(sparql_content)


# Path to Turtle files
ttl_files_path = '**/*.ttl'

if __name__ == "__main__":
    # Get the list of .ttl files
    ttl_files = glob.glob(ttl_files_path, recursive=True)

    # Process each Turtle file
    for i in ttl_files:
        process_ttl_file(i)
