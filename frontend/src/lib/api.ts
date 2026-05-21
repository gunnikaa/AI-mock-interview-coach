import axios from "axios";

export const API_BASE = "";

export const api = axios.create({ baseURL: API_BASE });

export interface StartResponse {
  session_id: string;
  question: string;
  turn: number;
}
export interface AnswerResponse {
  question: string;
  turn: number;
  done: boolean;
}
export interface RewrittenAnswer {
  original: string;
  improved: string;
  what_changed: string[];
}
export interface FeedbackResponse {
  feedback_markdown: string;
  rewritten_answers: RewrittenAnswer[];
  total_turns: number;
  average_score: number;
}

export function getApiError(err: unknown): string {
  if (axios.isAxiosError(err)) {
    if (!err.response) {
      return "Could not connect to interview server. Make sure the backend is running at localhost:8000.";
    }
    const data = err.response.data as { detail?: string; message?: string } | undefined;
    return data?.detail || data?.message || err.message;
  }
  return err instanceof Error ? err.message : "Unknown error";
}
