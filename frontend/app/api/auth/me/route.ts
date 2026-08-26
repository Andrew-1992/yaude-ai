// Reports who's currently logged in (or null), by reading the httpOnly
// cookie server-side and asking the backend to verify it. Always returns
// 200 -- "not logged in" is a normal, expected state, not an error.

import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.SANADI_BACKEND_URL ?? "http://localhost:8000";

export async function GET(req: NextRequest) {
  const token = req.cookies.get("sanadi_session")?.value;
  if (!token) {
    return NextResponse.json({ user: null });
  }

  try {
    const backendRes = await fetch(`${BACKEND_URL}/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "ngrok-skip-browser-warning": "true",
      },
    });
    if (!backendRes.ok) {
      return NextResponse.json({ user: null });
    }
    const user = await backendRes.json();
    return NextResponse.json({ user });
  } catch {
    return NextResponse.json({ user: null });
  }
}
