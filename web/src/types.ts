export type Feedback = "like" | "dislike" | null;

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
