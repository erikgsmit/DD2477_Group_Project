from __future__ import annotations

from search.rocchio import weighted_rocchio_update
from search.text_processing import article_to_text, preprocess_text
from search.vectorization import (
    build_article_vector,
    build_query_vector,
    cosine_similarity,
    compute_idf,
)

EXPANSION_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "was",
    "were",
    "with",
}


def _normalize_base_score(score: float, min_score: float, max_score: float) -> float:
    """
    Normalize the base score to a 0-1 range based on the candidate set.

    Parameters:
        score: The original base score to be normalized.
        min_score: The minimum base score among the candidates.
        max_score: The maximum base score among the candidates.
    Returns:
        A normalized score in the range [0, 1].
    """
    if max_score == min_score:
        return 1.0
    return (score - min_score) / (max_score - min_score)


def _query_similarity(
    left_query: str, right_query: str, idf_map: dict[str, float]
) -> float:
    """
    Compare two queries using cosine similarity over TF-IDF query vectors.
    """
    left_vector = build_query_vector(left_query, idf_map)
    right_vector = build_query_vector(right_query, idf_map)
    return cosine_similarity(left_vector, right_vector)


def expand_query_with_rocchio(
    query: str,
    feedback_articles: list[dict],
    feedback_entries: list[dict],
    alpha: float = 1.0,
    beta: float = 0.75,
    gamma: float = 0.15,
    max_expansion_terms: int = 6,
    query_similarity_threshold: float = 0.2,
) -> tuple[str, list[str]]:
    """
    Convert the Rocchio-updated query vector into extra search terms for the
    retrieval step before reranking.
    """
    if not feedback_articles or not feedback_entries:
        return query, []

    document_tokens = [
        preprocess_text(article_to_text(article)) for article in feedback_articles
    ]
    idf_map = compute_idf([preprocess_text(query), *document_tokens])
    query_vector = build_query_vector(query, idf_map)
    article_vectors = {
        article["id"]: build_article_vector(article, idf_map)
        for article in feedback_articles
    }

    feedback_queries = [
        entry.get("query", "")
        for entry in feedback_entries
        if isinstance(entry.get("query"), str) and entry.get("query", "").strip()
    ]
    query_idf_map = compute_idf(
        [preprocess_text(past_query) for past_query in [query, *feedback_queries]]
    )

    relevant_weighted_vectors: list[tuple[dict[str, float], float]] = []
    non_relevant_weighted_vectors: list[tuple[dict[str, float], float]] = []

    for entry in feedback_entries:
        past_query = entry.get("query", "")
        article_id = entry.get("article_id")
        feedback_value = int(entry.get("feedback", 0))

        if not isinstance(past_query, str) or article_id not in article_vectors:
            continue

        query_similarity = _query_similarity(query, past_query, query_idf_map)
        if query.strip() and query_similarity < query_similarity_threshold:
            continue

        weight = query_similarity if query_similarity > 0 else 1.0
        weighted_vector = (article_vectors[article_id], weight)
        if feedback_value == 1:
            relevant_weighted_vectors.append(weighted_vector)
        elif feedback_value == -1:
            non_relevant_weighted_vectors.append(weighted_vector)

    updated_query_vector = weighted_rocchio_update(
        query_vector=query_vector,
        relevant_weighted_vectors=relevant_weighted_vectors,
        non_relevant_weighted_vectors=non_relevant_weighted_vectors,
        alpha=alpha,
        beta=beta,
        gamma=gamma,
    )

    original_terms = set(preprocess_text(query))
    expansion_terms: list[str] = []
    for term, _score in sorted(
        updated_query_vector.items(), key=lambda item: item[1], reverse=True
    ):
        if term in original_terms or term in EXPANSION_STOPWORDS:
            continue
        if len(term) <= 2 or term.isdigit():
            continue
        expansion_terms.append(term)
        if len(expansion_terms) == max_expansion_terms:
            break

    expanded_query = " ".join([query.strip(), *expansion_terms]).strip()
    return expanded_query, expansion_terms


def rerank_with_rocchio(
    query: str,
    candidates: list[dict],
    feedback_entries: list[dict],
    feedback_articles: list[dict] | None = None,
    alpha: float = 0.5,
    beta: float = 0.5,
    gamma: float = 0.15,
    feedback_weight: float = 0.6,
    query_similarity_threshold: float = 0.2,
) -> list[dict]:
    """
    Rerank candidate articles by combining the original retrieval score with
    a Rocchio-updated similarity score derived from user feedback.

    Parameters:
        query: The original search query.
        candidates: A list of candidate articles, each with an optional 'base_score'.
        feedback_entries: A list of feedback records with article_id, query, and
            feedback values.
        alpha: Weight for the original query vector in Rocchio update.
        beta: Weight for the relevant (liked) article vectors in Rocchio update.
        gamma: Weight for the non-relevant (disliked) article vectors in Rocchio update.
        feedback_weight: The weight given to the feedback score when combining with the base score.
        query_similarity_threshold: Minimum query similarity required before
            historical feedback is reused.
    Returns:
        A list of articles with added 'feedback_score' and 'final_score', sorted by 'final_score' in descending order.
    """
    if not candidates:
        return []

    vector_articles_by_id = {
        article["id"]: article
        for article in [*candidates, *(feedback_articles or [])]
        if article.get("id")
    }

    # Get all tokens for IDF calculation
    document_tokens = [
        preprocess_text(article_to_text(article))
        for article in vector_articles_by_id.values()
    ]

    # Calculate IDF values for all terms across all candidate articles and the query
    idf_map = compute_idf([preprocess_text(query), *document_tokens])

    # Build the query vector and article vectors using TF-IDF.
    query_vector = build_query_vector(query, idf_map)
    article_vectors = {
        article["id"]: build_article_vector(article, idf_map)
        for article in vector_articles_by_id.values()
    }

    # Build a small query corpus so we can compare the current query to the
    # queries that produced past feedback.
    feedback_queries = [
        entry.get("query", "")
        for entry in feedback_entries
        if isinstance(entry.get("query"), str) and entry.get("query", "").strip()
    ]
    query_idf_map = compute_idf(
        [preprocess_text(past_query) for past_query in [query, *feedback_queries]]
    )

    relevant_weighted_vectors: list[tuple[dict[str, float], float]] = []
    non_relevant_weighted_vectors: list[tuple[dict[str, float], float]] = []

    for entry in feedback_entries:
        past_query = entry.get("query", "")
        article_id = entry.get("article_id")
        feedback_value = int(entry.get("feedback", 0))

        if not isinstance(past_query, str) or article_id not in article_vectors:
            continue

        query_similarity = _query_similarity(query, past_query, query_idf_map)
        if query_similarity < query_similarity_threshold:
            continue

        weighted_vector = (article_vectors[article_id], query_similarity)
        if feedback_value == 1:
            relevant_weighted_vectors.append(weighted_vector)
        elif feedback_value == -1:
            non_relevant_weighted_vectors.append(weighted_vector)

    # Apply the Rocchio update to the query vector using similarity-weighted feedback
    updated_query_vector = weighted_rocchio_update(
        query_vector=query_vector,
        relevant_weighted_vectors=relevant_weighted_vectors,
        non_relevant_weighted_vectors=non_relevant_weighted_vectors,
        alpha=alpha,
        beta=beta,
        gamma=gamma,
    )

    # Normalize base scores for all candidates to make sure they are on a comparable scale with feedback scores
    base_scores = [float(article.get("base_score", 0.0)) for article in candidates]
    min_base_score = min(base_scores)
    max_base_score = max(base_scores)

    reranked_articles: list[dict] = []
    for article in candidates:
        article_id = article["id"]
        base_score = float(article.get("base_score", 0.0))

        # Compute the feedback score using cosine similarity using the updated query vector and the article vector
        feedback_score = cosine_similarity(
            updated_query_vector, article_vectors[article_id]
        )
        normalized_base_score = _normalize_base_score(
            base_score, min_base_score, max_base_score
        )

        # Combine the normalized base score and the feedback score using the specified feedback weight
        final_score = ((1 - feedback_weight) * normalized_base_score) + (
            feedback_weight * feedback_score
        )

        # Create a new article dictionary that includes the feedback score and the final combined score
        reranked_article = {
            **article,
            "feedback_score": round(feedback_score, 6),
            "final_score": round(final_score, 6),
        }
        reranked_articles.append(reranked_article)

    reranked_articles.sort(key=lambda article: article["final_score"], reverse=True)
    return reranked_articles
