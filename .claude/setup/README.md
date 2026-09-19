# .claude/setup/

Scratch space for the `/setup` command.

`answers.md` is written here as the interview progresses, one section per phase. It
is gitignored, because it holds personal details. It exists for two reasons:

1. **Resumability.** `/setup resume` reads it and skips the phases already answered.
2. **Review.** `/setup review` checks the identity files against it and reports what
   is thin, stale, or contradictory.

Delete it when setup is done if you would rather not keep a second copy of those
answers on disk. You lose nothing but the ability to run `/setup review`.
