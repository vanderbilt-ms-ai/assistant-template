# Vendored: wiki-to-graph

`scripts/` and `reference/` are copied from https://github.com/vanderbilt-ms-ai/wiki-to-graph
(CC BY-NC-SA 4.0, see LICENSE.md), at commit 4ec170c of a branch that
merges main with these not-yet-merged changes:

- viewer: draw only nodes joined by a visible edge type (PR 8)
- viewer: legend lists what the graph contains and explains added types (PR 9)
- build: page frontmatter kept as node `meta`; `graph.db` stores node meta and edge context;
  `validate` counts unresolved links
- viewer: clear selection (button, Esc, empty-space click, empty search); symmetric edge
  types read from the graph; metadata escaping (from PR 5)
- update: accepts `--vocab`, so add-node and set-kind take this graph's `judgment` kind

`reference/page-authoring.md` and `reference/maintenance.md` are that repo's wiki-author
and wiki-graph-maintain skills, kept here as reference reading; the assistant's own skills
are in `.claude/skills/knowledge-graph*`.

To update: copy `skills/wiki-to-graph/scripts/*.py` from a newer wiki-to-graph over
`scripts/`, run `kb/kb build`, and check it still prints RESULT: PASS.
