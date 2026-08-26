// Single chat message. Assistant messages render markdown through
// react-markdown, with code blocks rendered via CodeBlock (copy button,
// no syntax-highlighting colors -- consistent with the black/cream/white
// brand discipline). Hover reveals message actions: copy, regenerate
// (last assistant message only), and feedback.
//
// Feedback uses plain text labels rather than thumbs-up/down emoji --
// emoji render in full color on most systems, which would break the
// deliberate no-accent-color brand system.

import { useState, type ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Monogram from "@/components/ui/Monogram";
import CodeBlock from "./CodeBlock";
import type { ChatMessage } from "@/lib/types";

interface MessageBubbleProps {
  message: ChatMessage;
  isLastAssistant: boolean;
  onRegenerate: () => void;
  onFeedback: (rating: "up" | "down") => void;
}

function extractCodeText(children: ReactNode): string {
  const codeEl = Array.isArray(children) ? children[0] : children;
  const inner = (codeEl as { props?: { children?: ReactNode } })?.props?.children;
  if (Array.isArray(inner)) return inner.join("");
  return String(inner ?? "");
}

function formatTime(ts: number): string {
  return new Date(ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export default function MessageBubble({
  message,
  isLastAssistant,
  onRegenerate,
  onFeedback,
}: MessageBubbleProps) {
  const { role, content, timestamp, feedback } = message;
  const isUser = role === "user";
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // Clipboard unavailable -- fail silently.
    }
  }

  return (
    <div className={`group flex gap-2.5 mb-1 sanadi-message-in ${isUser ? "justify-end" : ""}`}>
      {!isUser && (
        <div className="mt-0.5">
          <Monogram size={26} />
        </div>
      )}

      <div className={`flex flex-col ${isUser ? "items-end" : "items-start"} max-w-[75%]`}>
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? "bg-sanadi-black text-sanadi-cream rounded-br-md"
              : "bg-sanadi-cream text-sanadi-black rounded-bl-md"
          }`}
        >
          {isUser ? (
            <p className="text-[0.9375rem] leading-relaxed whitespace-pre-wrap">{content}</p>
          ) : (
            <div className="sanadi-prose">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  pre: ({ children }) => <CodeBlock>{extractCodeText(children)}</CodeBlock>,
                }}
              >
                {content}
              </ReactMarkdown>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2 mt-1 px-1 h-5">
          <span className="text-[0.6875rem] text-sanadi-ink-40">{formatTime(timestamp)}</span>

          <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              type="button"
              onClick={handleCopy}
              aria-label="Copy message"
              className="text-[0.6875rem] text-sanadi-ink-40 hover:text-sanadi-black px-1"
            >
              {copied ? "Copied" : "Copy"}
            </button>

            {!isUser && isLastAssistant && (
              <button
                type="button"
                onClick={onRegenerate}
                aria-label="Regenerate response"
                className="text-[0.6875rem] text-sanadi-ink-40 hover:text-sanadi-black px-1"
              >
                Regenerate
              </button>
            )}

            {!isUser && (
              <>
                <button
                  type="button"
                  onClick={() => onFeedback("up")}
                  aria-label="Good response"
                  className={`text-[0.6875rem] px-1 ${
                    feedback === "up"
                      ? "text-sanadi-black font-medium underline underline-offset-2"
                      : "text-sanadi-ink-40 hover:text-sanadi-black"
                  }`}
                >
                  Good
                </button>
                <button
                  type="button"
                  onClick={() => onFeedback("down")}
                  aria-label="Poor response"
                  className={`text-[0.6875rem] px-1 ${
                    feedback === "down"
                      ? "text-sanadi-black font-medium underline underline-offset-2"
                      : "text-sanadi-ink-40 hover:text-sanadi-black"
                  }`}
                >
                  Poor
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {isUser && (
        <div className="mt-0.5 flex items-center justify-center w-[26px] h-[26px] rounded-full border border-sanadi-ink-15 text-xs font-medium text-sanadi-ink-70 shrink-0">
          You
        </div>
      )}
    </div>
  );
}
