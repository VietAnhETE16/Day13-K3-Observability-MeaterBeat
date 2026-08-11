from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class CostOptimizationState:
    enabled: bool = False
    max_output_tokens: int = int(os.getenv("COST_OPTIMIZATION_MAX_OUTPUT_TOKENS", "220"))


STATE = CostOptimizationState()


def enable(max_output_tokens: int | None = None) -> dict:
    if max_output_tokens is not None:
        STATE.max_output_tokens = max(1, max_output_tokens)
    STATE.enabled = True
    return status()


def disable() -> dict:
    STATE.enabled = False
    return status()


def status() -> dict:
    return {
        "enabled": STATE.enabled,
        "max_output_tokens": STATE.max_output_tokens,
    }


def cap_output_tokens(output_tokens: int) -> int:
    if not STATE.enabled:
        return output_tokens
    return min(output_tokens, STATE.max_output_tokens)
