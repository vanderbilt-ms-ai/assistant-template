[kb-daily-update]

# Daily knowledge graph update

You are the assistant defined in this repository, running unattended as a scheduled
routine. Nobody is watching this run and nobody can answer a question. Read `CLAUDE.md`
and `.claude/skills/knowledge-graph-maintain/SKILL.md` first; this file adds only what
is specific to the unattended update.

Your job: turn what happened since the last update into durable pages in the knowledge
graph, so the next session knows it.

## Hard limits for this run

- Edit only files under `kb/wiki/`, and write the run report under `notes/kb-updates/`.
- Never send, post, publish, delete or accept anything, and never use a connector to
  write. Connectors are read-only in this run.
- Never edit `CLAUDE.md`, `.claude/identity/*`, `kb/vocab.json`, or anything outside
  `kb/wiki/` and `notes/kb-updates/`. A correction that is not yet in an identity file
  goes in the report as a proposal, not into the identity file.
- Never remove a page. When something stopped being true, mark it superseded.
- No credentials, account numbers, IDs, health details or private details about other
  people beyond what the principal's work needs, even if the digest contains them.

## Steps

1. `kb/kb checkpoint` (saves `kb/wiki/` so a bad run can be undone).
2. `kb/kb recent` and read the digest file it names, all of it. It holds the principal's
   and the assistant's turns from every session in this repo since the last successful
   update (24 hours on the first run), changed auto-memory files, commits, and files
   changed outside `kb/`. If it prints "nothing new", skip to step 7.
3. If `CLAUDE.md` lists a connected email or calendar, also read (only read) the last 24
   hours of sent mail and calendar events for facts that belong in the graph: new people,
   meetings agreed, decisions announced, documents sent as the current version.
4. List what is durable, using "What earns a page" in the maintain skill:
   - new people, organizations, projects, and changes to their status
   - decisions and the reason given for them
   - documents that became the source of record, or replaced an older one
   - corrections the principal gave. If the session also wrote the rule into an identity
     file, add the `judgment` page citing that file. If it did not, do not add a page;
     put the rule in the report under "Proposed corrections".
   Use only what the principal said or a tool returned. What the assistant only
   proposed or guessed is not a fact. Skip one-off details.
5. For each item, search first (`kb/kb search`, `kb/kb node`), then extend the existing
   page or add a new one, exactly as the maintain skill says: page contract, reasons on
   every link, sources cited by `[[source page]]`, superseded values kept visible. A fact
   whose source is a session cites `- [[Session transcripts]] - <session file>, <date>:
   what the principal said`. A fact from an auto-memory file cites the same page with the
   memory file's name.
6. Add an entry at the top of `kb/wiki/log.md`, under a `## YYYY-MM-DD` heading, one
   bullet per page added or changed: `- [[Page]] - what changed and why`.
7. `kb/kb build` must print `RESULT: PASS` and `kb/kb health` must print `RESULT: PASS`.
   Fix what they report. If you cannot get both to pass, run `kb/kb rollback`, do not
   run step 8, and say so at the top of the report.
8. `kb/kb recent --done` (records this run as the new starting point).
9. Write `notes/kb-updates/YYYY-MM-DD.md`: one line with the outcome (pages added,
   pages changed, or "no changes"), then the bullets from the log entry, then
   "Proposed corrections" and "Not added" (anything durable you left out and why).
   Keep it short; the principal reads it in a minute.
