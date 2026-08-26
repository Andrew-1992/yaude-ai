// Chat history and settings persistence via localStorage. Real for a
// normal browser app (unlike Artifacts); if Sanadi AI gets real accounts
// later, this is the seam to swap for backend-persisted storage.

import type { ChatSession, SanadiSettings } from "./types";
import { DEFAULT_SETTINGS } from "./types";

const SESSIONS_KEY = "sanadi-chat-sessions";
const SETTINGS_KEY = "sanadi-settings";

export function loadSessions(): ChatSession[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(SESSIONS_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function saveSessions(sessions: ChatSession[]): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(SESSIONS_KEY, JSON.stringify(sessions));
  } catch {
    // Storage full or unavailable -- fail silently, history just won't persist.
  }
}

export function makeSessionTitle(firstMessage: string): string {
  const trimmed = firstMessage.trim();
  return trimmed.length > 48 ? `${trimmed.slice(0, 48)}...` : trimmed;
}

export function loadSettings(): SanadiSettings {
  if (typeof window === "undefined") return DEFAULT_SETTINGS;
  try {
    const raw = window.localStorage.getItem(SETTINGS_KEY);
    if (!raw) return DEFAULT_SETTINGS;
    const parsed = JSON.parse(raw);
    return { ...DEFAULT_SETTINGS, ...parsed };
  } catch {
    return DEFAULT_SETTINGS;
  }
}

export function saveSettings(settings: SanadiSettings): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
  } catch {
    // fail silently
  }
}
