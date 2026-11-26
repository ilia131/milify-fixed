import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const { access, refresh } = await request.json();

    if (!access || !refresh) {
      return NextResponse.json(
        { detail: "Access and refresh tokens are required." },
        { status: 400 }
      );
    }

    const response = NextResponse.json({
      success: true,
    });

    const isProduction = process.env.NODE_ENV === "production";

    response.cookies.set("access", access, {
      httpOnly: true,
      secure: isProduction,
      sameSite: "lax",
      path: "/",
    });

    response.cookies.set("refresh", refresh, {
      httpOnly: true,
      secure: isProduction,
      sameSite: "lax",
      path: "/",
    });

    return response;
  } catch {
    return NextResponse.json(
      { detail: "Invalid request." },
      { status: 400 }
    );
  }
}