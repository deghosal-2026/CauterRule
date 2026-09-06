# PRD 03: Landscape

## Adjacent Solutions (Researched)

### Letta (f.k.a. MemGPT) — 24.6k stars
- **What:** Platform for stateful agents with memory that can learn and self-improve over time
- **Why it's different:** Letta focuses on general memory — conversations, identity, state persistence. It does not extract structured rules from failures, does not test rules against history, and does not promote based on evidence.
- **Gap it leaves open:** Memory is unstructured text, not tested rules. No extract → test → promote loop. No failure-driven learning.

### LangGraph — 41k stars
- **What:** Low-level orchestration framework for building stateful agents. Durable execution, human-in-the-loop, comprehensive memory (short-term + long-term).
- **Why it's different:** LangGraph's memory is state persistence and retrieval — not behavioral rules. It has no concept of "learn from failure → extract rule → test → promote."
- **Gap it leaves open:** No rule extraction, no replay testing, no promotion gate. Memory is raw state, not institutional knowledge.

### LangChain — 145k stars
- **What:** Agent engineering platform. General-purpose LLM application framework.
- **Why it's different:** LangChain is a framework for building agents, not for learning from their failures. No standing-rule concept.
- **Gap it leaves open:** No failure-driven learning, no rule store, no replay testing.

### Claude Code — 144k stars
- **What:** Agentic coding tool. Terminal-based, understands codebase, handles git workflows.
- **Why it's different:** Claude Code is an agent, not a learning system. It does not extract rules from its own failures.
- **Gap it leaves open:** Each session starts fresh. Corrections in chat are lost. No standing rules.

### `.cursorrules` / `CLAUDE.md` / `AGENTS.md` (Static Convention Files)
- **What:** Hand-written convention files that agents read at startup
- **Why it's different:** These are static — humans write them, humans maintain them. They are not extracted from failures, not tested, and not versioned with provenance.
- **Gap it leaves open:** CauterRule **exports to** these formats in v0.1.0, turning tested rules into drop-in convention files. And it **imports from** them, converting existing conventions into testable rules. It also imports from chat history — parsing past corrections given to agents.

### CrewAI — 58k stars
- **What:** Framework for orchestrating role-playing, autonomous AI agents
- **Why it's different:** CrewAI focuses on multi-agent collaboration, not on learning from failures
- **Gap it leaves open:** No rule extraction, no replay testing, no promotion gate

## White Space

CauterRule occupies the intersection of:

| Dimension | CauterRule | Everyone Else |
|-----------|-----------|---------------|
| **Learning trigger** | Failure-driven | Generic memory or none |
| **Rule format** | Structured *when X, do Y* | Unstructured prose or raw state |
| **Verification** | Historical replay testing before promotion | None — write and forget |
| **Provenance** | Full chain: source failure → evidence → promotion | None or minimal |
| **Versioning** | Git-based, with rollback | None or append-only |
| **Lifecycle** | Promote → track → retire → supersede → consolidate | Append-only or manual |
| **Sharing** | Rule packs + MCP server (both in v0.1.0) | None |
| **Interop** | Export to `.cursorrules`/`CLAUDE.md`/`AGENTS.md`/`.windsurfrules`/`aider` + import from all + chat history | None |
| **Corpus** | Tiered public corpus + private local mode + gold families + counterexample + adversarial | None |
| **Benchmarks** | Replay throughput, injection latency, conflict scale, cost, model bake-off | None |
| **DX** | CLI (25+ commands), TUI, demo, `@cauterule.watch`, Homebrew, Docker, binary | Varies |

**No existing OSS tool automates the extract → test → promote loop for agent standing rules.** The closest (Letta, LangGraph) provide memory infrastructure but not failure-driven, evidence-based rule promotion. None ship a corpus, benchmarks, or adversarial testing.