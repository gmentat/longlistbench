#!/usr/bin/env python3
"""Generate policy-centered single-document multi-hop benchmark cases.

The cases are synthetic public fixtures. Private insurance packets and the
policy-checking report schemas are used only as structural references; no real
customer names, addresses, policy numbers, form wording, or source text are
copied into the generated dataset.
"""

from __future__ import annotations

from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from benchmarks.policy_multihop import (  # noqa: E402
    POLICY_MULTIHOP_CASE_CONFIGS,
    PolicyMultiHopCaseConfig,
    generate_policy_multihop_suite,
)
from benchmarks.policy_multihop.artifacts import main  # noqa: E402


__all__ = [
    "POLICY_MULTIHOP_CASE_CONFIGS",
    "PolicyMultiHopCaseConfig",
    "generate_policy_multihop_suite",
]


if __name__ == "__main__":
    main()
