from __future__ import annotations

from search.vectorization import Vector


def compute_weighted_centroid(
    weighted_doc_vectors: list[tuple[Vector, float]],
) -> Vector:
    """
    Compute a weighted centroid where each vector contributes proportionally to
    its associated weight.

    Parameters:
        weighted_doc_vectors: A list of tuples, where each tuple contains a vector and its associated weight (e.g., similarity score).
    Returns:
        A single vector representing the weighted centroid of the input vectors.
    """
    if not weighted_doc_vectors:
        return {}

    weighted_sum: Vector = {}
    total_weight = 0.0

    for vector, weight in weighted_doc_vectors:
        if weight <= 0:
            continue
        total_weight += weight
        for term, value in vector.items():
            weighted_sum[term] = weighted_sum.get(term, 0.0) + (value * weight)

    if total_weight == 0.0:
        return {}

    return {term: value / total_weight for term, value in weighted_sum.items()}


def weighted_rocchio_update(
    query_vector: Vector,
    relevant_weighted_vectors: list[tuple[Vector, float]],
    non_relevant_weighted_vectors: list[tuple[Vector, float]],
    alpha: float = 1.0,
    beta: float = 0.75,
    gamma: float = 0.15,
) -> Vector:
    """
    Apply Rocchio using weighted centroids so feedback from more similar past
    queries influences the updated query vector more strongly.

    Q' = alpha * Q + beta * centroid(relevant) - gamma * centroid(non_relevant)
    """
    updated_query: Vector = {}
    relevant_centroid = compute_weighted_centroid(relevant_weighted_vectors)
    non_relevant_centroid = compute_weighted_centroid(non_relevant_weighted_vectors)
    terms = set(query_vector) | set(relevant_centroid) | set(non_relevant_centroid)

    for term in terms:
        score = alpha * query_vector.get(term, 0.0)
        score += beta * relevant_centroid.get(term, 0.0)
        score -= gamma * non_relevant_centroid.get(term, 0.0)

        if score > 0:
            updated_query[term] = score

    return updated_query
