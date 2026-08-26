// Chat history sidebar. Cream background against the white chat pane.
// Supports rename (double-click a title), delete (hover to reveal), and
// clear-all. Footer shows the real signed-in account (name, email) and a
// sign-out action -- Sanadi AI now has real accounts, so this is genuine
// account chrome, not decorative.

"use client";

import { useState, useRef, useEffect } from "react";
import Monogram from "@/components/ui/Monogram";
import type { ChatSession, SanadiUser } from "@/lib/types";

// Roadmap items shown in the sidebar but not yet functional -- see the
// comment where these render for why they're disabled rather than
// removed or faked as working.
const ROADMAP_ITEMS = [
  {
    label: "Library",
    icon: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <path d="M3 2.5h10v11H3v-11z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round" />
        <path d="M6 2.5v11M9.5 2.5v11" stroke="currentColor" strokeWidth="1.3" />
      </svg>
    ),
  },
  {
    label: "Projects",
    icon: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <path
          d="M2 4.5a1 1 0 011-1h3.2l1.2 1.5H13a1 1 0 011 1V12a1 1 0 01-1 1H3a1 1 0 01-1-1V4.5z"
          stroke="currentColor"
          strokeWidth="1.3"
          strokeLinejoin="round"
        />
      </svg>
    ),
  },
  {
    label: "Scheduled",
    icon: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <circle cx="8" cy="8.5" r="5.5" stroke="currentColor" strokeWidth="1.3" />
        <path d="M8 5.5V8.5L10 10" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    label: "Customize",
    icon: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <path d="M3 4.5h10M3 8h10M3 11.5h10" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
        <circle cx="6" cy="4.5" r="1.3" fill="currentColor" />
        <circle cx="11" cy="8" r="1.3" fill="currentColor" />
        <circle cx="7" cy="11.5" r="1.3" fill="currentColor" />
      </svg>
    ),
  },
];

interface SidebarProps {
  sessions: ChatSession[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNewChat: () => void;
  onDelete: (id: string) => void;
  onRename: (id: string, title: string) => void;
  onClearAll: () => void;
  open: boolean;
  onClose: () => void;
  modelMode: string | null;
  user: SanadiUser;
  onLogout: () => void;
}

function groupSessions(sessions: ChatSession[]) {
  const startOfToday = new Date();
  startOfToday.setHours(0, 0, 0, 0);
  const todayCutoff = startOfToday.getTime();

  const sorted = [...sessions].sort((a, b) => b.createdAt - a.createdAt);
  return {
    today: sorted.filter((s) => s.createdAt >= todayCutoff),
    earlier: sorted.filter((s) => s.createdAt < todayCutoff),
  };
}

function SessionRow({
  session,
  active,
  onSelect,
  onDelete,
  onRename,
}: {
  session: ChatSession;
  active: boolean;
  onSelect: () => void;
  onDelete: () => void;
  onRename: (title: string) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(session.title);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (editing) inputRef.current?.focus();
  }, [editing]);

  function commit() {
    const trimmed = draft.trim();
    if (trimmed) onRename(trimmed);
    else setDraft(session.title);
    setEditing(false);
  }

  if (editing) {
    return (
      <input
        ref={inputRef}
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onBlur={commit}
        onKeyDown={(e) => {
          if (e.key === "Enter") commit();
          if (e.key === "Escape") {
            setDraft(session.title);
            setEditing(false);
          }
        }}
        className="w-full rounded-lg px-2.5 py-2 text-[0.8125rem] bg-sanadi-white border border-sanadi-black/30 outline-none"
      />
    );
  }

  return (
    <div
      className={`group flex items-center gap-1.5 rounded-lg px-2.5 py-2 cursor-pointer ${
        active ? "bg-sanadi-black text-sanadi-cream" : "hover:bg-sanadi-ink-08 text-sanadi-black"
      }`}
      onClick={onSelect}
      onDoubleClick={(e) => {
        e.stopPropagation();
        setEditing(true);
      }}
    >
      <span className="flex-1 text-[0.8125rem] truncate">{session.title || "New chat"}</span>
      <button
        type="button"
        aria-label="Delete chat"
        onClick={(e) => {
          e.stopPropagation();
          onDelete();
        }}
        className={`opacity-0 group-hover:opacity-100 shrink-0 text-xs leading-none px-1 ${
          active ? "text-sanadi-cream/70 hover:text-sanadi-cream" : "text-sanadi-ink-40 hover:text-sanadi-black"
        }`}
      >
        {"\u2715"}
      </button>
    </div>
  );
}

export default function Sidebar({
  sessions,
  activeId,
  onSelect,
  onNewChat,
  onDelete,
  onRename,
  onClearAll,
  open,
  onClose,
  modelMode,
  user,
  onLogout,
}: SidebarProps) {
  const { today, earlier } = groupSessions(sessions);

  function handleClearAll() {
    if (sessions.length === 0) return;
    if (window.confirm("Clear all chat history? This can't be undone.")) {
      onClearAll();
    }
  }

  return (
    <>
      {open && (
        <div
          className="fixed inset-0 bg-black/30 z-30 md:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed md:static inset-y-0 left-0 z-40 w-72 shrink-0 bg-sanadi-cream flex flex-col transition-transform duration-200 ${
          open ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        }`}
      >
        <div className="flex items-center gap-2.5 px-4 pt-5 pb-4">
          <Monogram size={28} />
          <span className="font-semibold text-sanadi-black tracking-tight">Sanadi</span>
        </div>

        <div className="px-3 pb-3">
          <button
            type="button"
            onClick={onNewChat}
            title="Ctrl+K"
            className="w-full flex items-center gap-2 rounded-lg border border-sanadi-ink-15 hover:border-sanadi-black/40 px-3 py-2 text-sm text-sanadi-black transition-colors"
          >
            <span className="text-base leading-none">+</span>
            New chat
          </button>
        </div>

        {/* Roadmap nav items -- visually present to match the layout
            convention of Claude/ChatGPT, but genuinely disabled: none of
            these have real backend features yet (chat grouping, task
            scheduling, persona settings). Marking them "Soon" and making
            them non-interactive keeps this honest rather than shipping
            buttons that silently do nothing when clicked. */}
        <div className="px-3 pb-3 space-y-0.5">
          {ROADMAP_ITEMS.map((item) => (
            <div
              key={item.label}
              aria-disabled="true"
              className="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sanadi-ink-40 cursor-not-allowed select-none"
            >
              <span className="shrink-0">{item.icon}</span>
              <span className="flex-1 text-[0.8125rem]">{item.label}</span>
              <span className="text-[0.625rem] uppercase tracking-wide border border-sanadi-ink-15 rounded-full px-1.5 py-0.5">
                Soon
              </span>
            </div>
          ))}
        </div>

        <nav className="flex-1 overflow-y-auto px-3 pb-3 space-y-4">
          {today.length > 0 && (
            <div>
              <p className="px-2.5 pb-1 text-[0.6875rem] font-medium uppercase tracking-wide text-sanadi-ink-40">
                Today
              </p>
              <div className="space-y-0.5">
                {today.map((s) => (
                  <SessionRow
                    key={s.id}
                    session={s}
                    active={s.id === activeId}
                    onSelect={() => onSelect(s.id)}
                    onDelete={() => onDelete(s.id)}
                    onRename={(title) => onRename(s.id, title)}
                  />
                ))}
              </div>
            </div>
          )}

          {earlier.length > 0 && (
            <div>
              <p className="px-2.5 pb-1 text-[0.6875rem] font-medium uppercase tracking-wide text-sanadi-ink-40">
                Earlier
              </p>
              <div className="space-y-0.5">
                {earlier.map((s) => (
                  <SessionRow
                    key={s.id}
                    session={s}
                    active={s.id === activeId}
                    onSelect={() => onSelect(s.id)}
                    onDelete={() => onDelete(s.id)}
                    onRename={(title) => onRename(s.id, title)}
                  />
                ))}
              </div>
            </div>
          )}

          {sessions.length === 0 && (
            <p className="px-2.5 text-[0.8125rem] text-sanadi-ink-40">
              Your conversations will appear here.
            </p>
          )}
        </nav>

        <div className="px-4 py-3 border-t border-sanadi-ink-15 space-y-2">
          {sessions.length > 0 && (
            <button
              type="button"
              onClick={handleClearAll}
              className="text-[0.6875rem] text-sanadi-ink-40 hover:text-sanadi-black"
            >
              Clear all history
            </button>
          )}

          <div className="flex items-center justify-between gap-2">
            <div className="min-w-0">
              <p className="text-[0.8125rem] text-sanadi-black truncate">{user.name}</p>
              <p className="text-[0.6875rem] text-sanadi-ink-40 truncate">
                {user.email}
                {modelMode === "base-model-only" && " \u00b7 base model"}
                {modelMode === "fine-tuned" && " \u00b7 fine-tuned"}
              </p>
            </div>
            <button
              type="button"
              onClick={onLogout}
              className="text-[0.6875rem] text-sanadi-ink-40 hover:text-sanadi-black shrink-0"
            >
              Sign out
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
