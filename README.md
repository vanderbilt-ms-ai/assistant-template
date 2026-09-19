# Personal assistant template

A template repository for a Claude Code assistant that works for one person across
several lanes of their life. Clone it, run `/setup`, and answer questions for
twenty minutes. What comes out is an assistant with a named identity, a written
contract about what it may and may not do, and a style guide derived from your own
writing so it can draft in your voice.

This is not an agent framework and it does not ship any code. It is a set of
standing instructions, structured so that the parts that generalize stay put and
the parts that are about you get filled in.

## Quickstart

```bash
git clone <this-repo> my-assistant && cd my-assistant
```

Gather three to five real things you have written and sent, for each audience you
write to. Sent emails are ideal. See `writing-samples/README.md` for what makes a good
sample and why the short ones and the ones where you said no matter most.

Then open the directory in Claude Code and run:

```
/setup
```

Start a fresh session when it finishes. `CLAUDE.md` is read at session start, so
the session that set it up is still running on the template.

## What is in here

```
CLAUDE.md                        standing rules, loaded every session
.claude/identity/soul.md         character and moral compass
.claude/identity/persona.md      how the assistant talks to you
.claude/identity/operating.md    what it must and must not do
.claude/identity/user.md         who you are
.claude/identity/voice.md        how you write, so it can draft as you
.claude/identity/examples/       the same six files, filled in for a fictional person
.claude/commands/setup.md        the guided setup interview
.claude/claude-md-guide.md       how to keep CLAUDE.md from rotting
writing-samples/                 your own sent writing (gitignored)
```

Everything in `{{DOUBLE_BRACES}}` is a placeholder. When setup is done, this
returns nothing:

```bash
grep -rn '{{' CLAUDE.md .claude/identity/*.md
```

## Why the identity is split into four files

They answer different questions and they change at different rates.

- **soul.md** is character and ethics. Written once, edited almost never. If you
  find yourself rewriting it monthly, something is in the wrong file.
- **persona.md** is how the assistant sounds when it talks to you. Direct or
  chatty, opinionated or neutral, terse or thorough.
- **operating.md** is the contract. Draft versus send, what needs approval, how it
  handles tools and uncertainty. This is the file that grows, because every time
  the assistant gets something wrong the fix belongs here.
- **user.md** is its model of you. What you value, what annoys you, who else shows
  up in your week.

And separately:

- **voice.md** is how *you* write, for when the assistant writes as you. This is a
  different thing from all four above, and conflating it with `persona.md` is the
  most common way these setups go wrong. The assistant talking to you and the
  assistant drafting an email you will sign are two different registers.

## The defaults worth knowing about

Setup will offer to keep, loosen, or tighten each of these. They are defaults, not
dogma, but each one exists because the failure it prevents is expensive.

- **Draft, never send.** Nothing leaves the machine under your name without you
  pressing send. Including routine replies. Including things you already approved.
- **Never assert what another person did, thought, or will notice.** Ask a question
  instead. A question can be answered "none"; an assertion cannot be unread.
- **A tool result is the only evidence there is.** If a call failed, that gets said,
  not papered over with a plausible number.
- **Verify before claiming done.** A structural check is not proof.
- **The assistant updates its own files when corrected**, and tells you it did.

## After setup

The first three corrections you give it are worth more than the whole interview.
When something comes out wrong, say so and tell it to write the fix into
`operating.md`. That is the loop this repo is built around.

Re-run `/setup voice` when you have accumulated more writing samples, and
`/setup platforms` when you connect or lose a tool. `/setup review` reads the
identity files back and reports what has gone thin or stale.
