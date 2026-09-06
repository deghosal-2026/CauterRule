# Gold Rule Families Validation — Results

Date: 2026-09-05
Suite: `tests/corpus/test_gold.py`

## Command

```bash
pytest tests/corpus/test_gold.py -v --tb=short
```

## Results

```
============================= test session starts ==============================
platform darwin -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/deghosal/Desktop/code/github/CauterRule
configfile: pyproject.toml
plugins: cov-7.1.0
collected 5 items

tests/corpus/test_gold.py .....                                          [100%]

============================== 5 passed in 0.03s ===============================
```

**Outcome: 5 passed, 0 failed, 0 errors.**

## Test Details

| Test | Status |
|------|--------|
| `test_gold_rule_family_valid` | PASS |
| `test_gold_rule_family_invalid_id` | PASS |
| `test_load_gold_families_missing_dir` | PASS |
| `test_load_gold_families_empty_dir` | PASS |
| `test_load_gold_families_with_files` | PASS |