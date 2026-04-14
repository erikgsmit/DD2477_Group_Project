from __future__ import annotations

from collections import Counter
from math import log, sqrt

from search.text_processing import article_to_text, preprocess_text

# Type alias for a vector representation of text (e.g., TF-IDF vector)
Vector = dict[str, float]


def term_frequency(tokens: list[str]) -> Vector:
    """
    Compute term frequency (TF) for a list of tokens.
    TF is calculated as the count of each term divided by the maximum term count in the document
    (normalized)

    Parameters:
        tokens: A list of tokens from a document.
    Returns:
        A dictionary mapping each term to its TF value.
    """

    counts = Counter(tokens)
    if not counts:
        return {}

    max_count = max(counts.values())
    return {term: count / max_count for term, count in counts.items()}


def compute_idf(documents: list[list[str]]) -> Vector:
    """
    Compute inverse document frequency (IDF) for a collection of documents.
    IDF is calculated as log((1 + N) / (1 + df)) + 1.

    Parameters:
        documents: A list of documents, where each document is represented as a list of tokens.
    Returns:
        A dictionary mapping each term to its IDF value.
    """

    if not documents:
        return {}

    # Compute document count N and document frequency df for each term
    document_count = len(documents)
    containing_documents = Counter()

    for document in documents:
        for term in set(document):
            containing_documents[term] += 1

    return {
        term: log((1 + document_count) / (1 + freq)) + 1
        for term, freq in containing_documents.items()
    }


def tf_idf_vector(tokens: list[str], idf_map: Vector) -> Vector:
    """
    Compute the TF-IDF vector for a document given its tokens and an IDF map.
    The TF-IDF value for each term is calculated as TF(term) * IDF(term).

    Parameters:
        tokens: A list of tokens from the document.
        idf_map: A dictionary mapping each term to its IDF value.
    Returns:
        A dictionary mapping each term to its TF-IDF value.
    """

    tf = term_frequency(tokens)
    return {term: tf_value * idf_map.get(term, 0.0) for term, tf_value in tf.items()}


def build_query_vector(query: str, idf_map: Vector) -> Vector:
    """Build a TF-IDF vector for the query using the provided IDF map."""
    return tf_idf_vector(preprocess_text(query), idf_map)


def build_article_vector(article: dict, idf_map: Vector) -> Vector:
    """Build a TF-IDF vector for the article using the provided IDF map."""
    return tf_idf_vector(preprocess_text(article_to_text(article)), idf_map)


def cosine_similarity(query_vector: Vector, article_vector: Vector) -> float:
    """
    Compute cosine similarity between two vectors.
    Cosine similarity is calculated as the dot product of the two vectors
    divided by the product of their magnitudes (euclidean norms).

    Parameters:
        query_vector: The vector representation of the query.
        article_vector: The vector representation of the article.

    Returns:
        A float representing the cosine similarity between the query and article vectors.
    """
    if not query_vector or not article_vector:
        return 0.0

    # Compute the numerator (dot product) and the denominator (product of magnitudes) for cosine similarity
    dot_product = sum(
        query_vector.get(term, 0.0) * article_vector.get(term, 0.0)
        for term in query_vector
    )

    # Compute the magnitude of the query vector and the article vector (euclidean norm)
    query_norm = sqrt(sum(value * value for value in query_vector.values()))
    article_norm = sqrt(sum(value * value for value in article_vector.values()))

    if query_norm == 0.0 or article_norm == 0.0:
        return 0.0

    return dot_product / (query_norm * article_norm)
