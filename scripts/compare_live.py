#!/usr/bin/env python3
"""Check that the migrated .ttl examples return what the .rq files returned.

For every .ttl that has an .rq alias (snorql:alias), run the .rq query (its
{{param}} placeholders filled with the defaults, as the query editor did) and
the .ttl query against the endpoint, and compare the result columns and the
rows (as a multiset). Also prints both run times, to spot VALUES blocks that
Virtuoso handles more slowly than the constants they replaced.

Usage, from the repository root:

    python scripts/compare_live.py [--only WPQ036 WPQ061] [--workers 4]
"""

import argparse
import collections
import concurrent.futures
import json
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request

from rdflib import Graph, Namespace
from rdflib.namespace import DCTERMS

REPO = pathlib.Path(__file__).resolve().parent.parent
SH = Namespace("http://www.w3.org/ns/shacl#")
SCHEMA = Namespace("https://schema.org/")
SNORQL = Namespace("https://w3id.org/snorql/ns#")
OWL_DEPRECATED = "http://www.w3.org/2002/07/owl#deprecated"


def run(endpoint, query, timeout):
    data = urllib.parse.urlencode({"query": query}).encode()
    req = urllib.request.Request(endpoint, data=data, headers={
        "Accept": "application/sparql-results+json", "User-Agent": "wikipathways-sparqlqueries-migration-check"})
    start = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        doc = json.loads(r.read().decode("utf-8"))
    secs = time.time() - start
    cols = doc.get("head", {}).get("vars", [])
    rows = collections.Counter(
        json.dumps({k: (v.get("type"), v.get("value"), v.get("datatype"), v.get("xml:lang"))
                    for k, v in b.items()}, sort_keys=True)
        for b in doc.get("results", {}).get("bindings", []))
    return cols, rows, secs


def rq_query(path):
    text = path.read_text(encoding="utf-8")
    defaults = {}
    for m in re.finditer(r"^#\s*param:\s*(.+)$", text, re.M):
        parts = [p.strip() for p in m.group(1).split("|")]
        defaults[parts[0]] = parts[2]
    lines = text.split("\n")
    n = 0
    while n < len(lines) and lines[n].startswith("#"):
        n += 1
    body = "\n".join(lines[n:])
    return re.sub(r"\{\{\s*(\w+)\s*\}\}", lambda m: defaults[m.group(1)], body)


def compare(ttl, timeout):
    g = Graph().parse(ttl, format="turtle")
    s = next(g.subjects(DCTERMS.identifier, None))
    ident = str(g.value(s, DCTERMS.identifier))
    alias = g.value(s, SNORQL.alias)
    if alias is None or any(str(p) == OWL_DEPRECATED for p in g.predicates(s, None)):
        return ident, None
    target = str(g.value(s, SCHEMA.target))
    new_q = str(g.value(s, SH.select))
    old_q = rq_query(REPO / str(alias))
    try:
        oc, orows, osecs = run(target, old_q, timeout)
    except Exception as e:
        return ident, f"old query failed: {str(e)[:100]}"
    try:
        nc, nrows, nsecs = run(target, new_q, timeout)
    except Exception as e:
        return ident, f"new query failed: {str(e)[:100]}"
    status = []
    if oc != nc:
        status.append(f"columns differ: {oc} -> {nc}")
    if orows != nrows:
        status.append(f"rows differ: {sum(orows.values())} -> {sum(nrows.values())}")
    verdict = "SAME" if not status else "DIFF " + "; ".join(status)
    return ident, f"{verdict} | {sum(nrows.values())} rows | {osecs:.1f} s -> {nsecs:.1f} s"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--only", nargs="*", help="identifiers to compare")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=180)
    args = ap.parse_args()
    support = {"collection.ttl", "categories.ttl", "contributors.ttl"}
    files = [p for p in REPO.rglob("*.ttl")
             if p.relative_to(REPO).as_posix() not in support and ".git" not in p.parts]
    if args.only:
        files = [p for p in files if any(f'"{i}"' in p.read_text(encoding="utf-8") for i in args.only)]
    results = []
    with concurrent.futures.ThreadPoolExecutor(args.workers) as pool:
        for ident, result in pool.map(lambda p: compare(p, args.timeout), files):
            if result is not None:
                results.append((ident, result))
    bad = 0
    for ident, result in sorted(results):
        print(f"{ident} | {result}")
        bad += not result.startswith("SAME")
    print(f"{len(results)} compared, {bad} not the same", file=sys.stderr)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
