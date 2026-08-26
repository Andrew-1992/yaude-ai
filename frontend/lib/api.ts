// Streaming chat client + feedback submission.

import type { SanadiSettings } from "./types";

interface StreamChatOptions {
  message: string;
  settings: SanadiSettings;
  signal: AbortSignal;
  onToken: (token: string) => void;
}

export async function streamChat({
  message,
  settings,
  signal,
  onToken,
}: StreamChatOptions): Promise<{ mode: string }> {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      max_new_tokens: settings.maxNewTokens,
      temperature: settings.temperature,
    }),
    signal,
  });

  if (!res.ok || !res.body) {
    const detail = await res.json().catch(() => null);
    throw new Error(detail?.error ?? "Chat request failed");
  }

  const mode = res.headers.get("x-sanadi-mode") ?? "unknown";
  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    onToken(decoder.decode(value, { stream: true }));
  }

  return { mode };
}

export async function sendFeedback(
  message: string,
  response: string,
  rating: "up" | "down"
): Promise<void> {
  try {
    await fetch("/api/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, response, rating }),
    });
  } catch {
    // Feedback is a nice-to-have -- a failed submit shouldn't disrupt the
    // chat experience. The button's UI state still reflects the click.
  }
}
