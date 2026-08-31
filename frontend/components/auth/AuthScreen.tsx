// Login / signup screen shown when no one is authenticated. Same
// black/cream/white system as the rest of the app -- no accent color,
// errors shown via text and border weight, not color.

"use client";

import { useState, FormEvent } from "react";
import Monogram from "@/components/ui/Monogram";
import { login, signup } from "@/lib/auth";
import type { SanadiUser } from "@/lib/types";

interface AuthScreenProps {
  onAuthenticated: (user: SanadiUser) => void;
}

export default function AuthScreen({ onAuthenticated }: AuthScreenProps) {
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const result =
        mode === "signup" ? await signup(name, email, password) : await login(email, password);
      onAuthenticated(result.user);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="h-screen flex items-center justify-center bg-sanadi-white px-4">
      <div className="w-full max-w-sm">
        <div className="flex flex-col items-center mb-8">
          <Monogram size={44} />
          <h1 className="mt-4 text-xl font-semibold text-sanadi-black tracking-tight">Yaude AI</h1>
          <p className="mt-1 text-sm text-sanadi-ink-40">Coding & research assistant</p>
        </div>

        <div className="flex rounded-xl border border-sanadi-ink-15 p-1 mb-6">
          <button
            type="button"
            onClick={() => {
              setMode("login");
              setError(null);
            }}
            className={`flex-1 text-sm py-1.5 rounded-lg transition-colors ${
              mode === "login" ? "bg-sanadi-black text-sanadi-cream" : "text-sanadi-ink-70"
            }`}
          >
            Sign in
          </button>
          <button
            type="button"
            onClick={() => {
              setMode("signup");
              setError(null);
            }}
            className={`flex-1 text-sm py-1.5 rounded-lg transition-colors ${
              mode === "signup" ? "bg-sanadi-black text-sanadi-cream" : "text-sanadi-ink-70"
            }`}
          >
            Create account
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3">
          {mode === "signup" && (
            <div>
              <label className="block text-xs text-sanadi-ink-70 mb-1">Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="w-full rounded-lg border border-sanadi-ink-15 px-3 py-2 text-sm text-sanadi-black focus:outline-none focus:border-sanadi-black/40"
              />
            </div>
          )}

          <div>
            <label className="block text-xs text-sanadi-ink-70 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full rounded-lg border border-sanadi-ink-15 px-3 py-2 text-sm text-sanadi-black focus:outline-none focus:border-sanadi-black/40"
            />
          </div>

          <div>
            <label className="block text-xs text-sanadi-ink-70 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              className="w-full rounded-lg border border-sanadi-ink-15 px-3 py-2 text-sm text-sanadi-black focus:outline-none focus:border-sanadi-black/40"
            />
            {mode === "signup" && (
              <p className="mt-1 text-[0.6875rem] text-sanadi-ink-40">At least 8 characters</p>
            )}
          </div>

          {error && (
            <p className="text-sm text-sanadi-ink-70 underline underline-offset-2 decoration-sanadi-ink-40">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-sanadi-black text-sanadi-cream py-2.5 text-sm font-medium disabled:opacity-50 transition-opacity"
          >
            {loading ? "Please wait..." : mode === "signup" ? "Create account" : "Sign in"}
          </button>
        </form>
      </div>
    </div>
  );
}
