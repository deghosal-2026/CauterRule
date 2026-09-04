# CauterRule

**Automated standing-rule extraction from agent failures.**

Every agent fails. CauterRule ensures they never make the *same* failure twice.

After every failure, CauterRule:
1. **Extracts** a structured *when X, do Y* standing rule from the execution trajectory
2. **Tests** that candidate rule against historical scenarios (past failures + past successes)
3. **Promotes** only rules that survive replay into the agent's permanent rule store

No more corrections dying in chat. No more 134 hand-written standing rules. No more vague reflection paragraphs nobody re-reads. Rules are actionable, tested, and permanent.

---

## Why

The current state of "learning from mistakes" in agent systems is reflection-as-a-paragraph — prose that bloats the context window and is never read again. The manual alternative is 134 standing rules maintained by hand. Both are broken.

CauterRule automates the extract → test → promote loop. Same pattern as CI/CD for code, but for agent behavior: test a rule against the historical regression suite before merging it in.

---

## Project Status

**Pre-release / v0.1.0 in development.** The design spec is documented at `docs/SPEC.md`.

MVP scope:
- Trajectory capture on failure
- LLM extraction of candidate rules (*when X, do Y*)
- Historical replay harness (replay against past failures + successes)
- Promotion gate with pass/fail evidence
- Versioned standing-rules store (YAML, git)
- Rule injection on future matching tasks

---

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│ Trajectory      │ ──> │ Rule Extractor   │ ──> │ Historical Replay │
│ Capture         │     │ (LLM)            │     │ Engine            │
└─────────────────┘     └──────────────────┘     └───────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│ Rule Injection  │ <── │ Standing-Rules   │ <── │ Promotion Gate    │
│ (context prep)  │     │ Store (versioned)│     │ (evidence check)  │
└─────────────────┘     └──────────────────┘     └───────────────────┘
```

---

## License

MIT — see [LICENSE](LICENSE).

