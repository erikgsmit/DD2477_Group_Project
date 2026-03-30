import { FormEvent, useEffect, useState } from "react";
import { fetchRecommendations, submitFeedback } from "./api";
import type { Article, Feedback } from "./types";

const initialQuery = "Lorem";

function App() {
  // Initialize state variables for query, articles, feedback, and loading status
  const [query, setQuery] = useState(initialQuery);
  const [articles, setArticles] = useState<Article[]>([]);
  const [feedbackById, setFeedbackById] = useState<Record<string, Feedback>>({});
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    void loadArticles(initialQuery);
  }, []);

  /* Function to load articles based on the provided query and update the state accordingly */
  async function loadArticles(nextQuery: string) {
    setIsLoading(true);
    try {
      const response = await fetchRecommendations(nextQuery);
      setArticles(response.articles);
    } finally {
      setIsLoading(false);
    }
  }
  /* Triggered when the search form/query is submitted */
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await loadArticles(query);
  }

  /* Apply relevance feedback (like/dislike) to an article and submit it to the backend */
  async function handleFeedback(articleId: string, feedback: Exclude<Feedback, null>) {
    setFeedbackById((current) => ({ ...current, [articleId]: feedback }));
    await submitFeedback(articleId, feedback);
  }

  /* Calculate the total number of likes and dislikes based on the feedback state */
  const likedCount = Object.values(feedbackById).filter((value) => value === "like").length;
  const dislikedCount = Object.values(feedbackById).filter((value) => value === "dislike").length;

  /* Render the main application UI, including the search form, statistics, and article recommendations */
  return (
    <main className="page-shell">
      <section className="hero">
        <h1>News Recommendation</h1>
        <p className="hero-copy">
          Search for a topic and get personalized recommendations
        </p>
      </section>
      <section className="panel">
        <form className="search-form" onSubmit={handleSubmit}>
          <label className="field">
            <span>Search</span>
            <input
              type="text"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Try technology, sports, science..."
            />
          </label>
          <button type="submit" disabled={isLoading}>
            {isLoading ? "Searching..." : "Get recommendations"}
          </button>
        </form>
        <div className="stats">
          <div>
            <strong>{articles.length}</strong>
            <span>articles shown</span>
          </div>
          <div>
            <strong>{likedCount}</strong>
            <span>likes</span>
          </div>
          <div>
            <strong>{dislikedCount}</strong>
            <span>dislikes</span>
          </div>
        </div>
      </section>

      <section className="results">
        {articles.length === 0 ? (
          <div className="empty-state">
            <h2>No matching articles</h2>
            <p>Try another keyword or broaden the query.</p>
          </div>
        ) : (
          articles.map((article) => {
            const feedback = feedbackById[article.id] ?? null;

            return (
              <article className="article-card" key={article.id}>
                <div className="article-meta">
                  <span>{article.source}</span>
                  <span>{article.topic}</span>
                  <span>{article.publishedAt}</span>
                </div>
                <h2>{article.title}</h2>
                <p>{article.summary}</p>
                <div className="article-actions">
                  <a href={article.url} target="_blank" rel="noreferrer">
                    Open article
                  </a>
                  <div className="feedback-actions">
                    <button
                      type="button"
                      className={feedback === "like" ? "active positive" : ""}
                      onClick={() => void handleFeedback(article.id, "like")}
                    >
                      Like
                    </button>
                    <button
                      type="button"
                      className={feedback === "dislike" ? "active negative" : ""}
                      onClick={() => void handleFeedback(article.id, "dislike")}
                    >
                      Dislike
                    </button>
                  </div>
                </div>
              </article>
            );
          })
        )}
      </section>
    </main>
  );
}

export default App;
