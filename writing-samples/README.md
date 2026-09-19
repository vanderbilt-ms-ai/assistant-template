# writing-samples/

Drop your own writing here before running `/setup`, or paste it into the chat when
setup asks. Everything in this directory except this file is gitignored.

## What to put here

For **each audience** your assistant will write to, three to five real things you
actually sent. More is better; three is the floor.

Include:

- **Whole emails.** Greeting and sign-off included. The sign-off is half the signal
  and it is the part people trim when pasting.
- **At least one where you said no**, restated a policy, or held a line. Warmth is
  easy to imitate. Firmness is not, and a draft that gets it wrong does real damage.
- **At least one short reply**, two or three lines. Most messages are short. A voice
  guide built only from long ones produces drafts that overstay.
- **Whatever else that audience gets from you.** Feedback on someone's work, a
  memo, an announcement, a proposal, a status update, a post. If a lane produces a
  particular kind of artifact, it needs samples of that artifact.

## Naming

```
<audience>-<kind>-<n>.md
```

For example:

```
funders-email-1.md
funders-report-1.md
board-memo-1.md
students-feedback-1.md
personal-email-1.md
```

The audience prefix is what lets setup build the "Register by audience" section
rather than averaging everyone together into a voice that fits nobody.

## Redaction

Setup reads these to extract conventions: greetings, sign-offs, sentence shape,
recurring phrases. Nothing in them is quoted outside this repo.

Even so, redact before you drop a file in. Replace names, amounts, and account
details with placeholders if they are sensitive. Conventions survive redaction
perfectly well; `Hi Priya,` and `Hi <name>,` teach the same lesson.

## Refreshing

When a new batch of writing accumulates, add it here and run:

```
/setup voice
```

That re-derives `voice.md` against everything present and updates the Provenance
section with what it read.
