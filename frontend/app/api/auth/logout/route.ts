// Clears the session cookie. No backend call needed -- logging out is
// purely a matter of the frontend forgetting the token.

import { NextResponse } from "next/server";

export async function POST() {
  const response = NextResponse.json({ status: "ok" });
  response.cookies.set("sanadi_session", "", { httpOnly: true, path: "/", maxAge: 0 });
  return response;
}
