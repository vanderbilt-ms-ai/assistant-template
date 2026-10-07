---
kind: procedure
topics: Assistant / Knowledge graph
---

# Using the knowledge graph

## Summary
Before answering anything about a person, organization, project, lane, past decision or
standing rule, search the graph and read the page. The graph is what the assistant knows
across sessions; the conversation is not.

## Explanation
Search with `kb/kb search <words>`, then read the best match with `kb/kb node <title>`,
which prints the page's summary, the links in and out with their stated reasons, and the
file to open for the full text. `kb/kb query neighbors|backlinks|path|bfs|contradicts|timeline`
answers questions about how things connect. Read commands rebuild first when a page changed.

An answer from the graph is only as good as the source the page cites. When a page cites a
document, open that document before quoting a number from it. When the graph has nothing,
say so: not in the graph is not the same as not true.

## Related
- [[Growing the knowledge graph]] - the other half of the loop: what is learned goes back in
- [[A tool result is the only evidence]] - a search that returns nothing is reported as nothing
- [[Newest source wins]] - which value to give when two pages disagree

## Sources
- .claude/identity/operating.md - Operating contract
