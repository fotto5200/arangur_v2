"""Synthetic simulation helpers for Arangur demo surfaces."""

from .position_universe import (
    DEFAULT_OUTPUT_PATH,
    DEFAULT_SEED as DEFAULT_POSITION_UNIVERSE_SEED,
    DEFAULT_SUMMARY_OUTPUT_PATH,
    build_synthetic_position_universe_summary,
    generate_synthetic_position_universe,
    load_synthetic_position_universe,
    validate_synthetic_position_universe,
    write_synthetic_position_universe,
)
from .market_state import (
    DEFAULT_HISTORY_OUTPUT_PATH,
    DEFAULT_SCENARIO_OUTPUT_PATH,
    DEFAULT_SEED as DEFAULT_MARKET_STATE_SEED,
    DEFAULT_SUMMARY_OUTPUT_PATH as DEFAULT_MARKET_STATE_SUMMARY_OUTPUT_PATH,
    build_synthetic_market_state_summary,
    build_synthetic_scenario_market_state_set,
    generate_synthetic_market_state_history,
    load_synthetic_market_state_history,
    validate_synthetic_market_state_history,
    write_synthetic_market_state_history,
)

DEFAULT_SEED = DEFAULT_POSITION_UNIVERSE_SEED

__all__ = [
    "DEFAULT_OUTPUT_PATH",
    "DEFAULT_SEED",
    "DEFAULT_POSITION_UNIVERSE_SEED",
    "DEFAULT_SUMMARY_OUTPUT_PATH",
    "build_synthetic_position_universe_summary",
    "generate_synthetic_position_universe",
    "load_synthetic_position_universe",
    "validate_synthetic_position_universe",
    "write_synthetic_position_universe",
    "DEFAULT_HISTORY_OUTPUT_PATH",
    "DEFAULT_MARKET_STATE_SEED",
    "DEFAULT_SCENARIO_OUTPUT_PATH",
    "DEFAULT_MARKET_STATE_SUMMARY_OUTPUT_PATH",
    "build_synthetic_market_state_summary",
    "build_synthetic_scenario_market_state_set",
    "generate_synthetic_market_state_history",
    "load_synthetic_market_state_history",
    "validate_synthetic_market_state_history",
    "write_synthetic_market_state_history",
]
