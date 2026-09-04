# PRD 01: Why — Problem Statement and Motivation

## TLDR

Corrections die in chat. Standing rules are maintained by hand. Reflection produces paragraphs nobody re-reads. CauterRule automates the extract → test → promote loop so every failure becomes a tested, reusable rule.

## The Gap

Every agent fails. The difference between a mediocre agent and a great one is not that the great one never fails — it is that the great one stops making the *same* failure twice.

Current state:

1. **Corrections die in chat.** A human tells an agent "next time, do Y." That correction lives in the chat thread, which is never revisited. Next session starts fresh.
2. **Standing rules are maintained by hand.** The only people with working institutional knowledge built it the slow way — watching failures and writing rules manually. 134 rules, all hand-written, all human-maintained.
3. **Reflection is context bloat.** Frameworks ship a `reflect` step that appends a paragraph of prose. That paragraph is never read again, never tested, never promoted.
4. **No verification before a rule goes live.** Even when someone writes a rule, nothing verifies it. A rule that fixes one failure but breaks three prior successes is worse than no rule.

## The Solution

CauterRule automates the loop:

1. **Extract** — After every failure, an LLM reads the trajectory and proposes a *when X, do Y* rule
2. **Test** — Replay against historical scenarios: past failures + past successes
3. **Promote** — Only rules that survive testing enter the standing-rules store

The result: an agent whose knowledge compounds. Every failure, instead of being discarded, becomes a tested, reusable rule.