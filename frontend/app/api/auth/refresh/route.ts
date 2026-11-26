import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}));

    const refresh =
      request.cookies.get("refresh")?.value || body.refresh;

    if (typeof refresh !== "string" || !refresh) {
      return NextResponse.json(
        { detail: "Refresh token is required." },
        { status: 401 }
      );
    }

    const apiUrl = process.env.BACKEND_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL;

    if (!apiUrl) {
      console.error("NEXT_PUBLIC_API_URL is not defined");

      return NextResponse.json(
        { detail: "Authentication service is unavailable." },
        { status: 500 }
      );
    }

    const djangoResponse = await fetch(
      `${apiUrl.replace(/\/+$/, "")}/api/jwt/refresh/`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ refresh }),
        cache: "no-store",
      }
    );

    const data = await djangoResponse.json().catch(() => null);

    if (!djangoResponse.ok || !data?.access) {
      const response = NextResponse.json(
        { detail: data?.detail || "Token refresh failed." },
        { status: djangoResponse.status === 401 ? 401 : 502 }
      );

      if (djangoResponse.status === 401) {
        response.cookies.delete("access");
        response.cookies.delete("refresh");
      }

      return response;
    }

    const newRefresh =
      typeof data.refresh === "string" ? data.refresh : refresh;

    const isProduction = process.env.NODE_ENV === "production";

    const response = NextResponse.json({
      access: data.access,
      refresh: newRefresh,
    });

    const cookieOptions = {
      httpOnly: true,
      secure: isProduction,
      sameSite: "lax" as const,
      path: "/",
    };

    response.cookies.set("access", data.access, {
      ...cookieOptions,
      maxAge: 60 * 60,
    });

    response.cookies.set("refresh", newRefresh, {
      ...cookieOptions,
      maxAge: 60 * 60 * 24 * 7,
    });

    return response;
  } catch (error) {
    console.error("Auth refresh route failed:", error);

    return NextResponse.json(
      { detail: "Internal server error." },
      { status: 500 }
    );
  }
}