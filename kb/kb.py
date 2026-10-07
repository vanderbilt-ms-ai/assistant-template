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
    kb/kb recent [--hours N] [--done]  digest of activity since the last graph update
    kb/kb checkpoint | rollback      save / restore kb/wiki around an unattended update
"""
import argparse, glob, json, math, os, re, shutil, subprocess, sys, time
from collections import Counter
from datetime import datetime, timedelta, timezone

KB = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(KB)
rel = lambda p: os.path.relpath(p, REPO)
WIKI = os.path.join(KB, "wiki")
SEED = os.path.join(KB, "seed")
BUILD = os.path.join(KB, "build")
GRAPH = os.path.join(BUILD, "graph.json")
VIEWER = os.path.join(BUILD, "viewer", "index.html")
VOCAB = os.path.join(KB, "vocab.json")
MAP = os.path.join(KB, "map.json")
SCRIPTS = os.path.join(KB, "tools", "wiki-to-graph", "scripts")
TOOL = os.path.join(SCRIPTS, "wiki_to_graph.py")
STATE = os.path.join(KB, "state", "last-update.json")
CHECKPOINT = os.path.join(BUILD, "checkpoint")
# The daily routine's prompt starts with this; its own past sessions are left out of the digest.
ROUTINE_MARK = "[kb-daily-update]"
CLAUDE_PROJECTS = os.path.join(os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude")), "projects")


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
        print("viewer:", rel(VIEWER))
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
            print("run it again with the full title")
            sys.exit(1)
    print("no page matches %r" % q); sys.exit(1)


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
    superseded = {e["target"] for e in g["links"] if e["type"] == "supersedes"}
    N = len(units) or 1
    avg = sum(len(t) for _, t in units) / N
    df = Counter(w for _, t in units for w in set(t))
    scored = []
    for n, t in units:
        tf = Counter(t)
        s = sum(math.log(1 + (N - df[w] + .5) / (df[w] + .5)) * tf[w] * 2.5
                / (tf[w] + 1.5 * (.25 + .75 * len(t) / (avg or 1))) for w in q if tf[w])
        if s > 0:
            # a superseded page is history: still found, ranked below what replaced it
            scored.append((s * (.4 if n["id"] in superseded else 1), n))
    scored.sort(key=lambda x: -x[0])
    if not scored:
        print("nothing in the graph matches. Not in the graph is not the same as not true.")
        return
    for s, n in scored[:a.limit]:
        kind = n.get("kind") or n.get("type")
        topics = ", ".join(n.get("topics") or [])
        old = "  (superseded)" if n["id"] in superseded else ""
        print("%-40s [%s]%s%s" % (n.get("title") or n["id"], kind, ("  " + topics) if topics else "", old))
        if n.get("summary"):
            print("    " + n["summary"][:200].replace("\n", " "))


def cmd_node(a):
    g = fresh()
    n = resolve(g, " ".join(a.title))
    byid = {x["id"]: x for x in g["nodes"]}
    name = lambda i: (byid.get(i) or {}).get("title") or i
    print("%s  [%s]" % (n.get("title") or n["id"], n.get("kind") or n.get("type")))
    if n.get("topics"):
        print("topics:", ", ".join(n["topics"]))
    if n.get("locator"):
        print("locator:", n["locator"])
    if n.get("summary"):
        print(n["summary"])
    out, inc = [], []
    for e in g["links"]:
        why = (" - " + e["context"]) if e.get("context") else ""
        if e["source"] == n["id"]:
            out.append("  %-10s -> %s%s" % (e["type"], name(e["target"]), why))
        elif e["target"] == n["id"]:
            inc.append("  %-10s <- %s%s" % (e["type"], name(e["source"]), why))
    print("links out (%d):" % len(out)); print("\n".join(out) or "  none")
    print("links in (%d):" % len(inc)); print("\n".join(inc) or "  none")
    if n.get("file"):
        print("file:", rel(os.path.join(WIKI, n["file"])))


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


UPDATE_HELP = """kb/kb update <action> [options]   (edits kb/wiki/, then rebuilds)

  add-source  --title T --locator PATH|URL [--medium M] [--date YYYY-MM-DD] [--author A] [--topics T]
  add-node    --title T --kind concept|fact|procedure|schema|judgment [--topics T] [--summary S]
  add-edge    --from A --to B --type related|cites|contradicts|mentions
  remove-edge --from A --to B [--type T]
  remove-node --node T
  rename      --node OLD --title NEW        (rewrites every link to it)
  set-kind    --node T --kind K
  set-topics  --node T --topics T
"""


def cmd_update(a):
    if not a.rest or a.rest[0] in ("-h", "--help") or "-h" in a.rest or "--help" in a.rest:
        print(UPDATE_HELP); return
    ensure_wiki()
    rc = tool("update", WIKI, *a.rest, "--vocab", VOCAB)
    if rc == 0:
        # the edit landed; validation issues mid-task (a new page not linked yet) are
        # reported, and `kb/kb build` is the gate at the end
        print("rebuilt: RESULT: PASS" if build(quiet=True) == 0 else
              "rebuilt with the issues above; a new page stays an orphan until a page links to it")
    sys.exit(rc)


def cmd_lint(a):
    ensure_wiki()
    sys.exit(tool("lint", WIKI, "--vocab", VOCAB))


def title(g, nid):
    for n in g["nodes"]:
        if n["id"] == nid:
            return n.get("title") or nid
    return nid


def cmd_health(a):
    g = fresh()
    print("pages:", len(g["nodes"]), " links:", len(g["links"]))

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
    bare = ["%s -%s-> %s" % (title(g, e["source"]), e["type"], title(g, e["target"])) for e in g["links"]
            if e["type"] not in ("indexes", "records", "cites", "mentions") and not e.get("context")]
    print("links with no stated reason (%d): %s" % (len(bare), "; ".join(bare[:20])))
    # a Sources line that matched no source page becomes a stub source with no page of its own
    stubs = [n.get("title") or n["id"] for n in g["nodes"] if n.get("type") == "source" and not n.get("file")]
    print("citations that matched no source page (%d): %s" % (len(stubs), "; ".join(stubs[:20])))
    problems = len(nosrc) + len(orphans) + len(dangling) + len(bare) + len(stubs)
    print("RESULT: " + ("PASS" if not problems else "%d thing(s) to fix" % problems))
    sys.exit(1 if problems else 0)


def cmd_build(a):
    sys.exit(build())


def cmd_view(a):
    if stale() and build(quiet=True) != 0:
        sys.exit(1)
    print(VIEWER)
    if a.open:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.run([opener, VIEWER])


# ---- the daily update routine ----------------------------------------------------------------

SECRET = re.compile(r"(?i)(sk-[a-z0-9_-]{16,}|ghp_[a-z0-9]{20,}|xox[abpr]-[a-z0-9-]{10,}|"
                    r"(?:api[_-]?key|token|secret|password)\s*[:=]\s*\S+|\b(?:\d[ -]?){13,19}\b)")


def clean(s, limit):
    s = re.sub(r"<system-reminder>.*?</system-reminder>", "", s or "", flags=re.S)
    s = SECRET.sub("[redacted]", s).strip()
    return s if len(s) <= limit else s[:limit] + " [...]"


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content
                         if isinstance(b, dict) and b.get("type") == "text")
    return ""


def window_start(hours):
    if hours is None and os.path.exists(STATE):
        try:
            last = datetime.fromisoformat(json.load(open(STATE))["last_success"])
            # never reach back further than a week, even after a long gap
            return max(last, datetime.now(timezone.utc) - timedelta(days=7))
        except (ValueError, KeyError):
            pass
    return datetime.now(timezone.utc) - timedelta(hours=hours or 24)


def sessions(since):
    """Turns from every Claude Code session run in this repo (or a worktree of it) since `since`."""
    out = []
    for f in glob.glob(os.path.join(CLAUDE_PROJECTS, "*", "*.jsonl")):
        if os.path.getmtime(f) < since.timestamp():
            continue
        turns, routine = [], False
        for line in open(f, encoding="utf-8", errors="replace"):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("type") not in ("user", "assistant") or d.get("isMeta") or d.get("isSidechain"):
                continue
            if not (d.get("cwd") or "").startswith(REPO):
                continue
            body = text_of((d.get("message") or {}).get("content"))
            if not turns and d["type"] == "user" and ROUTINE_MARK in body:
                routine = True
                break
            ts = d.get("timestamp")
            if not ts or not body.strip():
                continue
            if datetime.fromisoformat(ts.replace("Z", "+00:00")) < since:
                continue
            who = "PRINCIPAL" if d["type"] == "user" else "ASSISTANT"
            turns.append("**%s** (%s): %s" % (who, ts[:16].replace("T", " "),
                                            clean(body, 2500 if who == "PRINCIPAL" else 1200)))
        if turns and not routine:
            out.append((os.path.basename(f), turns))
    return out


def memories(since):
    """Claude Code auto-memory files for this repo's project folders changed since `since`."""
    enc = re.sub(r"[^A-Za-z0-9]", "-", REPO)
    out = []
    for d in glob.glob(os.path.join(CLAUDE_PROJECTS, enc + "*", "memory")):
        for f in sorted(glob.glob(os.path.join(d, "*.md"))):
            if os.path.getmtime(f) >= since.timestamp() and os.path.basename(f) != "MEMORY.md":
                out.append((f, clean(open(f, encoding="utf-8", errors="replace").read(), 3000)))
    return out


SKIP_DIRS = {"kb", "node_modules", "venv", "__pycache__", "build", "dist", "writing-samples"}


def repo_changes(since):
    """Commits, and files changed on disk outside kb/ (gitignored drafts and notes included)."""
    log = subprocess.run(["git", "-C", REPO, "log", "--since", since.isoformat(), "--stat",
                          "--format=%h %ad %s", "--date=short"], capture_output=True, text=True).stdout
    changed = []
    for root, dirs, files in os.walk(REPO):
        # hidden folders, dependencies and build output say nothing about what was learned
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS and (not x.startswith(".") or x == ".claude")
                   and not (root == os.path.join(REPO, ".claude") and x == "worktrees")
                   # another git repository nested in here is its own project
                   and not os.path.exists(os.path.join(root, x, ".git"))]
        for f in files:
            p = os.path.join(root, f)
            try:
                if os.path.getmtime(p) >= since.timestamp():
                    changed.append(rel(p))
            except OSError:
                pass
    return log.strip(), sorted(changed)


def cmd_recent(a):
    if a.done:
        os.makedirs(os.path.dirname(STATE), exist_ok=True)
        json.dump({"last_success": datetime.now(timezone.utc).isoformat()}, open(STATE, "w"))
        print("recorded a successful graph update at", datetime.now().strftime("%Y-%m-%d %H:%M"))
        return
    since = window_start(a.hours)
    ss, mm, (log, changed) = sessions(since), memories(since), repo_changes(since)
    lines = ["# Activity since %s (UTC)" % since.strftime("%Y-%m-%d %H:%M"), "",
             "Sessions: %d. Memory files changed: %d. Files changed outside kb/: %d." % (
                 len(ss), len(mm), len(changed)), ""]
    for name, turns in ss:
        lines += ["## Session %s" % name, ""] + [t + "\n" for t in turns]
    for path, body in mm:
        lines += ["## Memory file %s" % path, "", body, ""]
    if log:
        lines += ["## Commits", "", "```", log, "```", ""]
    if changed:
        lines += ["## Files changed", ""] + ["- " + c for c in changed[:200]] + [""]
    os.makedirs(os.path.join(BUILD, "recent"), exist_ok=True)
    out = os.path.join(BUILD, "recent", datetime.now().strftime("%Y-%m-%d-%H%M") + ".md")
    open(out, "w", encoding="utf-8").write("\n".join(lines))
    print("digest:", rel(out))
    print("sessions %d, memory files %d, files changed %d" % (len(ss), len(mm), len(changed)))
    if not (ss or mm or log or changed):
        print("nothing new since the last update")


def cmd_checkpoint(a):
    ensure_wiki()
    shutil.rmtree(CHECKPOINT, ignore_errors=True)
    shutil.copytree(WIKI, CHECKPOINT)
    print("checkpoint of kb/wiki saved")


def cmd_rollback(a):
    if not os.path.isdir(CHECKPOINT):
        print("no checkpoint to roll back to"); sys.exit(1)
    shutil.rmtree(WIKI, ignore_errors=True)
    shutil.copytree(CHECKPOINT, WIKI)
    print("kb/wiki restored from the checkpoint")
    sys.exit(build())


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
    p = sp.add_parser("recent"); p.add_argument("--hours", type=float)
    p.add_argument("--done", action="store_true", help="record that the update succeeded")
    p.set_defaults(f=cmd_recent)
    sp.add_parser("checkpoint").set_defaults(f=cmd_checkpoint)
    sp.add_parser("rollback").set_defaults(f=cmd_rollback)
    # update and query pass their arguments straight to the graph tool; argparse would
    # otherwise claim leading options such as --help or --edges for itself
    if len(sys.argv) > 1 and sys.argv[1] in ("update", "query"):
        a = argparse.Namespace(rest=sys.argv[2:])
        return (cmd_update if sys.argv[1] == "update" else cmd_query)(a)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
