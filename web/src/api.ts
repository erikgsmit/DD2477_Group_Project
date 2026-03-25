/* 
API module to handle fetching article recommendations and submitting feedback 
This is where we would implement actual API calls to a backend service. For example:

/GET/recommendations?query=food to fetch articles related to "food"

*/

import { mockArticles } from "./mockData";
import type { Article, Feedback } from "./types";

export interface SearchResponse {
  articles: Article[];
}

/*** 
 * Fetch article recommendations based on a search query (currently using mock data)
 * @param query - The search query
 * @returns A promise resolving to the search results
 */ 
export async function fetchRecommendations(query: string): Promise<SearchResponse> {
  const normalizedQuery = query.trim().toLowerCase();

  const filteredArticles = normalizedQuery
    ? mockArticles.filter((article) => {
        const haystack = `${article.title} ${article.summary} ${article.topic}`.toLowerCase();
        return haystack.includes(normalizedQuery);
      })
    : mockArticles;

  return Promise.resolve({ articles: filteredArticles });
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
