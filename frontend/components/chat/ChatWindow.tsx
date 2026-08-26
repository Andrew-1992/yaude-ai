// Presentational chat pane. Two distinct compositions:
//
// - Empty state: a spacious hero -- a single personalized headline
//   ("Have an idea, <name>?") in a serif display font, and a big
//   centered input -- matching the first-impression convention
//   Claude/ChatGPT/Lovable all share. Unlike those three, Sanadi stays
//   strictly monochrome (no gradient, no colored mark); the
//   differentiation comes from type and restraint.
// - Active conversation: the compact docked-bottom input, message list
//   above it. Same container width as the hero so nothing visually jumps
//   when the first message is sent.
//
// The model-status badge and settings live INSIDE the input card's
// toolbar row (see InputBar) rather than scattered above the page --
// consolidating controls into one surface, the way all three references
// do, instead of splitting them across the layout.

"use client";

import { useRef, useEffect, useState, forwardRef } from "react";
import MessageBubble from "./MessageBubble";
import InputBar, { type InputBarHandle } from "./InputBar";
import type { ChatMessage, SanadiSettings } from "@/lib/types";

interface ChatWindowProps {
  messages: ChatMessage[];
  streamingText: string;
  isStreaming: boolean;
  error: string | null;
  modelMode: string | null;
  settings: SanadiSettings;
  onSettingsChange: (s: SanadiSettings) => void;
  onSend: (message: string) => void;
  onStop: () => void;
  onRegenerate: () => void;
  onFeedback: (index: number, rating: "up" | "down") => void;
  userName: string;
}

const ChatWindow = forwardRef<InputBarHandle, ChatWindowProps>(function ChatWindow(
  {
    messages,
    streamingText,
    isStreaming,
    error,
    modelMode,
    settings,
    onSettingsChange,
    onSend,
    onStop,
    onRegenerate,
    onFeedback,
    userName,
  },
  inputRef
) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const isEmpty = messages.length === 0 && !isStreaming;

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    const nearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 80;
    if (nearBottom) el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  }, [messages, streamingText, isStreaming]);

  function handleScroll() {
    const el = scrollRef.current;
    if (!el) return;
    const nearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 80;
    setShowScrollButton(!nearBottom);
  }

  function scrollToBottom() {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }

  const lastAssistantIndex = [...messages].map((m) => m.role).lastIndexOf("assistant");

  return (
    <div className="flex flex-col h-full max-w-2xl mx-auto w-full min-h-0">
      {isEmpty ? (
        <div className="flex-1 flex flex-col items-center justify-center px-4 pb-16">
          <h1 className="font-display text-[2.125rem] sm:text-[2.5rem] font-semibold tracking-tight text-sanadi-black text-center leading-tight">
            Have an idea, {userName.split(" ")[0]}?
          </h1>

          <div className="w-full mt-8">
            <InputBar
              ref={inputRef}
              variant="hero"
              onSend={onSend}
              onStop={onStop}
              loading={isStreaming}
              modelMode={modelMode}
              settings={settings}
              onSettingsChange={onSettingsChange}
            />
            <p className="mt-3 text-[0.6875rem] text-sanadi-ink-40 text-center">
              Enter to send &middot; Shift+Enter for a new line
            </p>
          </div>
        </div>
      ) : (
        <>
          <div className="relative flex-1 min-h-0">
            <div
              ref={scrollRef}
              onScroll={handleScroll}
              className="h-full overflow-y-auto px-4 pt-4 pb-2"
            >
              {messages.map((m, i) => (
                <MessageBubble
                  key={i}
                  message={m}
                  isLastAssistant={i === lastAssistantIndex && !isStreaming}
                  onRegenerate={onRegenerate}
                  onFeedback={(rating) => onFeedback(i, rating)}
                />
              ))}

              {isStreaming && (
                <MessageBubble
                  message={{ role: "assistant", content: streamingText || "\u2026", timestamp: Date.now() }}
                  isLastAssistant={false}
                  onRegenerate={() => {}}
                  onFeedback={() => {}}
                />
              )}

              {error && (
                <p className="text-sm text-sanadi-ink-70 text-center mt-2 underline underline-offset-2 decoration-sanadi-ink-40">
                  {error}
                </p>
              )}
            </div>

            {showScrollButton && (
              <button
                type="button"
                onClick={scrollToBottom}
                aria-label="Scroll to latest message"
                className="absolute bottom-3 left-1/2 -translate-x-1/2 w-8 h-8 flex items-center justify-center rounded-full bg-sanadi-black text-sanadi-cream shadow-md"
              >
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path
                    d="M3 6L7 10L11 6"
                    stroke="currentColor"
                    strokeWidth="1.6"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </button>
            )}
          </div>

          <InputBar
            ref={inputRef}
            variant="docked"
            onSend={onSend}
            onStop={onStop}
            loading={isStreaming}
            modelMode={modelMode}
            settings={settings}
            onSettingsChange={onSettingsChange}
          />
        </>
      )}
    </div>
  );
});

export default ChatWindow;
