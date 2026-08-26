// Owns all app state: sessions, streaming, settings, keyboard shortcuts.
// Sidebar and ChatWindow stay presentational -- this is the only place
// that knows about localStorage, the streaming fetch, or session structure.

"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import Sidebar from "./Sidebar";
import ChatWindow from "@/components/chat/ChatWindow";
import AuthScreen from "@/components/auth/AuthScreen";
import { loadSessions, saveSessions, makeSessionTitle, loadSettings, saveSettings } from "@/lib/storage";
import { streamChat, sendFeedback } from "@/lib/api";
import { getCurrentUser, logout as logoutRequest } from "@/lib/auth";
import type { ChatSession, SanadiSettings, SanadiUser } from "@/lib/types";
import type { InputBarHandle } from "@/components/chat/InputBar";

export default function AppShell() {
  const [user, setUser] = useState<SanadiUser | null>(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [streamingText, setStreamingText] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modelMode, setModelMode] = useState<string | null>(null);
  const [settings, setSettings] = useState<SanadiSettings>(loadSettings());
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [hydrated, setHydrated] = useState(false);

  const abortControllerRef = useRef<AbortController | null>(null);
  const inputRef = useRef<InputBarHandle>(null);
  // Tracks the user message currently streaming a response, for feedback
  // correlation once the exchange completes.
  const pendingUserTextRef = useRef<string>("");

  useEffect(() => {
    getCurrentUser().then((u) => {
      setUser(u);
      setAuthChecked(true);
    });
  }, []);

  useEffect(() => {
    setSessions(loadSessions());
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (hydrated) saveSessions(sessions);
  }, [sessions, hydrated]);

  useEffect(() => {
    saveSettings(settings);
  }, [settings]);

  const activeSession = sessions.find((s) => s.id === activeId) ?? null;
  const messages = activeSession?.messages ?? [];

  const handleNewChat = useCallback(() => {
    setActiveId(null);
    setError(null);
    setSidebarOpen(false);
    inputRef.current?.focus();
  }, []);

  function handleSelectSession(id: string) {
    setActiveId(id);
    setError(null);
    setSidebarOpen(false);
  }

  function handleDeleteSession(id: string) {
    setSessions((prev) => prev.filter((s) => s.id !== id));
    if (id === activeId) setActiveId(null);
  }

  function handleRenameSession(id: string, title: string) {
    setSessions((prev) => prev.map((s) => (s.id === id ? { ...s, title } : s)));
  }

  function handleClearAll() {
    setSessions([]);
    setActiveId(null);
  }

  // Global keyboard shortcuts: Ctrl/Cmd+K for new chat, Escape closes the
  // mobile sidebar overlay.
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        handleNewChat();
      }
      if (e.key === "Escape" && sidebarOpen) {
        setSidebarOpen(false);
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [sidebarOpen, handleNewChat]);

  async function runGeneration(sessionId: string, userText: string) {
    setError(null);
    setIsStreaming(true);
    setStreamingText("");
    pendingUserTextRef.current = userText;

    const controller = new AbortController();
    abortControllerRef.current = controller;

    let accumulated = "";

    try {
      const { mode } = await streamChat({
        message: userText,
        settings,
        signal: controller.signal,
        onToken: (token) => {
          accumulated += token;
          setStreamingText(accumulated);
        },
      });
      setModelMode(mode);

      setSessions((prev) =>
        prev.map((s) =>
          s.id === sessionId
            ? {
                ...s,
                messages: [
                  ...s.messages,
                  { role: "assistant", content: accumulated, timestamp: Date.now(), feedback: null },
                ],
              }
            : s
        )
      );
    } catch (err) {
      if ((err as Error).name === "AbortError") {
        // User hit stop -- keep whatever was streamed so far as the final
        // message rather than discarding it.
        setSessions((prev) =>
          prev.map((s) =>
            s.id === sessionId
              ? {
                  ...s,
                  messages: [
                    ...s.messages,
                    {
                      role: "assistant",
                      content: accumulated || "(stopped)",
                      timestamp: Date.now(),
                      feedback: null,
                    },
                  ],
                }
              : s
          )
        );
      } else {
        setError("Couldn't reach the backend. Is scripts/serve.py running on port 8000?");
      }
    } finally {
      setIsStreaming(false);
      setStreamingText("");
      abortControllerRef.current = null;
    }
  }

  async function handleSend(text: string) {
    let sessionId = activeId;

    if (!sessionId) {
      sessionId = crypto.randomUUID();
      const newSession: ChatSession = {
        id: sessionId,
        title: makeSessionTitle(text),
        messages: [{ role: "user", content: text, timestamp: Date.now() }],
        createdAt: Date.now(),
      };
      setSessions((prev) => [newSession, ...prev]);
      setActiveId(sessionId);
    } else {
      setSessions((prev) =>
        prev.map((s) =>
          s.id === sessionId
            ? { ...s, messages: [...s.messages, { role: "user", content: text, timestamp: Date.now() }] }
            : s
        )
      );
    }

    await runGeneration(sessionId, text);
  }

  function handleStop() {
    abortControllerRef.current?.abort();
  }

  async function handleRegenerate() {
    if (!activeSession) return;
    const msgs = activeSession.messages;
    const lastAssistantIdx = [...msgs].map((m) => m.role).lastIndexOf("assistant");
    if (lastAssistantIdx === -1) return;

    const lastUserMsg = [...msgs.slice(0, lastAssistantIdx)].reverse().find((m) => m.role === "user");
    if (!lastUserMsg) return;

    // Drop the old assistant response, then regenerate against the same
    // preceding user message.
    setSessions((prev) =>
      prev.map((s) =>
        s.id === activeSession.id ? { ...s, messages: msgs.slice(0, lastAssistantIdx) } : s
      )
    );

    await runGeneration(activeSession.id, lastUserMsg.content);
  }

  function handleFeedback(index: number, rating: "up" | "down") {
    if (!activeSession) return;
    const msgs = activeSession.messages;
    const assistantMsg = msgs[index];
    const precedingUser = [...msgs.slice(0, index)].reverse().find((m) => m.role === "user");
    if (!assistantMsg || !precedingUser) return;

    const newRating = assistantMsg.feedback === rating ? null : rating; // click again to un-set

    setSessions((prev) =>
      prev.map((s) =>
        s.id === activeSession.id
          ? {
              ...s,
              messages: s.messages.map((m, i) => (i === index ? { ...m, feedback: newRating } : m)),
            }
          : s
      )
    );

    if (newRating) {
      sendFeedback(precedingUser.content, assistantMsg.content, newRating);
    }
  }

  async function handleLogout() {
    await logoutRequest();
    setUser(null);
    setSessions([]);
    setActiveId(null);
  }

  if (!authChecked) {
    // Brief blank while we ask the server who's logged in -- avoids a
    // flash of the login screen for someone who's already signed in.
    return <div className="h-screen bg-sanadi-white" />;
  }

  if (!user) {
    return <AuthScreen onAuthenticated={setUser} />;
  }

  return (
    <div className="flex h-screen bg-sanadi-white">
      <Sidebar
        sessions={sessions}
        activeId={activeId}
        onSelect={handleSelectSession}
        onNewChat={handleNewChat}
        onDelete={handleDeleteSession}
        onRename={handleRenameSession}
        onClearAll={handleClearAll}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        modelMode={modelMode}
        user={user}
        onLogout={handleLogout}
      />

      <div className="flex-1 flex flex-col min-w-0">
        <div className="flex items-center gap-2 px-4 py-3 border-b border-sanadi-ink-08 md:hidden">
          <button
            type="button"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open chat history"
            className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-sanadi-ink-08 text-sanadi-black"
          >
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path
                d="M2.5 5H15.5M2.5 9H15.5M2.5 13H15.5"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
              />
            </svg>
          </button>
          <span className="font-semibold text-sanadi-black text-sm">Sanadi AI</span>
        </div>

        <ChatWindow
          ref={inputRef}
          messages={messages}
          streamingText={streamingText}
          isStreaming={isStreaming}
          error={error}
          modelMode={modelMode}
          settings={settings}
          onSettingsChange={setSettings}
          onSend={handleSend}
          onStop={handleStop}
          onRegenerate={handleRegenerate}
          onFeedback={handleFeedback}
          userName={user.name}
        />
      </div>
    </div>
  );
}
