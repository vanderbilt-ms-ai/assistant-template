---
name: knowledge-graph
description: Search and read the assistant's knowledge graph (kb/) - people, organizations, projects, lanes, decisions, standing rules, and the documents that are the source of record for them. Use before answering anything about a person, company, project, past decision, or "what do we know about X", "who is X", "what did we decide about X", "how is X connected to Y", "show me the graph", "open the knowledge graph", even when the principal does not say "graph". For adding to or fixing the graph, use knowledge-graph-maintain.
---

# Using the knowledge graph

The graph is what this assistant knows across sessions. The pages in `kb/wiki/` are the
source of truth; `kb/build/` is derived from them. Every command below rebuilds first if a
page changed, so answers are never from a stale build.

## Find

```bash
kb/kb search <words>                 # ranked keyword search over every page
kb/kb node <title>                   # one page: summary, links in/out with reasons, file path
kb/kb list --topic People            # pages by topic; also --kind judgment, --type source
```

`node` takes a partial title ("draft never" finds "Draft, never send"). When it prints
more than one match, pick the right one and run it again with the full title.

## Ask how things connect

```bash
kb/kb query neighbors "<title>"      # everything one link away
kb/kb query backlinks "<title>"      # what points at it
kb/kb query path "<A>" "<B>"         # shortest chain of links between two pages
kb/kb query bfs "<title>"            # everything reachable, nearest first
kb/kb query contradicts              # every recorded disagreement
kb/kb query timeline                 # pages by the year of their sources
kb/kb query topics                   # the topic tree and its counts
```

Filters: `--edges related,cites`, `--kind judgment`, `--topic People`, `--node-type source`.

## Answer from it

1. Search, then read the page with `node`. The summary is the page's claim; the links
   are its reasons. Open the page file when you need the full text.
2. A page's figures are only as good as the source it cites. If you are about to quote a
   number or a date to the principal or in a draft, open the cited document and check it.
3. When pages disagree, the one that `supersedes` the other is current. Say that an older
   value exists if it matters.
4. When the graph has nothing, say so in those words. Not in the graph is not the same as
   not true; check the other systems of record named in `CLAUDE.md`.
5. If what you found is wrong or out of date, fix the page in the same turn
   (knowledge-graph-maintain). Do not answer around a known-bad page.

## Show it

```bash
kb/kb view                           # rebuilds if needed and prints the viewer path
```

In the Claude desktop app, start the `knowledge-graph` preview from `.claude/launch.json`
and navigate to `http://127.0.0.1:8765/#<page title>` to open the viewer focused on a
page. In a terminal, `kb/kb view --open` opens it in the default browser. The viewer is
private: it is served on 127.0.0.1 only, and it is never published, shared, or uploaded.

The viewer draws only nodes joined by a visible edge type. `cites` and `indexes` are off
by default, so source pages appear when `cites` is switched on.
