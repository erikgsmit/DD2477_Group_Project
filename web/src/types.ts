export type Feedback = "like" | "dislike" | null;

/** Sent to POST /api/feedback (clear removes the active vote without a new Rocchio event). */
export type FeedbackAction = "like" | "dislike" | "clear";

export interface ArticleTotals {
  like_count: number;
  dislike_count: number;
  current: "like" | "dislike" | null;
}

export type FeedbackTotalsMap = Record<string, ArticleTotals>;

export interface Article {
  id: string;
  title: string;
  source: string;
  summary: string;
  topic: string;
  publishedAt: string;
  url: string;
  base_score?: number;
  feedback_score?: number;
  final_score?: number;
}
