import type { Article, FeedbackAction, FeedbackTotalsMap } from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export interface SearchResponse {
  articles: Article[];
}

export interface FeedbackResponse {
  articles: Article[];
  totals: FeedbackTotalsMap;
}

function normalizeTotals(raw: unknown): FeedbackTotalsMap {
  if (!raw || typeof raw !== "object") {
    return {};
  }
  const out: FeedbackTotalsMap = {};
  for (const [articleId, value] of Object.entries(raw as Record<string, unknown>)) {
    if (!value || typeof value !== "object") {
      continue;
    }
    const row = value as Record<string, unknown>;
    const currentRaw = row.current;
    const current =
      currentRaw === "like" || currentRaw === "dislike" ? currentRaw : null;
    out[articleId] = {
      like_count: Number(row.like_count ?? 0),
      dislike_count: Number(row.dislike_count ?? 0),
      current,
    };
  }
  return out;
}

/***
 * Fetch article recommendations based on a search query from the backend API.
 * @param query - The search query
 * @returns A promise resolving to the search results
 */
export async function fetchRecommendations(query: string): Promise<SearchResponse> {
  const searchParams = new URLSearchParams();
  const trimmedQuery = query.trim();

  if (trimmedQuery) {
    searchParams.set("query", trimmedQuery);
  }

  const response = await fetch(`${API_BASE_URL}/api/search?${searchParams.toString()}`);

  if (!response.ok) {
    throw new Error(`Search request failed with status ${response.status}`);
  }

  const payload = (await response.json()) as SearchResponse;
  return {
    articles: Array.isArray(payload.articles) ? payload.articles : [],
  };
}

/***
 * Fetch persisted like/dislike counts and current vote per article from Elasticsearch.
 */
export async function fetchFeedbackTotals(): Promise<FeedbackTotalsMap> {
  const response = await fetch(`${API_BASE_URL}/api/feedback/totals`);

  if (!response.ok) {
    throw new Error(`Feedback totals request failed with status ${response.status}`);
  }

  const payload = (await response.json()) as { totals?: unknown };
  return normalizeTotals(payload.totals);
}

/***
 * Submit user feedback and receive the reranked recommendation list plus updated totals.
 */
export async function submitFeedback(
  article: Article,
  action: FeedbackAction,
  query: string,
  size: number
): Promise<FeedbackResponse> {
  const response = await fetch(`${API_BASE_URL}/api/feedback`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      article_id: article.id,
      article,
      feedback: action,
      query,
      size,
    }),
  });

  if (!response.ok) {
    throw new Error(`Feedback request failed with status ${response.status}`);
  }

  const payload = (await response.json()) as { articles?: unknown; totals?: unknown };
  return {
    articles: Array.isArray(payload.articles) ? (payload.articles as Article[]) : [],
    totals: normalizeTotals(payload.totals),
  };
}
