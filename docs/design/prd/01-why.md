# PRD 01: Why — Problem Statement and Motivation

## TLDR

Corrections die in chat. Standing rules are maintained by hand. Reflection produces paragraphs nobody re-reads. CauterRule automates the extract → test → promote loop so every failure becomes a tested, reusable rule — and ships with the DX, corpus, benchmarks, and ecosystem surface to make it real from day one.

## The Gap

Every agent fails. The difference between a mediocre agent and a great one is not that the great one never fails — it is that the great one stops making the *same* failure twice.

Current state:

1. **Corrections die in chat.** A human tells an agent "next time, do Y." That correction lives in the chat thread, which is never revisited. Next session starts fresh.
2. **Standing rules are maintained by hand.** The only people with working institutional knowledge built it the slow way — watching failures and writing rules manually. 134 rules, all hand-written, all human-maintained.
3. **Reflection is context bloat.** Frameworks ship a `reflect` step that appends a paragraph of prose. That paragraph is never read again, never tested, never promoted.
4. **No verification before a rule goes live.** Even when someone writes a rule, nothing verifies it. A rule that fixes one failure but breaks three prior successes is worse than no rule.
5. **No corpus, no benchmarks, no proof.** Even if you build a learning loop, you cannot prove it works without a test corpus, replay benchmarks, and field tests. Nobody ships those with the tool.

## The Solution

CauterRule automates the loop:

1. **Extract** — After every failure, an LLM reads the trajectory and proposes a *when X, do Y* rule. Multi-pass extraction with draft tournaments picks the best candidate, not just the first.
2. **Test** — Replay against historical scenarios: past failures + past successes. The replay engine is deterministic, visualized, and benchmarked against a tiered corpus.
3. **Promote** — Only rules that survive testing enter the standing-rules store, with full provenance, conflict detection, and linter validation.

But the loop is only the core. CauterRule also ships:

- **Day-one interop** — export rules to `.cursorrules`, `CLAUDE.md`, `AGENTS.md`, `.windsurfrules`, `aider.conf.yml`; import existing conventions and chat corrections
- **MCP server** — any MCP-compatible agent gets rules with zero code changes
- **Bundled rule packs** — `pack-git` ships with the install; rules work out of the box
- **`@cauterule.watch` adapter** — add learning to any Python agent in 5 lines
- **Corpus & benchmarks** — tiered corpus, gold rule families, counterexample/near-miss/redaction corpora, model bake-off harness
- **Field test program** — coding, long-horizon, noisy, cold-start, cross-session, regression, multi-environment
- **Scale & reliability** — replay throughput, injection latency, conflict explosion, concurrent ingestion, cost benchmarks
- **Safety & adversarial** — prompt injection corpus, misleading root-cause, unsafe directive blocking, data poisoning, instruction leakage
- **Full CLI surface** — 25+ commands including `demo`, `rewind`, `review`, `counterfactual`, `story`, `health`, `validate`, `conflicts`, `explain`
- **Distribution** — PyPI, Homebrew, Docker, standalone binary

The result: an agent whose knowledge compounds, backed by evidence, and a tool that is usable, measurable, and shareable from day one.