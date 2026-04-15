import type { Article, Feedback } from "./types";


const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export interface SearchResponse {
  articles: Article[];
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
 * Submit user feedback (like/dislike) for a specific article (currently just logs the feedback)
 * @param articleId - The ID of the article for which feedback is being submitted
 * @param feedback - The feedback value ("like" or "dislike")
 * @returns A promise that resolves when the feedback has been "submitted"
 * Note: In a real implementation, this would involve an API call to the backend to record the feedback
 */
export async function submitFeedback(articleId: string, feedback: Feedback): Promise<void> {
  console.info("Feedback submitted", { articleId, feedback });
  return Promise.resolve();
}
