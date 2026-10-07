# kb/ - the assistant's knowledge graph

- `wiki/` - the pages, the source of truth. Created from `seed/` on the first `kb/kb` run.
  Gitignored by default (it holds personal details).
- `seed/` - the starting pages shipped with the template: how the graph is used and grown,
  and the default standing rules.
- `build/` - derived by `kb/kb build`: `graph.json`, `graph.db` (SQLite), `graph.graphml`,
  and `viewer/index.html`. Never edit; never commit.
- `vocab.json` - node kinds and edge types (the wiki-to-graph defaults plus `judgment`
  and `supersedes`).
- `map.json` - which page section produces which edge type.
- `state/` - when the daily update last succeeded (gitignored); `kb/kb recent` starts there.
- `kb` / `kb.py` - the command. `kb/kb --help` lists everything.
- `tools/wiki-to-graph/` - the vendored build, query and viewer tool. See `VENDORED.md`.

How the assistant uses it: `.claude/skills/knowledge-graph/` (search and read) and
`.claude/skills/knowledge-graph-maintain/` (add, correct, health check).
