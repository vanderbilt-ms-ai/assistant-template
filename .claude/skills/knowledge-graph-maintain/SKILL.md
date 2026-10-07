---
name: knowledge-graph-maintain
description: Add to, correct, and keep healthy the assistant's knowledge graph (kb/). Use when a session turns up something durable - a new person, organization or project, a status change, a decision and its reason, a document that is now the source of record, a correction from the principal - and when asked to "add this to the graph", "remember this", "update the graph", "fold this document in", "clean up the graph", "what's orphaned", or for the periodic health check. Also used by /setup to seed the graph. For searching and reading the graph, use knowledge-graph.
---

# Growing and maintaining the knowledge graph

The markdown pages in `kb/wiki/` are the single source of truth. Never edit anything in
`kb/build/`; every build recomputes it. The failure this skill prevents is silent decay:
near-duplicate pages, claims with no source, and pages nothing links to.

## What earns a page

Something that will matter again:

- a person who will come up in mail, meetings or drafts (topic `People`)
- an organization, project, deal, course or other piece of work with a status
  (topic `Organizations`, `Projects / <lane>`, or the lane's own name)
- a lane of the principal's life (topic `Lanes`)
- a decision, and why it was made (`kind: fact`)
- a document that is the system of record for some fact (a source page)
- a standing rule learned from a correction (`kind: judgment`)

A one-off detail stays out. So does anything sensitive: no credentials, account or card
numbers, government IDs, health details, or private details about third parties beyond
what the work needs.

## The page contract

```markdown
---
kind: concept | fact | procedure | schema | judgment
topics: People
---

# Title

## Summary
One to three sentences: what it is, and why it is in this graph.

## Explanation
The substance. Every date, number and status names the source it came from.

## Related
- [[Other Page]] - one line on why these two belong together

## Supersedes
- [[Older Page]] - what this replaces and since when (only when it replaces something)

## Sources
- path/or/URL - what it is, and where in it
```

What a page is about (a person, a company) is its `topics:`, not a new kind. How two pages
connect is the reason written after the link. One link per bullet, the page the bullet is
about first; text after the link becomes the edge's reason in the graph and the viewer.
Pages are plain ASCII. The full authoring guide is
`kb/tools/wiki-to-graph/reference/page-authoring.md`.

## Adding something

1. Search first: `kb/kb search <words>`. Extend an existing page rather than creating a
   near duplicate. Same person under two spellings is one page.
2. A document comes in as a source page first:
   ```bash
   kb/kb update add-source --title "<short name>" --locator <path or URL> --date <YYYY-MM-DD> --topics "<topic>"
   ```
3. Then the pages it supports:
   ```bash
   kb/kb update add-node --title "<Title>" --kind fact --topics "People" --summary "<one or two sentences>"
   ```
4. Open the new page and write the Explanation, Related (with reasons) and Sources. Link it
   from at least one existing page, and add a bullet for it under the right heading in
   `index.md` (edit the file; `add-edge` writes only related, cites, mentions and
   contradicts links). Until something links to it, the build reports it as an orphan.
   `add-edge` writes a bare link; add the reason after it.
5. When a fact changes, do not overwrite the old value silently. Write the new value, keep
   the old one marked "(superseded <date>, was ...)", or for a replaced document add a
   `## Supersedes` section on the new page.
6. `kb/kb build` must print `RESULT: PASS`. Then `kb/kb node "<Title>"` to read it back.
7. Tell the principal in one line what was added or changed.

## Corrections become judgments

When the principal corrects the assistant on something that will come up again, in the
same turn:

1. Write the rule into the right identity file (usually `.claude/identity/operating.md`).
2. Add a `kind: judgment` page whose title states the rule, whose Explanation says what
   went wrong and what to do instead, and whose Sources cite the identity file and the date.
3. Link it from `index.md` under "Standing rules" and from the pages it governs.
4. Build, and tell the principal both places it was written.

## Other edits

```bash
kb/kb update rename --node "<Old>" --title "<New>"    # rewrites every link to it
kb/kb update add-edge --from "<A>" --to "<B>" --type related
kb/kb update remove-node --node "<Title>"
kb/kb update set-kind --node "<Title>" --kind judgment
kb/kb update set-topics --node "<Title>" --topics "People"
```

## Health check

Run at the end of any session that added several pages, and when asked to clean up:

```bash
kb/kb health                         # orphans, pages citing no source, unexplained links, dangling links
kb/kb lint                           # links with no stated reason, what build will normalize
```

Fix what it finds in the same pass: merge duplicates (rename one onto the other, then
remove it), give every link a reason, give every fact page a source, and link orphans
from the page they belong under. Report the counts before and after.

## Changing the vocabulary

`kb/vocab.json` holds the kinds and edge types. Add one only when a real question cannot
be answered with a topic or a reasoned `related` link, and propose it to the principal
first with the question it answers
(`kb/tools/wiki-to-graph/reference/custom-vocabulary.md`, "Before you extend it").
