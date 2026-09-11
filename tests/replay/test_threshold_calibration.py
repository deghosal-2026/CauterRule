"""Regression guard for matcher threshold calibration (#691).

Runs the fixed golden/nearmiss sample through the production matcher at the
shipped thresholds and asserts precision/recall do not fall below the
committed baseline.  This is the fast CI signal that would have caught the
#492 alias regression before a full field-test sweep.
"""

from cauterule.replay.calibration import (
    evaluate_threshold,
    load_calibration_pairs,
    sweep_thresholds,
)
from cauterule.replay.matcher import (
    OMLX_NEARMISS_THRESHOLD,
    OMLX_THRESHOLD,
    STRATEGY_THRESHOLDS,
)

# Baseline observed on the committed sample (see
# docs/field-test/v0.3.0/threshold-calibration.md):
#   strict 0.70 / omlx 0.65 → precision 1.00, recall 0.50
_MIN_PRECISION = 0.90
_MIN_RECALL = 0.45


def test_calibration_sample_has_positives_and_negatives() -> None:
    pairs = load_calibration_pairs()
    assert sum(1 for p in pairs if p.expected_match) == 20
    assert sum(1 for p in pairs if not p.expected_match) > 100


def test_strict_threshold_meets_precision_recall_baseline() -> None:
    metrics = evaluate_threshold(STRATEGY_THRESHOLDS["strict"])
    assert metrics.precision >= _MIN_PRECISION, metrics
    assert metrics.recall >= _MIN_RECALL, metrics


def test_omlx_curated_threshold_meets_precision_baseline() -> None:
    metrics = evaluate_threshold(OMLX_THRESHOLD)
    assert metrics.precision >= _MIN_PRECISION, metrics
    assert metrics.recall >= _MIN_RECALL, metrics


def test_omlx_nearmiss_threshold_keeps_precision() -> None:
    metrics = evaluate_threshold(OMLX_NEARMISS_THRESHOLD)
    assert metrics.precision >= _MIN_PRECISION, metrics


def test_sweep_reports_full_range() -> None:
    metrics = sweep_thresholds()
    assert metrics[0].threshold == 0.50
    assert metrics[-1].threshold == 0.80
