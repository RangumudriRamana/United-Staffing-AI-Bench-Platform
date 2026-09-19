export interface BatchMatchRequest {
  requirement_id: string;
}

export interface BatchMatchItem {
  consultant_id: string;
  consultant_name: string;
  score: number;
  recommendation: string;
}

export interface BatchMatchResponse {
  matches: BatchMatchItem[];
}

export interface MatchHistoryItem {
  consultant_id: string;
  consultant_name: string;
  requirement_id: string;
  requirement_name: string;
  match_score: number;
  recommendation: string;
  matched_at: string;
}

export interface MatchHistoryResponse {
  history: MatchHistoryItem[];
}