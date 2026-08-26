// Proxies thumbs up/down feedback to the backend, same auth pattern as chat.

import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.SANADI_BACKEND_URL ?? "http://localhost:8000";
const API_KEY = process.env.SANADI_API_KEY;

export async function POST(req: NextRequest) {
  const body = await req.json();
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (API_KEY) headers["X-API-Key"] = API_KEY;

  try {
    const res = await fetch(`${BACKEND_URL}/feedback`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));
    return NextResponse.json(data, { status: res.status });
  } catch {
    return NextResponse.json({ error: "Could not reach backend." }, { status: 502 });
  }
}
