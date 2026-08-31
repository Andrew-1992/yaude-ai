// Proxies chat requests to the backend FastAPI /chat endpoint, passing the
// streamed response straight through to the browser rather than buffering
// it. Also forwards the abort signal both directions: if the browser
// aborts (stop-generating button), this fetch to the Python backend aborts
// too, which the backend detects as a client disconnect and uses to stop
// generation early.

import { NextRequest } from "next/server";

const BACKEND_URL = process.env.SANADI_BACKEND_URL ?? "http://localhost:8000";
const API_KEY = process.env.SANADI_API_KEY; // server-only, never sent to the browser

export async function POST(req: NextRequest) {
  const body = await req.json();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    // Bypasses ngrok's free-tier browser-warning interstitial page, which
    // would otherwise intercept every server-to-server request too, not
    // just first-time browser visits -- breaking chat entirely once
    // deployed behind an ngrok tunnel.
    "ngrok-skip-browser-warning": "true",
  };
  if (API_KEY) headers["X-API-Key"] = API_KEY;

  let backendRes: Response;
  try {
    backendRes = await fetch(`${BACKEND_URL}/chat`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
      signal: req.signal,
    });
  } catch {
    return new Response(
      JSON.stringify({ error: "Could not reach backend. Is it running on SANADI_BACKEND_URL?" }),
      { status: 502, headers: { "Content-Type": "application/json" } }
    );
  }

  if (!backendRes.ok || !backendRes.body) {
    const detail = await backendRes.json().catch(() => null);
    return new Response(JSON.stringify({ error: detail?.detail ?? "Backend request failed" }), {
      status: backendRes.status,
      headers: { "Content-Type": "application/json" },
    });
  }

  const mode = backendRes.headers.get("x-yaude-mode") ?? "unknown";
  return new Response(backendRes.body, {
    status: 200,
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "X-Yaude-Mode": mode,
    },
  });
}
