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

## What Makes It Different

| Existing | CauterRule |
|----------|-----------|
| Reflection produces prose nobody re-reads | Produces structured *when X, do Y* rules that are testable and injectable |
| Memory stores hold raw text (Letta/MemGPT) | Rules are tested against history before promotion — evidence-based, not append-only |
| Framework memory is unstructured (LangGraph) | Rules have provenance, versioning, conflict detection, and retirement |
| Standing rules maintained by hand (134 of them) | The agent writes its own rules, tests them, and promotes only what survives |
| `.cursorrules` / `CLAUDE.md` are static files | Rules are living artifacts that grow from real failures, not guesses |

---

## Feature Pillars

| Pillar | What it delivers |
|--------|-----------------|
| **Self-Improving Loop** | The extract → test → promote cycle that no other agent memory tool offers |
| **Framework Adapters** | Plug into LangGraph, CrewAI, PydanticAI, or any custom agent loop |
| **Rule Packs** | Pre-built, shareable rule collections — npm for agent behavioral knowledge |
| **DX & Observability** | CLI, TUI, replay dashboard, metrics — see your agent's knowledge compound |
| **MCP Server** | Expose rules as MCP tools — any MCP-compatible agent gets rules with zero code changes |

---

## Roadmap

| Version | Theme | Key Deliverable |
|---------|-------|-----------------|
| **v0.1.0** | Core Loop | Extract → test → promote in one command. `cauterule demo` runs the full loop in 60 seconds. |
| **v0.1.1** | Framework Adapters | `@cauterule.watch` on any agent function. Adapters for LangGraph, CrewAI, PydanticAI. |
| **v0.2.0** | Intelligence | Conflict detection, retirement, TUI rule browser (`cauterule review`). |
| **v0.3.0** | Rule Packs | Pre-built packs (`pack-git`, `pack-docker`, `pack-deploy`). Export to `.cursorrules` / `CLAUDE.md`. |
| **v0.4.0** | MCP & Integrations | CauterRule MCP server. GitHub Action for PR-based rule promotion. Webhooks. |
| **v0.5.0** | Observability | Replay dashboard, metrics, "what if?" simulation, failure recurrence tracking. |
| **v0.6.0** | Advanced Retrieval | Semantic rule matching, multi-pass extraction, confidence calibration. |
| **v0.7.0** | Multi-Agent | Cross-agent rule transfer, fleet governance, shared rule registries. |

See [docs/design/prd/05-features.md](docs/design/prd/05-features.md) for the full feature breakdown.

---

## Quick Start (Coming Soon)

```bash
pip install cauterule

# Run the demo — seeded failures, 10 rules extracted → tested → promoted
cauterule demo

# Watch your own agent fail and learn
cauterule watch --agent my_agent.py
cauterule list          # browse promoted rules
cauterule review        # TUI for reviewing pending promotions
```

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

**Rule Packs** and **MCP Server** extend the core loop:

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ Rule Packs   │ ──> │ Standing-Rules   │ <── │ MCP Server       │
│ (shareable)  │     │ Store            │     │ (any agent)      │
└──────────────┘     └──────────────────┘     └──────────────────┘
```

---

## Documentation

- [Docs Index](docs/README.md)
- [PRD: Why](docs/design/prd/01-why.md)
- [Feature Breakdown](docs/design/prd/05-features.md)
- [Architecture](docs/design/prd/02-architecture.md)
- [Design Decisions](docs/design/design-decisions.md)
- [Roadmap](docs/design/prd/09-roadmap.md)

---

## License

MIT — see [LICENSE](LICENSE).