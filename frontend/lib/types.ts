export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  feedback?: "up" | "down" | null;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: number;
}

export interface SanadiSettings {
  maxNewTokens: number;
  temperature: number;
}

export const DEFAULT_SETTINGS: SanadiSettings = {
  maxNewTokens: 512,
  temperature: 0.3,
};

export interface SanadiUser {
  id: string;
  name: string;
  email: string;
}
