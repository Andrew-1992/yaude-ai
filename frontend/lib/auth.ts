// Client-side auth helpers. Each of these calls a Next.js API route (never
// the FastAPI backend directly) -- the routes are what actually hold the
// httpOnly session cookie and forward it to the backend as a bearer token.

import type { SanadiUser } from "./types";

interface AuthResult {
  user: SanadiUser;
}

async function parseAuthError(res: Response): Promise<string> {
  const data = await res.json().catch(() => null);
  return data?.error ?? "Something went wrong. Please try again.";
}

export async function signup(name: string, email: string, password: string): Promise<AuthResult> {
  const res = await fetch("/api/auth/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password }),
  });
  if (!res.ok) throw new Error(await parseAuthError(res));
  return res.json();
}

export async function login(email: string, password: string): Promise<AuthResult> {
  const res = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error(await parseAuthError(res));
  return res.json();
}

export async function logout(): Promise<void> {
  await fetch("/api/auth/logout", { method: "POST" });
}

export async function getCurrentUser(): Promise<SanadiUser | null> {
  const res = await fetch("/api/auth/me");
  const data = await res.json().catch(() => ({ user: null }));
  return data.user ?? null;
}
