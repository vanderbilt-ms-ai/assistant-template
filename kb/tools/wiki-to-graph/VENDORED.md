# Vendored: wiki-to-graph

`scripts/` and `reference/` are copied from https://github.com/vanderbilt-ms-ai/wiki-to-graph
(CC BY-NC-SA 4.0, see LICENSE.md): its main branch plus these changes, which were open pull
requests there when this copy was taken:

- viewer: draw only nodes joined by a visible edge type (PR 8)
- viewer: legend lists what the graph contains and explains added types (PR 9)
- metadata escaping in the viewer (from PR 5)
- PR 11: build keeps page frontmatter as node `meta`, `graph.db` stores node meta and edge
  context, `validate` counts unresolved links; viewer clear selection and symmetric edge
  types read from the graph; `update` and `lint` accept `--vocab`

`reference/custom-vocabulary.md` has its worked example replaced by a pointer to this repo's
`kb/vocab.json`, since the example file it named is not copied here.

`reference/page-authoring.md` and `reference/maintenance.md` are that repo's wiki-author
and wiki-graph-maintain skills, kept here as reference reading; the assistant's own skills
are in `.claude/skills/knowledge-graph*`.

To update: copy `skills/wiki-to-graph/scripts/*.py` from a newer wiki-to-graph over
`scripts/`, run `kb/kb build`, and check it still prints RESULT: PASS.
