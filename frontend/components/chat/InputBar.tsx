// Auto-resizing textarea inside a single unified card -- the textarea sits
// on top, with a toolbar row below it holding the model-status badge,
// settings, and send/stop button. This consolidates what used to be
// scattered (a status pill and settings gear floating above the page)
// into one control surface, matching the pattern Claude/ChatGPT/Lovable
// all share: everything lives inside the input card, not around it.
//
// Two visual variants sharing one implementation (so behavior can't drift
// between them): "hero" is the large centered input on the empty state;
// "docked" is the compact bottom bar once a conversation is underway.
// Enter sends, Shift+Enter inserts a newline in both.

"use client";

import { useState, useRef, KeyboardEvent, useEffect, forwardRef, useImperativeHandle } from "react";
import SettingsPanel from "./SettingsPanel";
import type { SanadiSettings } from "@/lib/types";

interface InputBarProps {
  onSend: (message: string) => void;
  onStop: () => void;
  loading: boolean;
  variant?: "hero" | "docked";
  modelMode: string | null;
  settings: SanadiSettings;
  onSettingsChange: (s: SanadiSettings) => void;
}

export interface InputBarHandle {
  focus: () => void;
}

const InputBar = forwardRef<InputBarHandle, InputBarProps>(function InputBar(
  { onSend, onStop, loading, variant = "docked", modelMode, settings, onSettingsChange },
  ref
) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const isHero = variant === "hero";

  useImperativeHandle(ref, () => ({
    focus: () => textareaRef.current?.focus(),
  }));

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, isHero ? 220 : 160)}px`;
  }, [value, isHero]);

  function submit() {
    const trimmed = value.trim();
    if (!trimmed || loading) return;
    onSend(trimmed);
    setValue("");
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  const cardClass = isHero
    ? "rounded-3xl border border-sanadi-ink-15 bg-sanadi-white px-5 pt-4 pb-3 shadow-[0_1px_3px_rgba(17,17,17,0.06),0_8px_24px_rgba(17,17,17,0.05)] focus-within:border-sanadi-black/40 transition-colors"
    : "rounded-2xl border border-sanadi-ink-15 bg-sanadi-white px-3.5 pt-2.5 pb-2 focus-within:border-sanadi-black/40 transition-colors";

  const textareaClass = isHero
    ? "w-full resize-none bg-transparent text-[1.0625rem] leading-relaxed text-sanadi-black placeholder:text-sanadi-ink-40 focus:outline-none disabled:opacity-50"
    : "w-full resize-none bg-transparent text-[0.9375rem] leading-relaxed text-sanadi-black placeholder:text-sanadi-ink-40 focus:outline-none disabled:opacity-50";

  const sendButtonSize = isHero ? "w-9 h-9" : "w-8 h-8";

  return (
    <div className={isHero ? "" : "border-t border-sanadi-ink-08 p-3"}>
      <div className={cardClass}>
        <textarea
          ref={textareaRef}
          rows={1}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a coding or research question..."
          disabled={loading}
          autoFocus={isHero}
          className={textareaClass}
        />

        <div className="flex items-center justify-between mt-2.5 pt-2 border-t border-sanadi-ink-08">
          <div>
            {modelMode === "base-model-only" && (
              <span className="text-[0.625rem] font-medium uppercase tracking-wide text-sanadi-ink-40 border border-sanadi-ink-15 rounded-full px-2.5 py-1">
                Base model
              </span>
            )}
          </div>

          <div className="flex items-center gap-1">
            <SettingsPanel settings={settings} onChange={onSettingsChange} />

            {loading ? (
              <button
                type="button"
                onClick={onStop}
                aria-label="Stop generating"
                className={`flex items-center justify-center ${sendButtonSize} rounded-full bg-sanadi-black text-sanadi-cream shrink-0`}
              >
                <span className="w-2.5 h-2.5 rounded-[2px] bg-current" />
              </button>
            ) : (
              <button
                type="button"
                onClick={submit}
                disabled={!value.trim()}
                aria-label="Send message"
                className={`flex items-center justify-center ${sendButtonSize} rounded-full bg-sanadi-black text-sanadi-cream disabled:opacity-30 disabled:cursor-not-allowed shrink-0 transition-opacity`}
              >
                <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
                  <path
                    d="M8 13V3M8 3L3.5 7.5M8 3L12.5 7.5"
                    stroke="currentColor"
                    strokeWidth="1.6"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </button>
            )}
          </div>
        </div>
      </div>

      {!isHero && (
        <p className="mt-1.5 text-[0.6875rem] text-sanadi-ink-40 text-center">
          Enter to send &middot; Shift+Enter for a new line &middot; Ctrl+K new chat
        </p>
      )}
    </div>
  );
});

export default InputBar;
