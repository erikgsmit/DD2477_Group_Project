import { FormEvent, useCallback, useEffect, useState } from "react";
import { fetchFeedbackTotals, fetchRecommendations, submitFeedback } from "./api";
import type { Article, Feedback, FeedbackAction, FeedbackTotalsMap } from "./types";

const initialQuery = "";

function App() {
  const [query, setQuery] = useState(initialQuery);
  const [articles, setArticles] = useState<Article[]>([]);
  const [totalsById, setTotalsById] = useState<FeedbackTotalsMap>({});
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const refreshTotals = useCallback(async () => {
    try {
      const totals = await fetchFeedbackTotals();
      setTotalsById(totals);
    } catch {
      setTotalsById({});
    }
  }, []);

  useEffect(() => {
    void refreshTotals();
  }, [refreshTotals]);

  useEffect(() => {
    void loadArticles(initialQuery);
  }, []);

  /* Function to load articles based on the provided query and update the state accordingly */
  async function loadArticles(nextQuery: string) {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const response = await fetchRecommendations(nextQuery);
      setArticles(response.articles);
    } catch (error) {
      setArticles([]);
      setErrorMessage(
        error instanceof Error ? error.message : "Unable to load articles right now."
      );
    } finally {
      setIsLoading(false);
    }
  }
  /* Triggered when the search form/query is submitted */
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await loadArticles(query);
  }

  /* Apply relevance feedback (like/dislike/clear) and persist vote totals in Elasticsearch */
  async function handleFeedback(article: Article, feedback: Exclude<Feedback, null>) {
    const articleId = article.id;
    const currentFeedback = (totalsById[articleId]?.current ?? null) as Feedback;
    const nextFeedback: Feedback = currentFeedback === feedback ? null : feedback;

    const action: FeedbackAction = nextFeedback === null ? "clear" : nextFeedback;

    try {
      const response = await submitFeedback(article, action, query, articles.length || 10);
      setArticles(response.articles);
      setTotalsById(response.totals);
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Unable to submit feedback right now."
      );
      void refreshTotals();
    }
  }

  const likedCount = Object.values(totalsById).reduce((sum, row) => sum + row.like_count, 0);
  const dislikedCount = Object.values(totalsById).reduce(
    (sum, row) => sum + row.dislike_count,
    0
  );

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
        {errorMessage ? (
          <div className="empty-state">
            <h2>Search unavailable</h2>
            <p>{errorMessage}</p>
          </div>
        ) : null}

        {!errorMessage && articles.length === 0 ? (
          <div className="empty-state">
            <h2>No matching articles</h2>
            <p>Try another keyword or broaden the query.</p>
          </div>
        ) : (
          articles.map((article) => {
            const row = totalsById[article.id];
            const feedback = (row?.current ?? null) as Feedback;
            const likeCount = row?.like_count ?? 0;
            const dislikeCount = row?.dislike_count ?? 0;

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
                      onClick={() => void handleFeedback(article, "like")}
                    >
                      Like ({likeCount})
                    </button>
                    <button
                      type="button"
                      className={feedback === "dislike" ? "active negative" : ""}
                      onClick={() => void handleFeedback(article, "dislike")}
                    >
                      Dislike ({dislikeCount})
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
