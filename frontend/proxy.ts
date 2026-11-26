import { NextRequest, NextResponse } from "next/server";

function parseJwt(token: string) {
  try {
    const base64 = token.split(".")[1];
    const json = Buffer.from(base64, "base64").toString();
    return JSON.parse(json);
  } catch {
    return null;
  }
}

export async function proxy(request: NextRequest) {
  const access = request.cookies.get("access")?.value;
  const refresh = request.cookies.get("refresh")?.value;

  const { pathname } = request.nextUrl;

  const isLoginPage = pathname.startsWith("/auth/login");

  // اگر لاگین نیست و صفحه لاگین هست، اجازه بده
  if (!access && isLoginPage) {
    return NextResponse.next();
  }

  // اگر access وجود ندارد
  if (!access) {
    return NextResponse.redirect(
      new URL("/auth/login", request.url)
    );
  }

  const decoded = parseJwt(access);
  const now = Math.floor(Date.now() / 1000);

  // اگر JWT معتبر نبود
  if (!decoded) {
    const response = NextResponse.redirect(
      new URL("/auth/login", request.url)
    );

    response.cookies.delete("access");
    response.cookies.delete("refresh");

    return response;
  }

  // اگر access token منقضی شده
  if (decoded.exp < now) {
    // اگر refresh هم نبود
    if (!refresh) {
      const response = NextResponse.redirect(
        new URL("/auth/login", request.url)
      );

      response.cookies.delete("access");

      return response;
    }

    try {
      const apiUrl = process.env.BACKEND_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL;

      if (!apiUrl) {
        console.error("NEXT_PUBLIC_API_URL is not defined");

        return NextResponse.redirect(
          new URL("/auth/login", request.url)
        );
      }

      const refreshResponse = await fetch(
        `${apiUrl}/api/jwt/refresh/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            refresh,
          }),
          cache: "no-store",
        }
      );

      // اگر refresh fail شد
      if (!refreshResponse.ok) {
        const response = NextResponse.redirect(
          new URL("/auth/login", request.url)
        );

        response.cookies.delete("access");
        response.cookies.delete("refresh");

        return response;
      }

      const data = await refreshResponse.json();

      if (!data.access) {
        const response = NextResponse.redirect(
          new URL("/auth/login", request.url)
        );

        response.cookies.delete("access");
        response.cookies.delete("refresh");

        return response;
      }

      const response = NextResponse.next();

      // access جدید
      response.cookies.set("access", data.access, {
        path: "/",
        sameSite: "lax",
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
      });

      // refresh جدید اگر وجود داشت
      if (data.refresh) {
        response.cookies.set("refresh", data.refresh, {
          path: "/",
          sameSite: "lax",
          httpOnly: true,
          secure: process.env.NODE_ENV === "production",
        });
      }

      return response;

    } catch (error) {
      console.error("JWT refresh failed:", error);

      const response = NextResponse.redirect(
        new URL("/auth/login", request.url)
      );

      response.cookies.delete("access");
      response.cookies.delete("refresh");

      return response;
    }
  }

  // اگر لاگین کرده و وارد login شد
  if (access && isLoginPage) {
    return NextResponse.redirect(
      new URL("/browse", request.url)
    );
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    // "/",
    "/auth/login",
    "/browse/:path*",
    "/search/:path*",
    "/library/:path*",
    "/explore/:path*",
    // "/artist/:path*",
    "/popular-albums/:path*",
    "/fresh-track/:path*",
    "/trending/:path*",
    "/settings/:path*",
    "/profile/:path*",
    "/beats/:path*",
    "/notifications/:path*",
    "/producers/:path*",
    "/purchases/:path*",
  ],
};
