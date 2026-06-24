"""Tests for the clustering module."""

import numpy as np
import pytest

from groww_pulse.clustering import (
    Cluster,
    NormalizedReview,
    build_clusters,
    cluster_embeddings,
    load_normalized_reviews,
    rank_clusters,
    reduce_dimensions,
)
from groww_pulse.config import Config


@pytest.fixture
def mock_config():
    config = Config()
    config.clustering.umap_n_components = 2
    config.clustering.umap_n_neighbors = 2
    config.clustering.hdbscan_min_cluster_size = 2
    config.clustering.hdbscan_min_samples = 1
    return config


def make_review(idx: int, rating: int = 3, text: str = "sample review text") -> NormalizedReview:
    return NormalizedReview(
        doc_id=f"doc_{idx}",
        rating=rating,
        text=text,
        thumbs_up=0,
        app_version="18.0.0",
    )


def test_reduce_and_cluster(mock_config):
    embeddings = np.array([
        [1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0],
        [10.0, 10.0, 10.0],
        [10.0, 10.0, 10.0],
    ])

    reduced = reduce_dimensions(embeddings, mock_config)
    assert reduced.shape == (5, 2)

    labels = cluster_embeddings(reduced, mock_config)
    # Just verify the label array is the same length as input
    assert len(labels) == 5


def test_build_clusters():
    reviews = [
        make_review(0, rating=1, text="The app crashes on startup every single time."),
        make_review(1, rating=2, text="Cannot withdraw my money, very frustrating."),
        make_review(2, rating=5, text="I love this app very much."),
    ]
    # Reviews 0 & 1 in cluster 0; review 2 is noise (-1)
    labels = np.array([0, 0, -1])
    embeddings = np.array([
        [0.0, 0.0],
        [0.0, 1.0],
        [10.0, 10.0],
    ])

    clusters = build_clusters(reviews, labels, embeddings)
    assert len(clusters) == 1
    c = clusters[0]
    assert c.cluster_id == 0
    assert c.size == 2
    assert c.avg_rating == 1.5
    assert len(c.representative_reviews) == 2
    # Confirm doc_ids are correct
    assert all(r.doc_id in {"doc_0", "doc_1"} for r in c.representative_reviews)


def test_rank_clusters():
    c1 = Cluster(1, size=10, avg_rating=1.0, representative_reviews=[])
    c2 = Cluster(2, size=50, avg_rating=3.0, representative_reviews=[])
    c3 = Cluster(3, size=50, avg_rating=1.0, representative_reviews=[])  # most critical
    c4 = Cluster(4, size=10, avg_rating=5.0, representative_reviews=[])

    global_mean = 3.0
    ranked = rank_clusters([c1, c2, c3, c4], global_mean, top_n=2)

    # c3: size=50, delta=-2.0 → first
    # c2: size=50, delta=0.0  → second
    assert ranked[0].cluster_id == 3
    assert ranked[1].cluster_id == 2


def test_load_normalized_reviews_assigns_doc_ids(tmp_path):
    """load_normalized_reviews() should give every review a unique sequential doc_id."""
    data = [
        {"rating": 5, "text": "Great app and easy to use.", "thumbs_up": 1, "app_version": "18.0"},
        {"rating": 1, "text": "Cannot withdraw money from this app.", "thumbs_up": 0, "app_version": None},
    ]
    f = tmp_path / "normalized_reviews.json"
    f.write_text(__import__("json").dumps(data))

    reviews = load_normalized_reviews(str(f))
    assert len(reviews) == 2
    assert reviews[0].doc_id == "doc_0"
    assert reviews[1].doc_id == "doc_1"
    assert reviews[0].rating == 5
    assert reviews[1].app_version is None
