// Small popover for adjusting response length and creativity (temperature).
// Persisted via lib/storage.ts so it survives a refresh.

"use client";

import { useState, useRef, useEffect } from "react";
import type { SanadiSettings } from "@/lib/types";

interface SettingsPanelProps {
  settings: SanadiSettings;
  onChange: (settings: SanadiSettings) => void;
}

export default function SettingsPanel({ settings, onChange }: SettingsPanelProps) {
  const [open, setOpen] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    if (open) document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open]);

  const temperatureLabel =
    settings.temperature <= 0.2 ? "Focused" : settings.temperature <= 0.7 ? "Balanced" : "Creative";

  return (
    <div className="relative" ref={panelRef}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-label="Response settings"
        aria-expanded={open}
        className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-sanadi-ink-08 text-sanadi-ink-70 transition-colors"
      >
        <svg width="17" height="17" viewBox="0 0 17 17" fill="none">
          <path
            d="M8.5 11a2.5 2.5 0 100-5 2.5 2.5 0 000 5z"
            stroke="currentColor"
            strokeWidth="1.3"
          />
          <path
            d="M13.7 9.9c.05-.3.08-.6.08-.9s-.03-.6-.08-.9l1.4-1.1a.4.4 0 00.1-.5l-1.3-2.3a.4.4 0 00-.47-.18l-1.65.66a5.7 5.7 0 00-1.55-.9l-.25-1.76a.4.4 0 00-.4-.32H7.42a.4.4 0 00-.4.32l-.25 1.76c-.57.2-1.1.51-1.55.9l-1.65-.66a.4.4 0 00-.47.18l-1.3 2.3a.4.4 0 00.1.5l1.4 1.1c-.05.3-.08.6-.08.9s.03.6.08.9l-1.4 1.1a.4.4 0 00-.1.5l1.3 2.3c.1.17.3.24.47.18l1.65-.66c.46.39.98.7 1.55.9l.25 1.76c.03.2.2.32.4.32h2.16c.2 0 .37-.13.4-.32l.25-1.76a5.7 5.7 0 001.55-.9l1.65.66c.17.06.37 0 .47-.18l1.3-2.3a.4.4 0 00-.1-.5l-1.4-1.1z"
            stroke="currentColor"
            strokeWidth="1"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {open && (
        <div className="absolute right-0 bottom-full mb-2 z-50 w-64 rounded-xl border border-sanadi-ink-15 bg-sanadi-white shadow-lg p-4">
          <p className="text-sm font-medium text-sanadi-black mb-3">Response settings</p>

          <div className="mb-4">
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs text-sanadi-ink-70">Response length</label>
              <span className="text-xs text-sanadi-ink-40">{settings.maxNewTokens} tokens</span>
            </div>
            <input
              type="range"
              min={128}
              max={2048}
              step={64}
              value={settings.maxNewTokens}
              onChange={(e) => onChange({ ...settings, maxNewTokens: Number(e.target.value) })}
              className="w-full accent-sanadi-black"
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs text-sanadi-ink-70">Creativity</label>
              <span className="text-xs text-sanadi-ink-40">{temperatureLabel}</span>
            </div>
            <input
              type="range"
              min={0}
              max={1}
              step={0.1}
              value={settings.temperature}
              onChange={(e) => onChange({ ...settings, temperature: Number(e.target.value) })}
              className="w-full accent-sanadi-black"
            />
          </div>
        </div>
      )}
    </div>
  );
}
