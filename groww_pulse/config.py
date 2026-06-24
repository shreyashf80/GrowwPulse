"""
Groww Pulse — Configuration loader.

Loads config.yaml, validates required fields, exposes typed dataclasses
with dot-access, and supports CLI argument overrides.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional

import yaml


# ---------------------------------------------------------------------------
# Typed config dataclasses
# ---------------------------------------------------------------------------


@dataclass
class ProductConfig:
    """Product identification."""

    name: str = "Groww"
    play_store_app_id: str = "com.nextbillion.groww"


@dataclass
class IngestionConfig:
    """Review ingestion parameters."""

    window_weeks: int = 12
    max_reviews: int = 2000


@dataclass
class ClusteringConfig:
    """UMAP + HDBSCAN parameters."""

    umap_n_components: int = 5
    umap_n_neighbors: int = 15
    hdbscan_min_cluster_size: int = 10
    hdbscan_min_samples: int = 5


@dataclass
class LLMConfig:
    """LLM summarization parameters."""

    model: str = "gpt-4o-mini"
    temperature: float = 0.2
    max_tokens: int = 100_000
    quote_validation: bool = True


@dataclass
class DeliveryConfig:
    """Google Docs + Gmail delivery parameters."""

    google_doc_id: str = ""
    email_recipients: List[str] = field(default_factory=list)
    draft_only: bool = False


@dataclass
class ReceiptsConfig:
    """Run receipt storage."""

    storage_path: str = "data/receipts/"


@dataclass
class Config:
    """Top-level configuration container."""

    product: ProductConfig = field(default_factory=ProductConfig)
    ingestion: IngestionConfig = field(default_factory=IngestionConfig)
    clustering: ClusteringConfig = field(default_factory=ClusteringConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    delivery: DeliveryConfig = field(default_factory=DeliveryConfig)
    receipts: ReceiptsConfig = field(default_factory=ReceiptsConfig)


# ---------------------------------------------------------------------------
# Config file discovery
# ---------------------------------------------------------------------------

_DEFAULT_CONFIG_FILENAME = "config.yaml"


def _find_config_path(explicit_path: Optional[str] = None) -> Path:
    """Resolve the config file path.

    Search order:
      1. Explicit path (if provided).
      2. ``CONFIG_PATH`` environment variable.
      3. ``config.yaml`` in the project root (two levels up from this file).
    """
    if explicit_path:
        p = Path(explicit_path)
        if not p.is_file():
            _fail(f"Config file not found at explicit path: {p}")
        return p

    env_path = os.environ.get("CONFIG_PATH")
    if env_path:
        p = Path(env_path)
        if not p.is_file():
            _fail(f"Config file not found at CONFIG_PATH={p}")
        return p

    # Default: project root / config.yaml
    project_root = Path(__file__).resolve().parent.parent
    p = project_root / _DEFAULT_CONFIG_FILENAME
    if not p.is_file():
        _fail(
            f"config.yaml not found at {p}. "
            "Create it from the template or set CONFIG_PATH. "
            "See docs/architecture.md §8 for the expected schema."
        )
    return p


# ---------------------------------------------------------------------------
# Loader & validator
# ---------------------------------------------------------------------------


def load_config(path: Optional[str] = None) -> Config:
    """Load and validate ``config.yaml``, returning a typed :class:`Config`.

    Parameters
    ----------
    path:
        Optional explicit path to config file.  Falls back to env var /
        project root discovery.

    Returns
    -------
    Config
        Fully-populated config dataclass.

    Raises
    ------
    SystemExit
        If the file is missing, unparseable, or has invalid values.
    """
    config_path = _find_config_path(path)
    raw = _load_yaml(config_path)
    config = _parse(raw)
    _validate(config)
    return config


def apply_cli_overrides(
    config: Config,
    *,
    window: Optional[int] = None,
    draft_only: Optional[bool] = None,
) -> Config:
    """Merge CLI argument overrides into an existing config (in-place).

    Only non-``None`` values override the corresponding config field.
    """
    if window is not None:
        config.ingestion.window_weeks = window
    if draft_only is not None:
        config.delivery.draft_only = draft_only
    return config


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _load_yaml(path: Path) -> dict[str, Any]:
    """Read and parse a YAML file."""
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        _fail(f"Failed to parse {path}: {exc}")

    if not isinstance(data, dict):
        _fail(f"Expected a YAML mapping in {path}, got {type(data).__name__}.")
    return data


def _parse(raw: dict[str, Any]) -> Config:
    """Map raw YAML dict → typed Config dataclass tree."""
    return Config(
        product=_section(raw, "product", ProductConfig),
        ingestion=_section(raw, "ingestion", IngestionConfig),
        clustering=_section(raw, "clustering", ClusteringConfig),
        llm=_section(raw, "llm", LLMConfig),
        delivery=_section(raw, "delivery", DeliveryConfig),
        receipts=_section(raw, "receipts", ReceiptsConfig),
    )


def _section(raw: dict[str, Any], key: str, cls: type) -> Any:
    """Extract a section from the raw dict and instantiate the dataclass."""
    section_data = raw.get(key, {})
    if not isinstance(section_data, dict):
        _fail(f"Config section '{key}' must be a mapping, got {type(section_data).__name__}.")
    # Filter to only known fields to avoid TypeErrors on unknown keys
    known_fields = {f.name for f in cls.__dataclass_fields__.values()}
    unknown = set(section_data.keys()) - known_fields
    if unknown:
        import logging

        logging.getLogger("groww_pulse.config").warning(
            "Unknown config fields in '%s': %s (ignored)", key, ", ".join(sorted(unknown))
        )
    filtered = {k: v for k, v in section_data.items() if k in known_fields}
    return cls(**filtered)


def _validate(config: Config) -> None:
    """Validate config values; exit on invalid."""
    errors: List[str] = []

    if config.ingestion.window_weeks < 1:
        errors.append("ingestion.window_weeks must be >= 1")
    if config.ingestion.max_reviews < 1:
        errors.append("ingestion.max_reviews must be >= 1")
    if config.clustering.hdbscan_min_cluster_size < 2:
        errors.append("clustering.hdbscan_min_cluster_size must be >= 2")
    if config.clustering.hdbscan_min_samples < 1:
        errors.append("clustering.hdbscan_min_samples must be >= 1")
    if config.llm.temperature < 0 or config.llm.temperature > 2:
        errors.append("llm.temperature must be between 0 and 2")
    if config.llm.max_tokens < 1:
        errors.append("llm.max_tokens must be >= 1")

    if errors:
        _fail("Config validation failed:\n  • " + "\n  • ".join(errors))


def _fail(message: str) -> None:
    """Print an error and exit."""
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)
