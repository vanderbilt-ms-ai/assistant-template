---
kind: procedure
topics: Assistant / Knowledge graph
---

# Growing the knowledge graph

## Summary
When a session turns up a durable fact, a new person or organization, a decision, or a
correction, the assistant writes it into the graph in the same turn and rebuilds. A thing
written down survives; a thing intended does not.

## Explanation
A page is earned by something that will matter again: a person who will come up in mail
or meetings, an organization or project with a status, a decision and why it was made, a
document that is the system of record for some fact, or a rule learned from a correction.
One-off details stay out.

Before adding, search for an existing page and extend it rather than creating a near
duplicate. Add with `kb/kb update add-node --title ... --kind ... --topics ... --summary ...`
or `add-source --title ... --locator ...`, then edit the page so every link sits in its own
bullet with a stated reason. Corrections become a `judgment` page that cites where the rule
was written, and the same rule goes into the identity file. Finish with `kb/kb build`; it
must print RESULT: PASS. Tell the principal in one line what was added.

## Related
- [[Using the knowledge graph]] - the pages added here are what later searches find
- [[Operating contract]] - where a correction is written alongside its judgment page
- [[Newest source wins]] - how a newer fact replaces an older one without erasing it

## Sources
- [[Operating contract]] - the working contract
