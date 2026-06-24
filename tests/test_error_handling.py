"""Tests for error handling logic."""

from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from groww_pulse.__main__ import cli

@patch("groww_pulse.ingestion.ingest_reviews")
def test_zero_reviews_aborts(mock_ingest):
    # Mock ingest returning empty list
    mock_ingest.return_value = []
    
    runner = CliRunner()
    result = runner.invoke(cli, ["run", "--week", "2026-W24"])
    
    assert result.exit_code == 0
    assert "No reviews found within the window. Aborting pipeline." in result.output

@patch("groww_pulse.ingestion.ingest_reviews")
@patch("groww_pulse.clustering.run_clustering_pipeline")
def test_zero_clusters_aborts(mock_clustering, mock_ingest):
    # Mock ingest returning reviews, but clustering returns empty
    mock_ingest.return_value = [MagicMock()]
    mock_clustering.return_value = []
    
    runner = CliRunner()
    result = runner.invoke(cli, ["run", "--week", "2026-W24"])
    
    assert result.exit_code == 0
    assert "No clusters generated." in result.output
