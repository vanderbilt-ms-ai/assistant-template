#!/usr/bin/env python3
"""The assistant's knowledge graph: one command for build, search, read, query and edit.

The pages in kb/wiki/ are the source of truth. Everything in kb/build/ is derived from them
and is recomputed by `build`. Python standard library only.

    kb/kb build                      rebuild graph + viewer; must end with RESULT: PASS
    kb/kb search <words>             ranked keyword search over every page
    kb/kb node <title>               one page: summary, links in and out, file path
    kb/kb list [--kind K] [--topic T] [--type source]
    kb/kb query <question> [terms]   neighbors, backlinks, path, bfs, contradicts, timeline, ...
    kb/kb update <action> [...]      add-node, add-source, add-edge, rename, set-kind, ...
    kb/kb lint                       what build will normalize, links with no stated reason
    kb/kb health                     orphans, pages with no source, unexplained links
    kb/kb view [--open]              current viewer; prints its path
"""
import argparse, json, math, os, re, shutil, subprocess, sys
from collections import Counter

KB = os.path.dirname(os.path.abspath(__file__))
WIKI = os.path.join(KB, "wiki")
SEED = os.path.join(KB, "seed")
BUILD = os.path.join(KB, "build")
GRAPH = os.path.join(BUILD, "graph.json")
VIEWER = os.path.join(BUILD, "viewer", "index.html")
VOCAB = os.path.join(KB, "vocab.json")
MAP = os.path.join(KB, "map.json")
SCRIPTS = os.path.join(KB, "tools", "wiki-to-graph", "scripts")
TOOL = os.path.join(SCRIPTS, "wiki_to_graph.py")


def tool(*args, capture=False):
    cmd = [sys.executable, TOOL, *args]
    if capture:
        return subprocess.run(cmd, capture_output=True, text=True)
    return subprocess.run(cmd).returncode


def ensure_wiki():
    """First run: the wiki starts as a copy of the seed pages."""
    if not os.path.isdir(WIKI) or not any(f.endswith(".md") for f in os.listdir(WIKI)):
        shutil.copytree(SEED, WIKI, dirs_exist_ok=True)
        print("kb: started kb/wiki/ from kb/seed/")


def pages():
    for root, _, files in os.walk(WIKI):
        for f in sorted(files):
            if f.endswith(".md"):
                yield os.path.join(root, f)


def stale():
    if not os.path.exists(GRAPH) or not os.path.exists(VIEWER):
        return True
    built = min(os.path.getmtime(GRAPH), os.path.getmtime(VIEWER))
    inputs = [VOCAB, MAP, TOOL, *pages()]
    return any(os.path.getmtime(p) > built for p in inputs)


def build(quiet=False):
    ensure_wiki()
    os.makedirs(os.path.dirname(VIEWER), exist_ok=True)
    r = tool("build", WIKI, "-o", GRAPH, "--emit", "sqlite,graphml",
             "--vocab", VOCAB, "--map", MAP, capture=True)
    if r.returncode != 0:
        print(r.stdout + r.stderr); return 1
    v = tool("validate", GRAPH, "--vocab", VOCAB, capture=True)
    w = subprocess.run([sys.executable, os.path.join(SCRIPTS, "build_graph_viewer.py"),
                        GRAPH, "-o", VIEWER], capture_output=True, text=True)
    if w.returncode != 0:
        print(w.stdout + w.stderr); return 1
    if not quiet:
        print(r.stdout.strip())
        print(v.stdout.strip())
        print("viewer:", os.path.relpath(VIEWER))
    elif v.returncode != 0:
        # only the failing checks; `kb/kb build` prints the full report
        for line in v.stdout.splitlines():
            s = line.strip()
            if s.startswith("RESULT") or (": " in s and not s.endswith(": 0 []")
                                          and s.split(":")[0] in ("dangling links ", "orphan concepts", "self-loops     ")):
                print("  " + s)
    return v.returncode


def fresh():
    """Read commands rebuild first when any page changed since the last build."""
    if stale() and build(quiet=True) != 0:
        print("kb: build failed; fix it before trusting answers (kb/kb build)"); sys.exit(1)
    with open(GRAPH, encoding="utf-8") as fh:
        return json.load(fh)


def resolve(g, q):
    """Exact title, then case-insensitive, then prefix, then substring, then all words."""
    nodes = g["nodes"]
    ql = q.lower().strip()
    qw = set(tokens(q))
    for test in (lambda t: t == q, lambda t: t.lower() == ql,
                 lambda t: t.lower().startswith(ql), lambda t: ql in t.lower(),
                 lambda t: qw and qw <= set(tokens(t))):
        hits = [n for n in nodes if test(n.get("title") or n["id"])]
        if len(hits) == 1:
            return hits[0]
        if len(hits) > 1:
            print("more than one page matches %r:" % q)
            for n in hits[:15]:
                print("  ", n.get("title") or n["id"])
            sys.exit(1)
    print("no page matches %r. Try: kb/kb search %s" % (q, q)); sys.exit(1)


def tokens(s):
    return re.findall(r"[a-z0-9]+", (s or "").lower())


def cmd_search(a):
    g = fresh()
    units = []
    for n in g["nodes"]:
        body = ""
        if n.get("file") and os.path.exists(os.path.join(WIKI, n["file"])):
            body = open(os.path.join(WIKI, n["file"]), encoding="utf-8").read()
        title = n.get("title") or n["id"]
        # title words count three times, so a page about X outranks pages that mention X
        units.append((n, tokens(title) * 3 + tokens(n.get("summary")) * 2 + tokens(body)))
    q = tokens(" ".join(a.text))
    N = len(units) or 1
    avg = sum(len(t) for _, t in units) / N
    df = Counter(w for _, t in units for w in set(t))
    scored = []
    for n, t in units:
        tf = Counter(t)
        s = sum(math.log(1 + (N - df[w] + .5) / (df[w] + .5)) * tf[w] * 2.5
                / (tf[w] + 1.5 * (.25 + .75 * len(t) / (avg or 1))) for w in q if tf[w])
        if s > 0:
            scored.append((s, n))
    scored.sort(key=lambda x: -x[0])
    if not scored:
        print("nothing in the graph matches. Not in the graph is not the same as not true.")
        return
    for s, n in scored[:a.limit]:
        kind = n.get("kind") or n.get("type")
        topics = ", ".join(n.get("topics") or [])
        print("%-40s [%s]%s" % (n.get("title") or n["id"], kind, ("  " + topics) if topics else ""))
        if n.get("summary"):
            print("    " + n["summary"][:200].replace("\n", " "))


def cmd_node(a):
    g = fresh()
    n = resolve(g, " ".join(a.title))
    r = tool("query", GRAPH, "node", n["id"], "--vocab", VOCAB, capture=True)
    print(r.stdout.rstrip())
    if n.get("meta"):
        print("meta:", json.dumps(n["meta"], ensure_ascii=False))
    if n.get("file"):
        print("file:", os.path.relpath(os.path.join(WIKI, n["file"])))


def cmd_list(a):
    g = fresh()
    for n in sorted(g["nodes"], key=lambda n: (n.get("title") or n["id"]).lower()):
        if a.kind and (n.get("kind") or "") != a.kind:
            continue
        if a.type and n.get("type") != a.type:
            continue
        if a.topic and not any(a.topic.lower() in t.lower() for t in n.get("topics") or []):
            continue
        print("%-40s [%s]  %s" % (n.get("title") or n["id"], n.get("kind") or n.get("type"),
                                  ", ".join(n.get("topics") or [])))


def cmd_query(a):
    fresh()
    sys.exit(tool("query", GRAPH, *a.rest, "--vocab", VOCAB))


def cmd_update(a):
    ensure_wiki()
    rc = tool("update", WIKI, *a.rest, "--vocab", VOCAB)
    if rc == 0:
        rc = build(quiet=True)
        print("rebuilt: RESULT: PASS" if rc == 0 else
              "rebuilt with issues above; a new page stays an orphan until a page links to it")
    sys.exit(rc)


def cmd_lint(a):
    ensure_wiki()
    sys.exit(tool("lint", WIKI))


def cmd_health(a):
    g = fresh()
    print("pages:", len(g["nodes"]), " links:", len(g["links"]))
    for q in ("unexplained",):
        r = tool("query", GRAPH, q, "--vocab", VOCAB, capture=True)
        print(r.stdout.rstrip())
    cites = {e["source"] for e in g["links"] if e["type"] == "cites"}
    inbound = set()
    for e in g["links"]:
        if e["type"] in ("indexes", "records"):
            continue
        inbound.add(e["target"])
        if not e.get("directed", True):
            inbound.add(e["source"])
    concepts = [n for n in g["nodes"] if n.get("type") == "concept"]
    nosrc = [n.get("title") or n["id"] for n in concepts if n["id"] not in cites]
    orphans = [n.get("title") or n["id"] for n in concepts if n["id"] not in inbound]
    print("pages citing no source (%d): %s" % (len(nosrc), "; ".join(nosrc[:20])))
    print("pages nothing links to except the index (%d): %s" % (len(orphans), "; ".join(orphans[:20])))
    dangling = g.get("meta", {}).get("warnings", {}).get("dangling") or []
    print("links to pages that do not exist (%d): %s" % (
        len(dangling), "; ".join("%s -> %s" % tuple(d) for d in dangling[:20])))


def cmd_build(a):
    sys.exit(build())


def cmd_view(a):
    if stale() and build(quiet=True) != 0:
        sys.exit(1)
    print(VIEWER)
    if a.open:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.run([opener, VIEWER])


def main():
    ap = argparse.ArgumentParser(prog="kb", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("build").set_defaults(f=cmd_build)
    p = sp.add_parser("search"); p.add_argument("text", nargs="+")
    p.add_argument("--limit", type=int, default=10); p.set_defaults(f=cmd_search)
    p = sp.add_parser("node"); p.add_argument("title", nargs="+"); p.set_defaults(f=cmd_node)
    p = sp.add_parser("list"); p.add_argument("--kind"); p.add_argument("--topic")
    p.add_argument("--type", help="concept, source, index or log"); p.set_defaults(f=cmd_list)
    p = sp.add_parser("query", add_help=False); p.add_argument("rest", nargs=argparse.REMAINDER)
    p.set_defaults(f=cmd_query)
    p = sp.add_parser("update", add_help=False); p.add_argument("rest", nargs=argparse.REMAINDER)
    p.set_defaults(f=cmd_update)
    sp.add_parser("lint").set_defaults(f=cmd_lint)
    sp.add_parser("health").set_defaults(f=cmd_health)
    p = sp.add_parser("view"); p.add_argument("--open", action="store_true"); p.set_defaults(f=cmd_view)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
