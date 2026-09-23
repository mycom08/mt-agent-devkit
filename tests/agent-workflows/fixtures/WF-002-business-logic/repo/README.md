# Shipping fee fixture

This small Python repository is the frozen starting point for WF-002. It uses
only the standard library and has no service, network, or credential dependency.

Run the existing suite from this directory:

```text
python -m unittest discover -s tests -v
```

The `test_standard_at_threshold` failure is seeded intentionally. The story
defines the required behavior. The benchmark runner should copy this directory
into a fresh, isolated working directory for each run.
