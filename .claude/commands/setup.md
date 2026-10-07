---
description: Guided setup - interviews you and fills in this assistant's identity files
argument-hint: "[resume | voice | platforms | review]"
---

# /setup

You are running the guided setup for this assistant template. At the end of it,
every `{{PLACEHOLDER}}` in this repo is replaced with something true about the
person you are talking to, and the assistant has an identity.

Read this whole file before your first message.

## What you are filling in

```
CLAUDE.md                        standing rules, lanes, platforms, domain notes
.claude/identity/soul.md         character and moral compass
.claude/identity/persona.md      how you come across to them
.claude/identity/operating.md    what you must and must not do
.claude/identity/user.md         who they are
.claude/identity/voice.md        how they write, so you can draft as them
kb/wiki/                         the knowledge graph: people, lanes, sources, rules
```

Worked examples of all six, filled in for a fictional person, are in
`.claude/identity/examples/`. Read them before you start. They show the level of
specificity to aim for. Do not copy their content; the fictional person is not
your principal.

## Ground rules for the interview

1. **Batch questions by phase.** One message per phase, a small numbered group of
   questions in it. Never one question per message. Never a wall of thirty.
2. **Never ask what you can find.** Check the git config, the connected tools, the
   system timezone, and the files on disk first. Ask only to confirm what you
   found, and only when getting it wrong would matter.
3. **Accept "skip" and "I don't know".** Write `not established yet` into the file
   and move on. A placeholder left visibly unanswered is honest. A confident
   invention is not.
4. **Show your draft before you write it.** At the end of each phase, show the
   text you are about to put in the file and get a yes. Edits at this stage are
   cheap.
5. **Save as you go.** After every phase, append the confirmed answers to
   `.claude/setup/answers.md`. If the session dies, `/setup resume` picks up from
   there.
6. **Write plain ASCII.** No em-dashes, no smart quotes, no emoji, in your own
   messages and in every file you write. This holds regardless of what the
   principal's own character-set rule turns out to be.
7. **You are the one doing the reasoning.** Where a sensible default exists,
   propose it and ask for a yes or a correction. Do not hand over a blank field.

## Arguments

- no argument, or `resume`: run the phases, skipping any already recorded in
  `.claude/setup/answers.md`
- `voice`: re-run Phase 5 only, against new samples. Use this when a fresh batch
  of writing arrives.
- `platforms`: re-run Phase 6 only. Use this when a connector is added or dies.
- `graph`: re-run Phase 8 only, against the current answers. Use this to reseed
  the knowledge graph after the identity files change.
- `review`: run no interview. Read every identity file, check them against
  `.claude/setup/answers.md`, and report what is thin, stale, or contradictory.
  Also run `kb/kb health` and report orphans, unsourced pages, and judgments in
  `operating.md` that have no page in the graph (or the reverse).

---

## Phase 0 - Orientation

Before you ask anything:

1. `cat .claude/setup/answers.md` if it exists. Everything in it is already
   answered; skip those phases.
2. Read all six example files in `.claude/identity/examples/`.
3. `git config user.name` and `git config user.email`.
4. Check the current date and the system timezone.
5. `ls writing-samples/` to see whether writing samples are already there.
6. Check which connectors and tools this session actually has. Do not guess from
   tool names alone; note what is present and what is absent.

Then tell them, in about five lines: what setup will produce, that it takes
roughly twenty minutes, that Phase 5 needs them to paste or point at real writing
they have sent, and that they can stop anywhere and resume with `/setup resume`.

Then go straight into Phase 1. Do not wait for permission to begin.

---

## Phase 1 - Who you are talking to

Ask, in one message:

1. Full name, and what you should call them.
2. Pronouns. Say that you will use they/them until told otherwise, so this is a
   correction rather than a demand.
3. Primary email address, and any others that matter.
4. Timezone. Propose the one you detected.
5. What they want to call this assistant. Say that the name goes in every identity
   file and in `CLAUDE.md`, and offer a default if they have no preference.

Fills: `ASSISTANT_NAME`, `PRINCIPAL_FULL_NAME`, `PRINCIPAL_FIRST_NAME`,
`PRINCIPAL_PREFERRED_NAME`, `PRINCIPAL_PRONOUNS`, `PRINCIPAL_EMAIL`,
`PRINCIPAL_TIMEZONE`.

---

## Phase 2 - The lanes

This is the most important phase. A lane is a distinct area of their life with its
own audience, its own stakes, and its own idea of what "done" looks like. Most
people have two to four. Work, and a second thing, and the admin that both land on.

Ask:

1. What are the distinct areas of their life this assistant should help with? Ask
   for a name and one sentence each.
2. For each lane: what kinds of task actually land here? Drafting, research,
   scheduling, tracking, review?
3. For each lane: what is explicitly **out** of scope, and where does that work
   live instead? Give an example of the shape you want: "not the engineering
   itself; that lives in the product repos under their own rules". This is the
   line that stops the assistant doing the wrong work in the wrong place.
4. For each lane: who is downstream of anything written? A customer, a student, a
   regulator, a family member, nobody? Name the stakes.
5. Any recurring people the assistant will meet in mail, calendar, or drafts, with
   a role and one clause of context.

Then ask about the audience inside each lane where it is not obvious. "Who reads
this, and what do they already know" changes every draft that lane produces.

Fills: `LANE_SCOPE`, `LANE_NAMES_INLINE`, `LANE_DOWNSTREAM_INLINE`,
`PRINCIPAL_ROLES`, `PRINCIPAL_SITUATION`, `KEY_PEOPLE`.

For `PRINCIPAL_SITUATION`, write one short paragraph in the assistant's own voice
about the shape of their life. It is the sentence that explains why the assistant
exists. Show it to them; people are particular about how their life is described.

---

## Phase 3 - How they want to be worked with

Propose the defaults already in `operating.md` and `user.md` rather than asking
open questions. For each, ask keep, loosen, or tighten.

1. **Draft, never send.** The default is that nothing goes out under their name
   without them pressing send, including routine replies. Confirm. If they want to
   loosen it, make them name the exact category that is exempt, and write that
   exemption into `operating.md` in their words.
2. **Irreversible actions.** Deleting, spending, accepting terms, submitting forms,
   changing account settings: state and wait. Confirm.
3. **Confirmation appetite.** How much checking in before acting on internal work?
   Offer the spectrum: ask before each step / ask once then execute the whole task
   / just go.
4. **Verbosity.** One-line outcomes with depth on request, or full narration?
5. **What annoys them.** Ask outright. This is the highest-signal question in the
   whole interview and people answer it readily. Push for specifics: what has a
   previous assistant, human or otherwise, done that made them grind their teeth?
6. **Working values.** Correctness over speed? Simple over clever? Ask for three.
7. **How they give correction,** and how much technical depth to assume.
8. **Hard nevers.** Anything absolute. Paths never to touch, systems never to log
   into, topics never to draft on, a system of record that must always be cited
   over its older copies.
9. **Interface.** Terminal, desktop app, or both? This sets the formatting rules in
   `persona.md`: markdown tables and emoji are fine in a rendered UI and are not in
   a terminal.

Fills: `PRINCIPAL_VALUES`, `PRINCIPAL_ANNOYANCES`, `PRINCIPAL_FEEDBACK_STYLE`,
`HARD_RULES`, `OPERATING_ADDITIONS`, `FORMATTING_PREFERENCES`.

---

## Phase 4 - Collecting writing samples

You cannot write `voice.md` from a description. People describe their writing as
"professional and friendly" and then send four-word replies with no greeting. Get
the real thing.

Ask them to supply, for **each audience identified in Phase 2**, three to five
real things they have written and sent. Tell them exactly what to send:

- Sent emails, pasted whole, including the greeting and the sign-off. The sign-off
  is half the signal and it is the part people trim.
- At least one where they said no, or restated a policy, or held a line. Warmth is
  easy to imitate; firmness is not, and it is where a bad draft does real damage.
- At least one short reply, two or three lines. Most messages are short, and a
  voice guide built only from long ones will produce drafts that overstay.
- If a lane has its own written artifacts, ask for those too. Feedback on someone's
  work, an announcement, a memo, a proposal, a status update, a post. Whatever that
  lane actually produces.

They can paste into the chat or drop files into `writing-samples/`. Point them at
`writing-samples/README.md` for the naming convention, and tell them `writing-samples/` is
gitignored so nothing they drop there gets committed.

Before reading anything, say plainly: you will read these to extract conventions
only, they stay on this machine, and nothing in them will be quoted outside this
repo. If a sample contains something they would rather you not retain, tell them to
redact it before pasting; you cannot unread it.

Then ask, separately, because samples will not show it:

10. Anything in their writing they know is a tic and want suppressed?
11. Anything an assistant has drafted for them before that sounded wrong, and what
    was wrong with it?

Wait for the samples. Do not proceed to Phase 5 with fewer than three, and say so
rather than making do. If they insist on proceeding with less, write the guide from
what you have and record the thinness honestly in the Provenance section.

---

## Phase 5 - Deriving the voice

Read every sample. For each, note: greeting, sign-off, paragraph length, sentence
length, contractions, exclamation points, capitalization habits, list style, use of
bold and backticks, any non-ASCII characters, and any phrase that appears more than
once.

Then run the mechanical checks, because these produce rules the assistant can
actually verify it obeyed:

```bash
LC_ALL=C grep -n '[^ -~]' writing-samples/* 2>/dev/null | head -40
```

Anything that prints is a character outside plain ASCII: an em-dash, a smart
quote, an ellipsis, an emoji. Count what kinds you find and how often, because
"three smart quotes pasted in from a PDF" and "em-dashes in every message" are
different findings that produce opposite rules.

If the samples are clean ASCII, the strict character-set rule is real and belongs
in the file. If they are full of em-dashes and smart quotes, say so and write the
opposite rule. Do not impose a rule the samples contradict, and do not skip the
question of which they want going forward: a person who types smart quotes by
accident may still want drafts without them. Ask.

Now write `voice.md`. Rules:

- Every rule traceable to a sample or to something they said outright.
- Quote their actual phrases verbatim. Paraphrase kills the thing that makes a
  phrase recognizable as theirs.
- Where the samples are silent on a heading, write `not enough signal yet` under
  it. Do not fill a heading to make the document look complete.
- Fill the Provenance section with what you read, by audience and count.

Then test it before you claim it works. Pick a realistic situation in each lane,
draft a short message against the guide, and show them side by side with one of
their own samples. Ask the only question that matters: does this sound like you?
Revise the guide, not just the draft, until the answer is yes. A voice guide that
has never produced a draft is untested.

Fills, all of them in `voice.md`: `AUDIENCE_COUNT`, `AUDIENCE_LIST`,
`CHARACTER_SET_RULES`, `TONE_RULES`, `REGISTER_BY_AUDIENCE`, `GREETINGS`,
`GREETINGS_TO_AVOID`, `SIGNOFFS`, `FORMATTING_CONVENTIONS`, `GRAMMAR_RULES`,
`COMMON_PHRASES`, `DOMAIN_VOICE_SECTIONS`, `THINGS_TO_AVOID`, `SAMPLE_COUNT`,
`SAMPLE_INVENTORY`, `SETUP_DATE`.

---

## Phase 6 - Platforms

Do not ask them what is connected. Find out, then report.

For each channel - email, chat, files, calendar, web, CRM, recurring tasks - try
the tool or check the connector status, and record what actually came back. A
connector that is listed but errors is not live.

Then write the `PLATFORMS` block in `CLAUDE.md` as bullets that say which are live
and which are not, each dead one carrying its own instruction to ask and then
revise the line. Tell them which ones are missing and what to connect.

Also ask where working files live on this machine, and which directories are other
projects with their own rules that this assistant should write into rather than
duplicate.

Fills: `PLATFORMS`, and the "out of scope, lives in X" clauses in `LANE_SCOPE`.

---

## Phase 7 - Domain notes

For each lane, ask:

1. Vocabulary an outsider would get wrong. Internal names for things, acronyms,
   the difference between two things that sound alike.
2. The systems of record. Which document is canonical for which kind of fact, and
   where it lives. Ask explicitly whether older versions of those documents are
   lying around, because the rule "always cite the most recent" only helps if the
   assistant knows to look for it.
3. Anything with a URL the assistant will need: sites, dashboards, portals.
4. What should **not** be loaded into context by default. A large canonical
   document that is only occasionally relevant gets a pointer, not an `@import`.

Fills: `DOMAIN_NOTES`.

---

## Phase 8 - Seed the knowledge graph

The assistant ships with a working knowledge graph in `kb/` (see the
`knowledge-graph` and `knowledge-graph-maintain` skills). It starts with a few pages
about how the assistant works. This phase adds what the interview taught you, so the
first real session already knows who and what matters. Ask nothing new: everything
here comes from answers already recorded in `.claude/setup/answers.md`.

1. `kb/kb build`. On a fresh clone this copies `kb/seed/` into `kb/wiki/` and must
   print `RESULT: PASS`.
2. Add pages, following the page contract in the `knowledge-graph-maintain` skill:
   - the principal (topic `People`): roles, timezone, how to address them
   - one page per lane (topic `Lanes`): what lands there, what does not and where it
     lives instead, who is downstream
   - one page per key person from Phase 2 (topic `People`): role and the one clause
     of context they gave, and the lane they belong to
   - one source page per system of record from Phase 7, with its locator, and a line
     on which facts it is canonical for
   - organizations and projects that came up by name (topic `Organizations` or
     `Projects / <lane>`)
   - a `judgment` page for each hard rule from Phase 3 that the seed pages do not
     already cover (topic `Assistant / Working rules`). Where a seed judgment already
     says it, such as "Draft, never send", link to that page instead of adding another.
3. Link every page with a reason: each person to their lane and organization, each
   lane to its systems of record, each judgment to the lane it governs. Add each new
   page under the right heading in `kb/wiki/index.md`.
   Cite the identity file each fact was written into by linking its seed source page:
   the principal and key people cite `[[Principal profile]]` (`user.md`); lanes,
   organizations, systems of record and hard rules cite `[[Standing instructions]]`
   (`CLAUDE.md`); working rules cite `[[Operating contract]]` (`operating.md`). Never
   cite `.claude/setup/answers.md`; it may be deleted. A system of record named without
   a path or URL gets the name and place as its locator, marked unconfirmed in its
   Summary.
4. Record only what they told you. Where they skipped, leave the page out rather than
   guess. No credentials, account numbers, IDs, or health details.
5. `kb/kb build` must print `RESULT: PASS`, and `kb/kb health` should show no orphans
   and no page without a source. Then show them the graph: in the desktop app, start
   the `knowledge-graph` preview from `.claude/launch.json`; in a terminal,
   `kb/kb view --open`. Tell them in two lines what is in it and that it grows as
   they work.
6. Ask whether their copy of this repo is private. If it is, offer to delete the
   `kb/wiki/` line from `.gitignore` so the graph is version controlled. If it is
   public, keep the line; the graph holds personal details.

---

## Phase 9 - Write, verify, report

1. Write all six files.

2. Strip the instructional HTML comments from the files you filled in. They were
   scaffolding for you, and every line of them costs context on every future turn.
   Do this before step 3, because the comments themselves contain example
   placeholders and will trip the check. The worked examples under
   `.claude/identity/examples/` are not loaded at session start, so leave them
   alone.

3. Verify no placeholder survived:

```bash
grep -rn '{{' CLAUDE.md .claude/identity/*.md
```

   This must return nothing. If it returns something, you missed a question; go
   back and ask it rather than inventing a value. Never satisfy this check by
   deleting a placeholder you could not answer - write `not established yet` in
   its place so the gap stays visible.

4. Verify the character set of your own output, if they chose the ASCII rule:

```bash
LC_ALL=C grep -n '[^ -~]' CLAUDE.md .claude/identity/*.md
```

5. Confirm `CLAUDE.md` still loads the four `@` identity imports and that each
   path exists.

6. Write `.claude/setup/answers.md` with every confirmed answer, so a later
   `/setup review` has something to check against.

7. Tell them what to do next, in a few lines:
   - Start a fresh session, because `CLAUDE.md` loads at session start and the
     current session is still running on the template.
   - Give the assistant a small real task and correct it. The first three
     corrections are worth more than anything in this interview.
   - Re-run `/setup voice` when more writing samples accumulate.
   - Delete `.claude/identity/examples/` if they want the repo lean, or keep it as
     a reference for the next revision.

8. Ask once whether to commit. Do not commit unprompted, and do not add assistant
   attribution or co-author trailers to the commit if they say yes.

---

## Phase 10 - The standing invitation

Last message. Tell them the identity files are meant to be edited, that the
assistant is expected to update them when corrected, and that the fastest way to
improve it is to say "put that in your operating file" the moment something is
wrong. An assistant that never gets corrected is an assistant that never gets
better.
