"""Rule matcher with semantic similarity scoring.

Replaces pure substring/token-overlap heuristics with a single scoring
function that combines:

1. Exact normalized-substring match (score 1.0 — preserves legacy behavior).
2. Weighted token overlap — informative tokens (error codes, tool names,
   paths, quoted strings) weigh more than common words.
3. Bigram overlap — captures multi-word concepts even with rewording.
4. Domain alias expansion — small paraphrase map for common failure
   vocabulary (e.g. "non-fast-forward" ~ "remote contains work").

``rule_matches`` keeps its ``(candidate, trajectory) -> bool`` signature;
``match_score`` exposes the underlying float for corpus-aware thresholds
and inconclusive attribution.
"""

from __future__ import annotations

import re
import string
from typing import Any

from cauterule.models.candidate import CandidateRule
from cauterule.models.trajectory import Trajectory

# Triggers shorter than this are considered too generic to match reliably.
_MIN_TRIGGER_WORDS = 1

# Degenerate trigger pattern — step identifiers like "step_1", "step 2".
_DEGENERATE_TRIGGER_RE = re.compile(r"^step[_\s]*\d+$", re.IGNORECASE)

# Default similarity threshold for a match. Corpus-aware callers may pass
# a different threshold (see issue #420).
DEFAULT_THRESHOLD = 0.6

# Corpus-aware thresholds (issue #420).
# Curated corpora have clean failure signatures → stricter.
# Raw corpora are noisy → looser. Cross-repo needs transfer.
STRATEGY_THRESHOLDS: dict[str, float] = {
    "strict": 0.70,
    "loose": 0.35,
    "semantic": 0.60,
    "transfer": 0.40,
}

CURATED_CORPORA: frozenset[str] = frozenset(
    {"golden", "successes", "nearmiss", "noisy", "corrections"}
)

# OMLX/local models use a lower curated threshold — small models produce
# broader trigger phrasings that don't match as tightly at 0.70.
# Nearmiss is safety-critical: keep 0.70 to reject "wrong failure" matches.
OMLX_THRESHOLD = 0.65
OMLX_NEARMISS_THRESHOLD = 0.70

# Corpora that must keep the strict threshold even for OMLX (safety-critical).
NEARMISS_CORPORA: frozenset[str] = frozenset({"nearmiss"})

def strategy_for_corpus(corpus_name: str) -> str:
    """Return recommended matcher strategy for *corpus_name*."""
    lower = corpus_name.lower()
    if "sibling" in lower or "cross-repo" in lower:
        return "transfer"
    if "raw" in lower:
        return "loose"
    # Curated corpora and anything else default to strict/semantic.
    # Use strict for curated with clean signatures, semantic otherwise.
    base = corpus_name.split("/")[-1].strip().lower()
    if base in CURATED_CORPORA:
        return "strict"
    return "semantic"


def threshold_for_corpus(corpus_name: str, omlx: bool = False) -> float:
    """Return similarity threshold for *corpus_name*.

    Args:
        corpus_name: Corpus type name.
        omlx: If True, use lower curated threshold (0.65) for local OMLX models.
              Nearmiss keeps 0.70 (safety-critical — reject "wrong failure" matches).
    """
    threshold = STRATEGY_THRESHOLDS[strategy_for_corpus(corpus_name)]
    if omlx and threshold == STRATEGY_THRESHOLDS["strict"]:
        base = corpus_name.split("/")[-1].strip().lower()
        if base in NEARMISS_CORPORA:
            threshold = OMLX_NEARMISS_THRESHOLD
        else:
            threshold = OMLX_THRESHOLD
    return threshold

# Common words carry no matching signal.
_STOPWORDS: frozenset[str] = frozenset(
    {
        "a", "an", "the", "and", "or", "but", "if", "then", "else", "when",
        "what", "which", "who", "whom", "this", "that", "these", "those",
        "am", "is", "are", "was", "were", "be", "been", "being", "have",
        "has", "had", "having", "do", "does", "did", "doing", "will",
        "would", "shall", "should", "can", "could", "may", "might", "must",
        "ought", "to", "of", "in", "for", "on", "by", "with", "about",
        "into", "through", "during", "before", "after", "above", "below",
        "up", "down", "out", "off", "over", "under", "again", "further",
        "once", "here", "there", "all", "any", "both", "each", "few",
        "more", "most", "other", "some", "such", "only", "own", "same",
        "so", "than", "too", "very", "just", "also", "not", "no", "nor",
        "as", "at", "from", "it", "its", "you", "your", "we", "they",

    }
)

_PUNCT_RE = re.compile(f"[{re.escape(string.punctuation)}]")
_WS_RE = re.compile(r"\s+")

# Domain paraphrase map: canonical key -> set of equivalent phrases.
# Expansion is one-directional (trigger side) and conservative.
_DISTINCTIVE_PHRASES: frozenset[str] = frozenset(
    {
        "non-fast-forward", "merge conflict", "permission denied",
        "connection refused", "module not found", "modulenotfounderror",
        "assertion error", "assertionerror", "type error", "typeerror",
        "syntax error", "syntaxerror", "import error", "importerror",
        "key error", "keyerror", "value error", "valueerror",
        "index error", "indexerror", "attribute error", "attributeerror",
        "file not found", "filenotfounderror", "out of memory", "oomkilled",
        "rate limit", "rate limit exceeded", "deadline exceeded",
        "state lock", "element not found", "nosuchelementexception",
        "stale element", "staleelementreferenceexception",
        "timeout", "timed out", "connection timeout",
        "access denied", "not found", "notfound", "conflict",
        "build failed", "test failed", "deploy failed",
        "no such file", "directory not empty",
        "unknown host", "could not resolve",
        "unable to find", "unable to connect",
        "no matches for kind", "cr not found",
        "resource not found", "not authorized",
        "exit code", "non-zero exit", "process exited",
        "ssl certificate", "certificate verification", "ssl verification",
        "nxdomain", "dns resolution", "name resolution",
        "npm build", "npm install", "npm ERR",
        "network connection", "network unreachable",
        "cache miss", "cache not found",
        "browser alert", "unexpected alert",
        "no such frame", "frame not found", "switch to frame",
        "checkout", "delete branch", "branch checked out",
        "flaky", "intermittent", "intermittent failure",
    }
)

_LONG_PHRASE_THRESHOLD = 8

# Domain paraphrase map: canonical key -> set of equivalent phrases.
# Expansion is one-directional (trigger side) and conservative.
_ALIASES: dict[str, frozenset[str]] = {
    "non-fast-forward": frozenset(
        {"remote contains work", "updates were rejected", "fetch first", "pull first", "behind remote"}
    ),
    "non fast forward": frozenset(
        {"remote contains work", "updates were rejected", "fetch first", "pull first", "behind remote"}
    ),
    "push rejected": frozenset({"updates were rejected", "non-fast-forward"}),
    "merge conflict": frozenset({"conflicting changes", "automatic merge failed", "merge failed"}),
    "import error": frozenset({"no module named", "modulenotfounderror"}),
    "module not found": frozenset({"no module named", "modulenotfounderror"}),
    "connection refused": frozenset({"could not connect", "network unreachable", "connection reset"}),
    "out of memory": frozenset({"oomkilled", "memory exhausted", "killed"}),
    "permission denied": frozenset({"operation not permitted", "access denied", "eacces"}),
    "file not found": frozenset({"no such file", "enoent", "does not exist"}),
    "timeout": frozenset({"timed out", "deadline exceeded", "took too long"}),
    "version conflict": frozenset({"dependency resolver conflict", "dependency conflict"}),
    "package not found": frozenset({"unable to find ", "no package matching", "libpq-dev not found"}),
    "state lock": frozenset({"conditionalcheckfailedexception", "state locked", "error acquiring"}),
    "rate limit": frozenset({"429", "too many requests", "rate limit exceeded"}),
    "assertion error": frozenset({"assertionerror", "assertion failed"}),
    "kubectl apply": frozenset({"no matches for kind", "unable to recognize"}),
    "crd not found": frozenset({"no matches for kind", "unrecognized resource"}),
    "not found": frozenset({"no matches for kind", "does not exist", "not found"}),
    "deploy timeout": frozenset({"deployment exceeded", "timed out", "timeout"}),
    "health check": frozenset({"health check", "rollout timed out", "timed out"}),
    "times out": frozenset({"timeout", "timed out", "deadline exceeded"}),
    "ssl certificate": frozenset({"ssl", "certificate", "verification", "cert"}),
    "certificate verification": frozenset({"ssl", "certificate", "cert"}),
    "dns resolution": frozenset({"nxdomain", "dns", "name resolution", "resolve"}),
    "nxdomain": frozenset({"dns", "domain not found", "name resolution"}),
    "npm build": frozenset({"npm", "build", "webpack", "module not found"}),
    "npm install": frozenset({"npm", "install", "package", "dependency"}),
    "network connection": frozenset({"connection", "network", "unreachable", "reset"}),
    "cache miss": frozenset({"cache", "not found", "missing", "restore"}),
    "browser alert": frozenset({"alert", "unexpected", "dismiss", "popup"}),
    "frame not found": frozenset({"no such frame", "frame", "switch", "iframe"}),
    "delete branch": frozenset({"checkout", "branch", "checked out", "delete"}),
    "flaky": frozenset({"intermittent", "retry", "transient", "intermittent failure"}),
    # Qwen alias expansion (#492): Qwen produces more abstract trigger phrasings
    # that the matcher needs alias support to match.
    "command fails": frozenset({"exit code", "non-zero exit", "return code", "process exited"}),
    "tool fails": frozenset({"tool error", "command error", "execution error", "operation failed"}),
    "authentication error": frozenset({"auth failed", "permission denied", "unauthorized", "login failed"}),
    "not found error": frozenset({"no such file", "not found", "missing", "does not exist"}),
    "pipeline fails": frozenset({"ci failed", "build failed", "deploy failed", "test failed", "stage failed"}),
}


def _normalize(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    lowered = text.lower()
    no_punct = _PUNCT_RE.sub(" ", lowered)
    return _WS_RE.sub(" ", no_punct).strip()


def _tokenize(text: str) -> set[str]:
    """Return lowercase word tokens from *text* (legacy behavior)."""
    return {w for w in text.lower().split() if len(w) > 1}


def _stem(token: str) -> str:
    """Light suffix stripping for tokens longer than 4 chars."""
    if len(token) <= 4:
        return token
    for suffix in ("ing", "ed", "es", "ly", "s"):
        if token.endswith(suffix) and len(token) - len(suffix) >= 3:
            return token[: -len(suffix)]
    return token


def _content_tokens(text: str) -> set[str]:
    """Normalized, stemmed, stopword-free tokens carrying match signal."""
    return {_stem(w) for w in _normalize(text).split() if w not in _STOPWORDS and len(w) > 1}


def _bigrams(tokens: list[str]) -> set[tuple[str, str]]:
    """Adjacent token pairs in order."""
    return set(zip(tokens, tokens[1:], strict=False))


def _ordered_content_tokens(text: str) -> list[str]:
    """Content tokens preserving order (for bigram extraction)."""
    return [_stem(w) for w in _normalize(text).split() if w not in _STOPWORDS and len(w) > 1]


def _expand_aliases(normalized_trigger: str) -> set[str]:
    """Return extra content tokens from matching alias phrases."""
    extra: set[str] = set()
    for key, phrases in _ALIASES.items():
        if key in normalized_trigger:
            for phrase in phrases:
                extra.update(_content_tokens(phrase))
    return extra


def _build_haystack(trajectory: Trajectory, include_input: bool = True) -> str:
    """Build normalized haystack text from a trajectory."""
    parts: list[str] = [trajectory.task]
    if trajectory.failure_class:
        parts.append(trajectory.failure_class)
    for step in trajectory.steps:
        if step.error:
            parts.append(step.error)
        if step.output:
            parts.append(step.output)
        if include_input and step.input:
            parts.append(step.input)
    return _normalize(" ".join(parts))


def match_score(candidate: CandidateRule, trajectory: Trajectory) -> float:
    """Return trigger similarity in [0.0, 1.0] for *candidate* vs *trajectory*.

    Score components:
    - 1.0 for exact normalized-substring match.
    - Otherwise a weighted blend: 0.6 * weighted-token-F1 + 0.4 * bigram-recall,
      where alias-expanded tokens count at half weight.
    """
    trigger = candidate.when.trigger
    if not trigger or not trigger.strip():
        return 0.0

    norm_trigger = _normalize(trigger)
    if not norm_trigger:
        return 0.0

    # --- Exact normalized-substring match → score 1.0 ---
    haystack = _build_haystack(trajectory)
    if norm_trigger in haystack:
        return 1.0

    # --- Token-based scoring ---
    trigger_content = _content_tokens(norm_trigger)
    haystack_content = _content_tokens(haystack)

    if not trigger_content:
        return 0.0

    # Phrase-level paraphrase: if any alias phrase appears verbatim in
    # the haystack, that is strong equivalence evidence.
    alias_phrase_hit = any(
        _normalize(phrase) in haystack
        for key, phrases in _ALIASES.items()
        if key in norm_trigger
        for phrase in phrases
    )

    # Direct hit tokens
    direct_hit = trigger_content & haystack_content
    # Alias expansion
    alias_tokens = _expand_aliases(norm_trigger)
    alias_hit = alias_tokens & haystack_content

    # Weighted token F1: direct hits count 1.0, alias hits count 0.5.
    weighted_hit = len(direct_hit) + 0.5 * len(alias_hit)
    weighted_trigger = len(trigger_content) + 0.5 * len(alias_tokens)
    if weighted_trigger == 0:
        token_f1 = 0.0
    else:
        recall = weighted_hit / weighted_trigger
        token_f1 = recall  # precision shares denominator, so this is just recall for now

    # Bigram recall (adjacent content-token pairs)
    trigger_bigrams = _bigrams(_ordered_content_tokens(norm_trigger))
    haystack_bigrams = _bigrams(_ordered_content_tokens(haystack))
    bigram_recall = 0.0
    if trigger_bigrams:
        bigram_recall = len(trigger_bigrams & haystack_bigrams) / len(trigger_bigrams)

    score = 0.6 * token_f1 + 0.4 * bigram_recall
    # Phrase-level paraphrase floors at 0.70 (alias text matches haystack verbatim).
    if alias_phrase_hit:
        score = 0.70
    elif alias_hit and score < DEFAULT_THRESHOLD:
        score = DEFAULT_THRESHOLD

    # Substring fallback: if trigger contains a distinctive error phrase
    # that appears verbatim in the haystack, floor the score at 0.70 so
    # it passes both default and curated thresholds.
    if score < 0.70 and len(norm_trigger) >= _LONG_PHRASE_THRESHOLD:
        raw_lower = trigger.lower()
        for phrase in _DISTINCTIVE_PHRASES:
            if phrase in raw_lower and _normalize(phrase) in haystack:
                score = 0.70
                break

    return round(score, 4)


def extract_trigger_domain(trigger: str) -> str | None:
    """Extract the primary domain/tool from a trigger string.

    Returns the first recognizable tool or error domain keyword, or None.
    Used for domain-mismatch detection (#487).
    """
    tl = trigger.lower()
    for domain in ("git", "docker", "pip", "pytest", "kubectl",
                   "terraform", "api", "browser", "python", "ssh",
                   "npm", "deploy", "ci", "test"):
        if domain in tl:
            return domain
    return None


def check_domain_mismatch(
    candidate: CandidateRule, trajectory: Trajectory
) -> bool:
    """Return True if the candidate trigger and trajectory are in different domains.

    A mismatch means the rule's primary tool/domain does not align with the
    trajectory's failure_class (e.g. trigger mentions "docker" but reference
    trajectory has failure_class="git/push/...").
    """
    trigger_domain = extract_trigger_domain(candidate.when.trigger)
    traj_domain: str | None = None
    if trajectory.failure_class:
        traj_domain = trajectory.failure_class.split("/")[0].lower()
    if trigger_domain is None or traj_domain is None:
        return False
    return trigger_domain != traj_domain


def match_detail(candidate: CandidateRule, trajectory: Trajectory) -> dict[str, Any]:
    """Return match diagnostics for attribution and debugging."""
    trigger = candidate.when.trigger
    norm_trigger = _normalize(trigger)
    haystack = _build_haystack(trajectory)
    trigger_tokens = _content_tokens(trigger)
    haystack_tokens = _content_tokens(haystack)
    return {
        "score": match_score(candidate, trajectory),
        "exact_substring": bool(norm_trigger) and norm_trigger in haystack,
        "trigger_tokens": sorted(trigger_tokens),
        "matched_tokens": sorted(trigger_tokens & haystack_tokens),
        "alias_tokens": sorted(_expand_aliases(norm_trigger) - trigger_tokens),
        "trigger_word_count": len(_tokenize(trigger)),
        "content_token_count": len(trigger_tokens),
    }


def _context_matches(candidate: CandidateRule, trajectory: Trajectory) -> bool:
    """Return True if every context item matches (normalized containment)."""
    haystack = _build_haystack(trajectory)
    for ctx in candidate.when.context:
        norm_ctx = _normalize(ctx)
        if not norm_ctx or norm_ctx not in haystack:
            return False
    return True


def rule_matches(
    candidate: CandidateRule,
    trajectory: Trajectory,
    threshold: float = DEFAULT_THRESHOLD,
) -> bool:
    """Return True if *candidate* matches *trajectory*.

    Matching strategy:
    1. Build a normalized haystack from task, failure_class, and step
       input/output/error.
    2. Score the trigger with :func:`match_score`; require ``score >= threshold``.
    3. Require every context item to match (normalized containment).
    4. Reject overly generic triggers unless context disambiguates.

    Case-insensitive throughout. The ``threshold`` parameter enables
    corpus-aware calibration (see issue #420).
    """
    trigger = candidate.when.trigger
    if not trigger or not trigger.strip():
        return False

    # Reject degenerate triggers (step identifiers like "step_1").
    if _DEGENERATE_TRIGGER_RE.match(trigger.strip().lower()):
        return False

    trigger_words = _tokenize(trigger)

    # Reject overly generic triggers unless context narrows them.
    if len(trigger_words) < _MIN_TRIGGER_WORDS and not candidate.when.context:
        return False

    if match_score(candidate, trajectory) < threshold:
        return False

    return _context_matches(candidate, trajectory)


def is_near_miss(candidate: CandidateRule, trajectory: Trajectory) -> bool:
    """Return True if trigger matches but not all context (partial)."""
    trigger = candidate.when.trigger
    if not trigger or not trigger.strip():
        return False

    if match_score(candidate, trajectory) < DEFAULT_THRESHOLD:
        return False

    # If context exists and not all context matches, it's near miss.
    if candidate.when.context:
        haystack = _build_haystack(trajectory, include_input=False)
        matched_ctx = sum(1 for ctx in candidate.when.context if _normalize(ctx) in haystack)
        if 0 < matched_ctx < len(candidate.when.context):
            return True
    return False
