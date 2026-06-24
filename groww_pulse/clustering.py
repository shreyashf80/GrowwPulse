"""Groww Pulse — Clustering module using UMAP and HDBSCAN."""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
import umap
import hdbscan
from sentence_transformers import SentenceTransformer

from groww_pulse.config import Config


@dataclass
class NormalizedReview:
    """A single review loaded from normalized_reviews.json.
    
    The `doc_id` is an anonymous sequential ID (e.g. 'doc_0', 'doc_42') assigned
    at load-time purely for internal cross-referencing during summarization.
    It is NOT persisted and is NOT the original review_id (which was stripped during PII removal).
    """
    doc_id: str           # anonymous e.g. "doc_0", "doc_1"
    rating: int
    text: str
    thumbs_up: int
    app_version: Optional[str]


@dataclass
class Cluster:
    cluster_id: int
    size: int
    avg_rating: float
    representative_reviews: List[NormalizedReview]
    embedding_centroid: List[float] = field(default_factory=list)


def load_normalized_reviews(path: str = "data/normalized_reviews.json") -> List[NormalizedReview]:
    """Load normalized reviews from disk and assign sequential anonymous doc IDs."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Normalized reviews file not found: {path}")

    with open(file_path, encoding="utf-8") as f:
        raw = json.load(f)

    reviews = []
    for idx, item in enumerate(raw):
        reviews.append(NormalizedReview(
            doc_id=f"doc_{idx}",
            rating=item["rating"],
            text=item["text"],
            thumbs_up=item.get("thumbs_up", 0),
            app_version=item.get("app_version"),
        ))

    logging.info(f"Loaded {len(reviews)} normalized reviews from {path}.")
    return reviews


def generate_embeddings(texts: List[str], model_name: str = "BAAI/bge-small-en-v1.5") -> np.ndarray:
    """Generate dense embeddings for a list of texts using a local sentence-transformers model."""
    logging.info(f"Generating embeddings for {len(texts)} reviews using {model_name}...")
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, show_progress_bar=False)
    return np.array(embeddings)


def reduce_dimensions(embeddings: np.ndarray, config: Config) -> np.ndarray:
    """Reduce embedding dimensionality using UMAP."""
    logging.info(f"Reducing dimensions via UMAP (n_components={config.clustering.umap_n_components})...")
    reducer = umap.UMAP(
        n_neighbors=config.clustering.umap_n_neighbors,
        n_components=config.clustering.umap_n_components,
        min_dist=0.0,
        metric='cosine',
        random_state=42  # for reproducibility
    )
    return reducer.fit_transform(embeddings)


def cluster_embeddings(reduced_embeddings: np.ndarray, config: Config) -> np.ndarray:
    """Cluster the reduced embeddings using HDBSCAN."""
    logging.info(f"Clustering with HDBSCAN (min_cluster_size={config.clustering.hdbscan_min_cluster_size})...")
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=config.clustering.hdbscan_min_cluster_size,
        min_samples=config.clustering.hdbscan_min_samples,
        metric='euclidean',
        cluster_selection_method='eom'
    )
    clusterer.fit(reduced_embeddings)
    return clusterer.labels_


def build_clusters(
    reviews: List[NormalizedReview],
    labels: np.ndarray,
    embeddings: np.ndarray,
) -> List[Cluster]:
    """Group reviews by cluster label and compute centroids/representatives."""
    unique_labels = set(labels)
    clusters = []

    for cluster_id in unique_labels:
        if cluster_id == -1:
            continue  # Skip noise points

        indices = np.where(labels == cluster_id)[0]
        cluster_reviews = [reviews[i] for i in indices]
        cluster_emb = embeddings[indices]

        # Calculate centroid
        centroid = np.mean(cluster_emb, axis=0)

        # Distance to centroid → pick top-5 most central reviews as representatives
        distances = np.linalg.norm(cluster_emb - centroid, axis=1)
        sorted_indices = np.argsort(distances)
        top_indices = sorted_indices[:5]
        representative_reviews = [cluster_reviews[i] for i in top_indices]

        avg_rating = sum(r.rating for r in cluster_reviews) / len(cluster_reviews)

        clusters.append(Cluster(
            cluster_id=int(cluster_id),
            size=len(cluster_reviews),
            avg_rating=round(avg_rating, 2),
            representative_reviews=representative_reviews,
            embedding_centroid=centroid.tolist(),
        ))

    logging.info(f"Built {len(clusters)} valid clusters (excluding noise).")
    return clusters


def rank_clusters(clusters: List[Cluster], global_mean_rating: float, top_n: int = 5) -> List[Cluster]:
    """Rank clusters primarily by size, secondarily by negative rating delta."""
    def sort_key(c: Cluster):
        # Largest clusters first; within same size, most negative rating delta first
        rating_delta = c.avg_rating - global_mean_rating
        return (-c.size, rating_delta)

    ranked = sorted(clusters, key=sort_key)
    return ranked[:top_n]


def run_clustering_pipeline(
    reviews: List[NormalizedReview],
    config: Config,
) -> List[Cluster]:
    """End-to-end clustering pipeline accepting NormalizedReview objects."""
    if not reviews:
        logging.warning("No reviews to cluster.")
        return []

    texts = [r.text for r in reviews]
    global_mean_rating = sum(r.rating for r in reviews) / len(reviews)

    embeddings = generate_embeddings(texts)
    reduced = reduce_dimensions(embeddings, config)
    labels = cluster_embeddings(reduced, config)

    clusters = build_clusters(reviews, labels, embeddings)
    ranked = rank_clusters(clusters, global_mean_rating, top_n=5)

    return ranked
