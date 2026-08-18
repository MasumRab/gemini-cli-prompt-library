# Compatibility

V7.3 is a derived-output mode that reads existing `analysis_snapshot.json` and `plan.json` and writes downstream outputs (target analysis, root health, stack ordering). It does not require a separate fixture directory; the `fixtures/v73/` directory contains example inputs for testing this mode.

V6.4 provides the base topology audit with multi-root support.
V7.2 adds human-in-the-loop automation (target analysis, root health, stack ordering).
V7.3 is the full pipeline mode combining V6.4 analysis with V7.2 derived outputs.
