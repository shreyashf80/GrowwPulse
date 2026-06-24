"""Tests for the config loader (Phase 0)."""

from __future__ import annotations

import os
import textwrap
from pathlib import Path

import pytest

from groww_pulse.config import Config, apply_cli_overrides, load_config


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def config_file(tmp_path: Path) -> Path:
    """Create a minimal valid config.yaml in a temp directory."""
    content = textwrap.dedent("""\
        product:
          name: "Groww"
          play_store_app_id: "com.nextbillion.groww"

        ingestion:
          window_weeks: 12
          max_reviews: 2000

        clustering:
          umap_n_components: 5
          umap_n_neighbors: 15
          hdbscan_min_cluster_size: 10
          hdbscan_min_samples: 5

        llm:
          model: "gpt-4o-mini"
          temperature: 0.2
          max_tokens: 100000
          quote_validation: true

        delivery:
          google_doc_id: "test-doc-id"
          email_recipients:
            - "test@example.com"
          draft_only: false

        receipts:
          storage_path: "data/receipts/"
    """)
    p = tmp_path / "config.yaml"
    p.write_text(content)
    return p


@pytest.fixture()
def config(config_file: Path) -> Config:
    """Load a Config from the test fixture."""
    return load_config(str(config_file))


# ---------------------------------------------------------------------------
# Test: Loading
# ---------------------------------------------------------------------------


class TestConfigLoading:
    """Config file loading and parsing."""

    def test_load_returns_config(self, config: Config) -> None:
        assert isinstance(config, Config)

    def test_product_fields(self, config: Config) -> None:
        assert config.product.name == "Groww"
        assert config.product.play_store_app_id == "com.nextbillion.groww"

    def test_ingestion_fields(self, config: Config) -> None:
        assert config.ingestion.window_weeks == 12
        assert config.ingestion.max_reviews == 2000

    def test_clustering_fields(self, config: Config) -> None:
        assert config.clustering.umap_n_components == 5
        assert config.clustering.umap_n_neighbors == 15
        assert config.clustering.hdbscan_min_cluster_size == 10
        assert config.clustering.hdbscan_min_samples == 5

    def test_llm_fields(self, config: Config) -> None:
        assert config.llm.model == "gpt-4o-mini"
        assert config.llm.temperature == 0.2
        assert config.llm.max_tokens == 100_000
        assert config.llm.quote_validation is True

    def test_delivery_fields(self, config: Config) -> None:
        assert config.delivery.google_doc_id == "test-doc-id"
        assert config.delivery.email_recipients == ["test@example.com"]
        assert config.delivery.draft_only is False

    def test_receipts_fields(self, config: Config) -> None:
        assert config.receipts.storage_path == "data/receipts/"


# ---------------------------------------------------------------------------
# Test: Defaults
# ---------------------------------------------------------------------------


class TestConfigDefaults:
    """Missing sections fall back to defaults."""

    def test_empty_config_uses_defaults(self, tmp_path: Path) -> None:
        p = tmp_path / "config.yaml"
        p.write_text("{}")  # Empty mapping
        cfg = load_config(str(p))
        assert cfg.product.name == "Groww"
        assert cfg.ingestion.window_weeks == 12
        assert cfg.llm.model == "gpt-4o-mini"

    def test_partial_section(self, tmp_path: Path) -> None:
        p = tmp_path / "config.yaml"
        p.write_text("ingestion:\n  window_weeks: 8\n")
        cfg = load_config(str(p))
        assert cfg.ingestion.window_weeks == 8
        assert cfg.ingestion.max_reviews == 2000  # default


# ---------------------------------------------------------------------------
# Test: CLI Overrides
# ---------------------------------------------------------------------------


class TestCLIOverrides:
    """CLI arguments override config values."""

    def test_override_window(self, config: Config) -> None:
        apply_cli_overrides(config, window=8)
        assert config.ingestion.window_weeks == 8

    def test_override_draft_only(self, config: Config) -> None:
        apply_cli_overrides(config, draft_only=True)
        assert config.delivery.draft_only is True

    def test_none_override_is_noop(self, config: Config) -> None:
        apply_cli_overrides(config, window=None, draft_only=None)
        assert config.ingestion.window_weeks == 12
        assert config.delivery.draft_only is False


# ---------------------------------------------------------------------------
# Test: Validation
# ---------------------------------------------------------------------------


class TestConfigValidation:
    """Invalid config values trigger SystemExit."""

    def test_invalid_window_weeks(self, tmp_path: Path) -> None:
        p = tmp_path / "config.yaml"
        p.write_text("ingestion:\n  window_weeks: 0\n")
        with pytest.raises(SystemExit):
            load_config(str(p))

    def test_invalid_max_reviews(self, tmp_path: Path) -> None:
        p = tmp_path / "config.yaml"
        p.write_text("ingestion:\n  max_reviews: -1\n")
        with pytest.raises(SystemExit):
            load_config(str(p))

    def test_invalid_min_cluster_size(self, tmp_path: Path) -> None:
        p = tmp_path / "config.yaml"
        p.write_text("clustering:\n  hdbscan_min_cluster_size: 1\n")
        with pytest.raises(SystemExit):
            load_config(str(p))

    def test_invalid_temperature(self, tmp_path: Path) -> None:
        p = tmp_path / "config.yaml"
        p.write_text("llm:\n  temperature: 5.0\n")
        with pytest.raises(SystemExit):
            load_config(str(p))


# ---------------------------------------------------------------------------
# Test: Missing file
# ---------------------------------------------------------------------------


class TestConfigMissing:
    """Missing config file triggers SystemExit."""

    def test_missing_explicit_path(self) -> None:
        with pytest.raises(SystemExit):
            load_config("/nonexistent/config.yaml")

    def test_env_var_path(self, config_file: Path) -> None:
        os.environ["CONFIG_PATH"] = str(config_file)
        try:
            cfg = load_config()
            assert cfg.product.name == "Groww"
        finally:
            del os.environ["CONFIG_PATH"]


# ---------------------------------------------------------------------------
# Test: Unknown fields
# ---------------------------------------------------------------------------


class TestUnknownFields:
    """Unknown config fields are warned but not rejected."""

    def test_unknown_field_ignored(self, tmp_path: Path) -> None:
        p = tmp_path / "config.yaml"
        p.write_text("delivery:\n  slack_webhook: 'https://hooks.slack.com/test'\n")
        # Should not crash — unknown field is silently ignored
        cfg = load_config(str(p))
        assert not hasattr(cfg.delivery, "slack_webhook")
