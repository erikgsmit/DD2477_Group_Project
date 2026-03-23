export type Feedback = "like" | "dislike" | null;

export interface Article {
  id: string;
  title: string;
  source: string;
  summary: string;
  topic: string;
  publishedAt: string;
  url: string;
}
