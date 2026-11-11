#!/usr/bin/env python3
"""One-off migration: turn the .rq example queries into .ttl example files.

Kept for the record of how the .ttl files were made; after the migration the
.ttl files are edited by hand (see AUTHORING.md) and this script is not run again.

For every .rq file with a comment header (# title, # category, # description,
# param) it writes a .ttl file next to it, in the format checked by Snorql-UI's
tools/examples/snorql_examples.py:

- the identifier WPQnnn takes the number the query already has in
  BiGCAT-UM/sparql-examples (scripts/wikipathways/sources.tsv), so the two map 1:1;
  queries without a number there get the next free numbers;
- every {{param}} placeholder becomes a query variable, bound to the default in a
  VALUES block in the innermost group where the parameter is used, so the query
  is valid SPARQL that runs as it is; the parameter itself becomes a sh:Parameter;
- PREFIX lines that Virtuoso does not need but other SPARQL engines do are added;
- created, creator and contributors come from the git history of the .rq file
  (which in most cases starts with the 2020 restructure of this repository);
- prov:wasDerivedFrom points at the .rq file at the commit it was migrated from,
  and snorql:alias keeps the old path, so old ?example=<path>.rq links still work.

It also imports the examples that exist only in BiGCAT-UM/sparql-examples (written
from the WikiPathways website pages), so this repository holds every WPQ example.

Usage, from the repository root:

    python scripts/migrate_rq_to_ttl.py --bigcat ../sparql-examples [--check]
"""

import argparse
import csv
import pathlib
import re
import subprocess
import sys
import urllib.parse

from rdflib import Graph, Namespace
from rdflib.namespace import RDFS, DCTERMS

REPO = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://sparql.wikipathways.org/.well-known/sparql-examples/"
TARGET = "https://sparql.wikipathways.org/sparql"
LICENSE = "https://www.gnu.org/licenses/gpl-3.0.html"
SOURCE_BASE = "https://github.com/wikipathways/SPARQLQueries/blob/"
BIGCAT_BASE = "https://github.com/BiGCAT-UM/sparql-examples/blob/"

SH = Namespace("http://www.w3.org/ns/shacl#")
SCHEMA = Namespace("https://schema.org/")
SPEX = Namespace("https://purl.expasy.org/sparql-examples/ontology#")
CITO = Namespace("http://purl.org/spar/cito/")

MARVIN = "https://orcid.org/0000-0003-2230-0840"
DENISE = "https://orcid.org/0000-0001-8449-1318"
EGON = "https://orcid.org/0000-0001-7542-0286"
LAURENT = "https://github.com/laurent2207"
WP_TEAM = "https://www.wikipathways.org/"
AUTHORS = {
    "Marvin Martens": MARVIN, "marvinm2": MARVIN,
    "De": DENISE, "Denise Slenter": DENISE, "DeniseSl22": DENISE,
    "Egon Willighagen": EGON, "egonw": EGON,
    "Laurent Winckers": LAURENT,
}
BOTS = {"GitHub Action", "github-actions[bot]"}

# Folder -> category (the most specific one). The tree in the query editor used to
# be the folder tree; these keep the same grouping.
FOLDER_CATEGORY = {
    "A. Metadata": "Metadata",
    "A. Metadata/datacounts": "DataCounts",
    "A. Metadata/species": "Species",
    "A. Metadata/datasources": "DataSources",
    "B. Communities": "Communities",
    "B. Communities/Inborn Errors of Metabolism": "InbornErrorsOfMetabolism",
    "B. Communities/Lipids": "Lipids",
    "B. Communities/Reactome": "Reactome",
    "C. Collaborations/AOP-Wiki": "AOPWiki",
    "C. Collaborations/MetaNetX": "MetaNetX",
    "C. Collaborations/MolMeDB": "MolMeDB",
    "C. Collaborations/neXtProt": "neXtProt",
    "C. Collaborations/smallMolecules_Rhea_IDSM": "RheaIDSM",
    "D. General": "General",
    "E. Literature": "Literature",
    "F. Datadump": "DataExport",
    "G. Curation": "Curation",
    "H. Chemistry": "Chemistry",
    "I. DirectedSmallMoleculesNetwork (DSMN)": "DSMN",
    "J. Authors": "Authors",
    "K. Metabolites": "Metabolites",
}

# Extra keywords per folder, on top of the category (as in BiGCaT's rq2ttl.py).
FOLDER_KEYWORDS = {
    "A. Metadata/datacounts": ["counts"],
    "A. Metadata/species": ["organism"],
    "B. Communities/Inborn Errors of Metabolism": ["inborn errors of metabolism", "metabolism"],
    "B. Communities/Lipids": ["lipids", "LIPID MAPS"],
    "B. Communities/Reactome": ["Reactome"],
    "C. Collaborations/AOP-Wiki": ["AOP-Wiki", "metabolite"],
    "C. Collaborations/MetaNetX": ["MetaNetX", "reaction"],
    "C. Collaborations/MolMeDB": ["MolMeDB", "PubChem"],
    "C. Collaborations/neXtProt": ["neXtProt", "protein"],
    "C. Collaborations/smallMolecules_Rhea_IDSM": ["Rhea", "IDSM", "reaction"],
    "I. DirectedSmallMoleculesNetwork (DSMN)": ["directed small molecules network"],
}

# Parameters that the editor gave autocomplete by their name only.
LEGACY_AUTOCOMPLETE = {"pathwayId": "pathway", "species": "species"}

# Queries whose endpoint is gone: kept as deprecated examples so links still resolve.
DEPRECATED = {
    "C. Collaborations/neXtProt/ProteinCellularLocation.rq":
        "The neXtProt SPARQL endpoint has been archived (it redirects to expasy.org/archives/nextprot), "
        "so this query no longer works.",
    "C. Collaborations/neXtProt/ProteinMitochondria.rq":
        "The neXtProt SPARQL endpoint has been archived (it redirects to expasy.org/archives/nextprot), "
        "so this query no longer works.",
}

# Queries where Virtuoso answers differently depending on where the VALUES block
# sits: here only a block at the end of the group returns the same rows as the
# old constant did (both forms miss some valid rows; that is a Virtuoso issue).
VALUES_AT_END = {
    "I. DirectedSmallMoleculesNetwork (DSMN)/extracting protein titles and identifiers for metabolic reactions.rq",
}

# Examples that exist only in BiGCAT-UM/sparql-examples: number -> (path here, category).
IMPORTS = {
    "005": ("D. General/PathwayCountPerDisease.ttl", "General"),
    "006": ("A. Metadata/species/SpeciesWithIRIs.ttl", "Species"),
    "007": ("A. Metadata/species/PathwaysAndSpecies.ttl", "Species"),
    "010": ("A. Metadata/HomologyConvertedPathways.ttl", "Metadata"),
    "065": ("D. General/PathwaysWithGene.ttl", "General"),
    "066": ("D. General/GroupsAndComplexesWithGene.ttl", "General"),
    "067": ("A. Metadata/datacounts/PathwayCountPerOntologyTerm.ttl", "DataCounts"),
    "068": ("B. Communities/PathwayCountPerCurationTag.ttl", "Communities"),
    "069": ("D. General/PathwaysWithOntologyTerm.ttl", "General"),
    "070": ("A. Metadata/species/MetaboliteCountPerSpecies.ttl", "Species"),
    "071": ("D. General/InteractionsOfDataNode.ttl", "General"),
    "072": ("A. Metadata/datasources/AllDataSources.ttl", "DataSources"),
    "073": ("A. Metadata/datasources/EntryCountPerDataSource.ttl", "DataSources"),
    "074": ("H. Chemistry/ChEMBLCompoundsAndPathways.ttl", "Chemistry"),
    "075": ("H. Chemistry/MetabolitesWithInChIKeysFromWikidata.ttl", "Chemistry"),
    "076": ("K. Metabolites/AllMetabolites.ttl", "Metabolites"),
    "077": ("K. Metabolites/MetabolitesInZebrafishPathways.ttl", "Metabolites"),
    "078": ("K. Metabolites/MetaboliteIdentifierCountPerDataSource.ttl", "Metabolites"),
    "079": ("K. Metabolites/MetabolitesWithKEGGIdentifier.ttl", "Metabolites"),
    "080": ("K. Metabolites/HumanMetabolome.ttl", "Metabolites"),
    "081": ("K. Metabolites/PathwaysWithMostMetabolites.ttl", "Metabolites"),
    "082": ("K. Metabolites/MetabolitesInMostPathways.ttl", "Metabolites"),
    "083": ("K. Metabolites/EnzymaticReactionsBetweenMetabolites.ttl", "Metabolites"),
}

HEADER_FIELD = re.compile(r"^#\s*(title|category|description|keywords|param):\s?(.*)$")

PREFIXES = """@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix param: <https://w3id.org/snorql/param#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix schema: <https://schema.org/> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix snorql: <https://w3id.org/snorql/ns#> .
@prefix spex: <https://purl.expasy.org/sparql-examples/ontology#> .
@prefix wpcat: <https://sparql.wikipathways.org/.well-known/sparql-examples/category/> .
@prefix wpq: <https://sparql.wikipathways.org/.well-known/sparql-examples/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
"""


class MigrationError(Exception):
    pass


def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise MigrationError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


# ---------------------------------------------------------------- query text

def mask(query):
    """Same-length copy of the query with comments, strings and IRIs blanked out."""
    out = list(query)
    i, n = 0, len(query)

    def blank(a, b):
        for k in range(a, b):
            if out[k] != "\n":
                out[k] = " "
    while i < n:
        c = query[i]
        if c == "#":
            j = query.find("\n", i)
            j = n if j < 0 else j
            blank(i, j)
            i = j
        elif c == "<":
            j = query.find(">", i)
            if j > 0 and not re.search(r"\s", query[i:j]):
                blank(i, j + 1)
                i = j + 1
            else:
                i += 1
        elif c in "\"'":
            quote = query[i:i + 3] if query[i:i + 3] in ('"""', "'''") else c
            j = i + len(quote)
            while j < n and query[j:j + len(quote)] != quote:
                j += 2 if query[j] == "\\" else 1
            blank(i, min(n, j + len(quote)))
            i = j + len(quote)
        else:
            i += 1
    return "".join(out)


def brace_stack(code, pos):
    """Positions of the '{' that are open at pos (outermost first)."""
    stack = []
    for i, c in enumerate(code[:pos]):
        if c == "{":
            stack.append(i)
        elif c == "}" and stack:
            stack.pop()
    return stack


def is_subquery(code, brace):
    return re.match(r"\{\s*SELECT\b", code[brace:], re.I) is not None


def used_prefixes(query):
    code = mask(query)
    code = re.sub(r"(?im)^\s*PREFIX\s+[\w.-]*:\s*", " ", code)
    names = re.findall(r"(?<![\w?$.:-])([A-Za-z][\w.-]*)?:(?=[\w%(\\]|\s|[;,.)\]}]|$)", code)
    return {n for n in names}


def declared_prefixes(query):
    return {m.group(1): m.group(2) for m in re.finditer(r"(?im)^\s*PREFIX\s+([\w.-]*)\s*:\s*<([^>]*)>", query)}


def add_prefixes(body, namespaces, where):
    missing = sorted(used_prefixes(body) - set(declared_prefixes(body)))
    unknown = [p for p in missing if p not in namespaces]
    if unknown:
        raise MigrationError(f"{where}: prefixes not known: {', '.join(unknown)}")
    prologue = "".join(f"PREFIX {p}: <{namespaces[p]}>\n" for p in missing)
    if prologue and not re.match(r"(?i)\s*PREFIX\b", body):
        prologue += "\n"
    return (prologue + body).strip() + "\n"


def encode_value(value):
    return urllib.parse.quote(value, safe="-_.!~*'()")


def placeholder_terms(body, name, namespaces):
    """Every term holding {{name}}: list of (start, end, kind, template)."""
    terms = []
    ph = "{{" + name + "}}"
    for m in re.finditer(re.escape(ph), body):
        s, e = m.start(), m.end()
        # Inside a string literal "...": the whole literal must be the placeholder.
        if body[s - 1:s] == '"' and body[e:e + 1] == '"':
            if body[e + 1:e + 2] in ("@", "^"):
                raise MigrationError(f"{{{{{name}}}}}: literal with a language tag or datatype")
            terms.append((s - 1, e + 1, "literal", None))
            continue
        # Inside an IRI <...{{name}}...>.
        lt = body.rfind("<", 0, s)
        gt = body.find(">", e)
        if lt >= 0 and gt >= 0 and not re.search(r"[\s<>]", body[lt + 1:s] + body[e:gt]):
            template = body[lt + 1:s] + "{value}" + body[e:gt]
            terms.append((lt, gt + 1, "iri", template))
            continue
        # A prefixed name pfx:local{{name}}rest.
        pm = re.search(r"([A-Za-z][\w.-]*)?:([\w.%-]*)$", body[:s])
        if pm:
            rest = re.match(r"[\w.%-]*", body[e:]).group(0)
            prefix = pm.group(1) or ""
            ns = declared_prefixes(body).get(prefix) or namespaces.get(prefix)
            if ns is None:
                raise MigrationError(f"{{{{{name}}}}}: unknown prefix {prefix}:")
            template = ns + pm.group(2) + "{value}" + rest
            terms.append((pm.start(), e + len(rest), "iri", template))
            continue
        raise MigrationError(f"{{{{{name}}}}} is not inside a literal, an IRI or a prefixed name")
    return terms


def turn_into_values(body, params, namespaces, where, at_end=False):
    """Replace each {{param}} by ?param and bind it in a VALUES block. Returns (body, kinds)."""
    kinds = {}
    for name, _, default, _ in params:
        terms = placeholder_terms(body, name, namespaces)
        if not terms:
            raise MigrationError(f"{where}: parameter {name} is not used in the query")
        shapes = {(k, t) for _, _, k, t in terms}
        if len(shapes) != 1:
            raise MigrationError(f"{where}: parameter {name} is used in different ways: {shapes}")
        kind, template = shapes.pop()
        if kind == "literal":
            value_term = '"' + default.replace("\\", "\\\\").replace('"', '\\"') + '"'
        else:
            value_term = "<" + template.replace("{value}", encode_value(default)) + ">"
        # Already the only value of a VALUES block: keep that block and its variable.
        if len(terms) == 1:
            s, e, _, _ = terms[0]
            m = re.search(r"(?i)\bVALUES\s+[?$](\w+)\s*\{\s*$", body[:s])
            if m and re.match(r"\s*\}", body[e:]):
                kinds[name] = (kind, template, m.group(1))
                body = body[:s] + value_term + body[e:]
                continue
        kinds[name] = (kind, template, None)
        if re.search(r"[?$]" + re.escape(name) + r"\b", body):
            raise MigrationError(f"{where}: the query already has a variable ?{name}")
        # Replace from the end so earlier offsets stay valid; remember the new offsets.
        offsets = []
        for s, e, _, _ in sorted(terms, reverse=True):
            body = body[:s] + "?" + name + body[e:]
            offsets = [o - (e - s) + len(name) + 1 for o in offsets]
            offsets.append(s)
        code = mask(body)
        stacks = [brace_stack(code, o) for o in offsets]
        common = []
        for level in zip(*stacks):
            if len(set(level)) != 1:
                break
            common.append(level[0])
        if not common:
            raise MigrationError(f"{where}: {name} is used outside any group")
        group = common[-1]
        for st in stacks:
            for b in st[len(common):]:
                if is_subquery(code, b):
                    raise MigrationError(f"{where}: {name} is used inside a subquery below its common group")
        insert = f"VALUES ?{name} {{ {value_term} }}"
        # When every use is directly in that group, put the block just before the
        # statement with the first use: Virtuoso rejects a VALUES block before a
        # SERVICE call in the same group ("Unsupported combination of subqueries
        # and service invocations"), but accepts it after one.
        if at_end:
            close = group + 1
            depth = 1
            while depth:
                depth += {"{": 1, "}": -1}.get(code[close], 0)
                close += 1
            close -= 1
            line_start = body.rfind("\n", 0, close) + 1
            indent = re.match(r"[ \t]*", body[body.rfind("\n", 0, group) + 1:]).group(0)
            body = body[:line_start] + indent + insert + "\n" + body[line_start:]
            continue
        if all(len(st) == len(common) for st in stacks):
            first = min(offsets)
            k = first
            while k > group + 1 and not (code[k - 1] in "{}" or (code[k - 1] == "." and code[k:k + 1].isspace())):
                k -= 1
            stmt = k + (len(code[k:first]) - len(code[k:first].lstrip()))
            line_start = body.rfind("\n", 0, stmt) + 1
            if stmt > group + 1 and not body[line_start:stmt].strip():
                indent = body[line_start:stmt]
                body = body[:line_start] + indent + insert + "\n" + body[line_start:]
                continue
        line_start = body.rfind("\n", 0, group) + 1
        after = body[group + 1:]
        nl = re.match(r"[ \t]*\n([ \t]*)", after)
        if nl:
            indent = nl.group(1) or (re.match(r"[ \t]*", body[line_start:]).group(0) + "  ")
            body = body[:group + 1] + "\n" + indent + insert + body[group + 1:]
        else:
            body = body[:group + 1] + " " + insert + body[group + 1:]
    return body, kinds


# ---------------------------------------------------------------- turtle

def turtle_string(text):
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def turtle_long_string(text):
    text = text.replace("\\", "\\\\")
    text = re.sub(r'"(?=""|"*$)', r'\\"', text)
    return '"""' + text + '"""'


def query_form(query):
    code = mask(query)
    code = re.sub(r"(?im)^\s*(PREFIX\s+[\w.-]*:|BASE)\s*", " ", code)
    m = re.search(r"(?i)\b(SELECT|ASK|CONSTRUCT|DESCRIBE)\b", code)
    if not m:
        raise MigrationError("cannot find the query form")
    return m.group(1).lower()


def services(query):
    code = re.sub(r"#[^\n]*", "", query)
    return sorted(set(re.findall(r"(?i)\bSERVICE\s+(?:SILENT\s+)?<([^>]+)>", code)))


FORMS = {
    "select": ("sh:SPARQLSelectExecutable", "sh:select"),
    "ask": ("sh:SPARQLAskExecutable", "sh:ask"),
    "construct": ("sh:SPARQLConstructExecutable", "sh:construct"),
    "describe": ("spex:SPARQLDescribeExecutable", "spex:describe"),
}


def render(ex):
    """Turtle for one example (a dict)."""
    cls, prop = FORMS[query_form(ex["query"])]
    L = [PREFIXES, f"wpq:{ex['id']} a sh:SPARQLExecutable, {cls} ;"]
    add = L.append
    add(f'    dcterms:identifier "{ex["id"]}" ;')
    add(f"    rdfs:label {turtle_string(ex['label'])}@en ;")
    add(f"    rdfs:comment {turtle_string(ex['comment'])}@en ;")
    add('    schema:version "1.0.0" ;')
    add(f'    dcterms:created "{ex["created"]}"^^xsd:date ;')
    add("    dcterms:creator " + ", ".join(f"<{c}>" for c in ex["creators"]) + " ;")
    if ex["contributors"]:
        add("    dcterms:contributor " + ", ".join(f"<{c}>" for c in ex["contributors"]) + " ;")
    add(f"    dcterms:license <{LICENSE}> ;")
    add(f"    dcterms:subject wpcat:{ex['category']} ;")
    if ex["keywords"]:
        add("    schema:keywords " + ", ".join(turtle_string(k) for k in ex["keywords"]) + " ;")
    add(f"    schema:target <{TARGET}> ;")
    for s in services(ex["query"]):
        add(f"    spex:federatesWith <{s}> ;")
    for a in ex.get("aliases", []):
        add(f"    snorql:alias {turtle_string(a)} ;")
    for d in ex["derived"]:
        add(f"    prov:wasDerivedFrom <{d}> ;")
    if ex.get("deprecated"):
        add("    owl:deprecated true ;")
    else:
        add("    snorql:expect [ snorql:minResults 1 ] ;")
    for order, p in enumerate(ex["params"], 1):
        add("    sh:parameter [")
        add("        a sh:Parameter ;")
        add(f"        sh:path param:{p['name']} ;")
        add(f"        sh:name {turtle_string(p['label'])} ;")
        add(f"        sh:defaultValue {turtle_string(p['default'])} ;")
        if p.get("variable"):
            add(f"        snorql:variable {turtle_string(p['variable'])} ;")
        if p["kind"] == "iri":
            add("        sh:nodeKind sh:IRI ;")
            add(f"        snorql:valueTemplate {turtle_string(p['template'])} ;")
        else:
            add("        sh:datatype xsd:string ;")
        if p.get("autocomplete"):
            add(f"        snorql:autocomplete {turtle_string(p['autocomplete'])} ;")
        for k, o in enumerate(p.get("options") or [], 1):
            add(f"        snorql:option [ rdf:value {turtle_string(o[0])} ; rdfs:label {turtle_string(o[1])} ;"
                f" sh:order {k} ] ;")
        add(f"        sh:order {order}")
        add("    ] ;")
    add(f"    {prop} {turtle_long_string(ex['query'].rstrip())} .")
    ttl = "\n".join(L) + "\n"
    g = Graph()
    g.parse(data=ttl, format="turtle")
    s = next(g.subjects(DCTERMS.identifier, None))
    found = [str(o) for p, o in g.predicate_objects(s) if str(p).endswith(("#select", "#ask", "#construct", "#describe"))]
    if found != [ex["query"].rstrip()]:
        raise MigrationError(f"{ex['id']}: the query does not survive the Turtle round trip")
    return ttl


# ---------------------------------------------------------------- sources

class RqFile:
    def __init__(self, rel):
        self.rel = rel
        self.title, self.category, self.description, self.keywords, self.params = "", "", [], [], []
        text = (REPO / rel).read_text(encoding="utf-8").replace("\r\n", "\n")
        lines = text.split("\n")
        n, field = 0, None
        while n < len(lines) and lines[n].startswith("#"):
            m = HEADER_FIELD.match(lines[n])
            if m:
                field, value = m.group(1), m.group(2).strip()
                if field == "title":
                    self.title = value
                elif field == "category":
                    self.category = value
                elif field == "description":
                    self.description.append(value)
                elif field == "keywords":
                    self.keywords += [k.strip() for k in value.split(",") if k.strip()]
                elif field == "param":
                    parts = [p.strip() for p in value.split("|")]
                    parts += [""] * (4 - len(parts))
                    self.params.append(tuple(parts[:4]))
            elif field == "description" and lines[n].startswith("#"):
                self.description.append(lines[n].lstrip("#").strip())
            n += 1
        self.body = "\n".join(lines[n:]).strip("\n")


def history(paths):
    """(created date, [author names] oldest first) over the history of these files."""
    log = []
    for rel in paths:
        if not (REPO / rel).exists():
            continue
        out = git(REPO, "log", "--follow", "--format=%cs\t%an", "--", rel)
        log += [tuple(line.split("\t", 1)) for line in out.splitlines() if line]
    log.sort()
    authors = []
    for _, a in log:
        if a not in BOTS and a not in authors:
            authors.append(a)
    return (log[0][0] if log else None), authors


def people(authors):
    iris = []
    for a in authors:
        if a not in AUTHORS:
            raise MigrationError(f"no IRI for git author {a!r}; add it to AUTHORS")
        if AUTHORS[a] not in iris:
            iris.append(AUTHORS[a])
    return iris


def keywords_for(rq):
    words = [rq.category.lower() if rq.category != "DSMN" else rq.category]
    folder = str(pathlib.PurePosixPath(rq.rel).parent)
    words += FOLDER_KEYWORDS.get(folder, []) + rq.keywords
    seen, out = set(), []
    for w in words:
        if w and w.lower() not in seen:
            seen.add(w.lower())
            out.append(w)
    return out


def load_namespaces(bigcat):
    g = Graph()
    g.parse(bigcat / "examples" / "WikiPathways" / "prefixes.ttl", format="turtle")
    return {str(p): str(ns) for _, d in g.subject_objects(SH.declare)
            for p in g.objects(d, SH.prefix) for ns in g.objects(d, SH.namespace)}


def from_rq(ident, rel, namespaces):
    rq = RqFile(rel)
    folder = str(pathlib.PurePosixPath(rel).parent)
    if folder not in FOLDER_CATEGORY:
        raise MigrationError(f"{rel}: no category for folder {folder}")
    body, kinds = (turn_into_values(rq.body, rq.params, namespaces, rel, rel in VALUES_AT_END)
                   if rq.params else (rq.body, {}))
    query = add_prefixes(body, namespaces, rel)
    ttl_rel = re.sub(r"\.rq$", ".ttl", rel)
    created, authors = history([rel, ttl_rel])
    persons = people(authors)
    sha = git(REPO, "log", "-1", "--format=%H", "--", rel).strip()
    params = []
    for name, ptype, default, label in rq.params:
        kind, template, variable = kinds[name]
        p = {"name": name, "label": label, "default": default, "kind": kind, "template": template,
             "variable": variable}
        if ptype.startswith("enum:"):
            opts = []
            for o in ptype[5:].split(","):
                o = o.strip()
                value, _, olabel = o.partition("=")
                opts.append((value, olabel or value))
            p["options"] = opts
        elif ptype.startswith("autocomplete:"):
            p["autocomplete"] = ptype[13:].strip()
        elif name in LEGACY_AUTOCOMPLETE:
            p["autocomplete"] = LEGACY_AUTOCOMPLETE[name]
        params.append(p)
    comment = " ".join(d for d in rq.description if d)
    deprecated = rel in DEPRECATED
    if deprecated:
        comment += " " + DEPRECATED[rel]
    return {
        "id": ident, "path": ttl_rel, "label": rq.title, "comment": comment, "created": created,
        "creators": persons[:1], "contributors": persons[1:],
        "category": FOLDER_CATEGORY[folder], "keywords": keywords_for(rq),
        "aliases": [rel], "derived": [SOURCE_BASE + sha + "/" + urllib.parse.quote(rel)],
        "params": params, "query": query, "deprecated": deprecated,
    }


def from_bigcat(number, bigcat):
    rel_here, category = IMPORTS[number]
    rel = f"examples/WikiPathways/{number}.ttl"
    g = Graph()
    g.parse(bigcat / rel, format="turtle")
    s = next(g.subjects(SCHEMA.target, None))
    query = None
    for p in (SH.select, SH.ask, SH.construct, SPEX.describe):
        query = query or g.value(s, p)
    out = git(bigcat, "log", "--follow", "--format=%cs\t%an\t%H", "--", rel).splitlines()
    created, first_author, _ = out[-1].split("\t")
    sha = out[0].split("\t")[2]
    derived = [BIGCAT_BASE + sha + "/" + rel]
    derived += [str(o) for o in g.objects(s, CITO.usesMethodIn)]
    if int(number) >= 65:
        # Written on 2026-11-10 from the queries on the WikiPathways website pages.
        creators, contributors = [WP_TEAM], [AUTHORS[first_author]]
    else:
        creators, contributors = [AUTHORS[first_author]], []
    return {
        "id": "WPQ" + number, "path": rel_here, "label": str(g.value(s, RDFS.label)),
        "comment": " ".join(str(c) for c in g.objects(s, RDFS.comment)), "created": created,
        "creators": creators, "contributors": contributors, "category": category,
        "keywords": sorted({str(k) for k in g.objects(s, SCHEMA.keywords)}, key=str.casefold),
        "aliases": [], "derived": derived, "params": [], "query": str(query).strip() + "\n",
        "deprecated": False,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--bigcat", required=True, type=pathlib.Path, help="checkout of BiGCAT-UM/sparql-examples")
    ap.add_argument("--check", action="store_true", help="write nothing")
    args = ap.parse_args()
    bigcat = args.bigcat.resolve()
    namespaces = load_namespaces(bigcat)

    with open(bigcat / "scripts" / "wikipathways" / "sources.tsv", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    numbers = {r["source"]: r["id"] for r in rows if r["kind"] in ("rq", "same") and r["source"].endswith(".rq")}
    used = {int(r["id"]) for r in rows if r["id"].isdigit()}
    rq_files = sorted((p.relative_to(REPO).as_posix() for p in REPO.rglob("*.rq")
                       if p.relative_to(REPO).parts[0] not in {".git", "scripts"}), key=str.casefold)
    examples, errors = [], []
    for rel in rq_files:
        if rel not in numbers:
            numbers[rel] = f"{max(used) + 1:03d}"
            used.add(max(used) + 1)
            print(f"new number {numbers[rel]} for {rel}")
        try:
            examples.append(from_rq("WPQ" + numbers[rel], rel, namespaces))
        except MigrationError as e:
            errors.append(str(e))
    for number in sorted(IMPORTS):
        examples.append(from_bigcat(number, bigcat))
    if errors:
        for e in errors:
            print("ERROR: " + e, file=sys.stderr)
        sys.exit(1)

    ids = [e["id"] for e in examples]
    assert len(ids) == len(set(ids)), "duplicate identifiers"
    for ex in examples:
        ttl = render(ex)
        if not args.check:
            path = REPO / ex["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(ttl, encoding="utf-8")
    print(f"{len(examples)} examples ({sum(1 for e in examples if e['deprecated'])} deprecated), "
          f"{sum(1 for e in examples if e['params'])} with parameters")


if __name__ == "__main__":
    main()
