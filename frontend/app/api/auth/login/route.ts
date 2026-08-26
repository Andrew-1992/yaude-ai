// Logs in an existing account, same cookie-setting pattern as signup.

import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.SANADI_BACKEND_URL ?? "http://localhost:8000";

export async function POST(req: NextRequest) {
  const body = await req.json();

  let backendRes: Response;
  try {
    backendRes = await fetch(`${BACKEND_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "true",
      },
      body: JSON.stringify(body),
    });
  } catch {
    return NextResponse.json({ error: "Could not reach backend." }, { status: 502 });
  }

  const data = await backendRes.json().catch(() => null);

  if (!backendRes.ok) {
    return NextResponse.json(
      { error: data?.detail ?? "Sign in failed" },
      { status: backendRes.status }
    );
  }

  const response = NextResponse.json({ user: data.user });
  response.cookies.set("sanadi_session", data.token, {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 30,
  });
  return response;
}
