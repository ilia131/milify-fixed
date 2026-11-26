import { NextRequest, NextResponse } from "next/server";

const ALLOWED_HOST =
  "milify-bucket.s3.ir-thr-at1.arvanstorage.ir";

export async function GET(request: NextRequest) {
  try {
    const url = request.nextUrl.searchParams.get("url");

    if (!url) {
      return NextResponse.json(
        { error: "Missing image URL" },
        { status: 400 }
      );
    }

    const imageUrl = new URL(url);

    // فقط اجازه دسترسی به Bucket خود Milify
    if (imageUrl.hostname !== ALLOWED_HOST) {
      return NextResponse.json(
        { error: "Invalid image host" },
        { status: 403 }
      );
    }

    const response = await fetch(imageUrl.toString(), {
      cache: "no-store",
    });

    if (!response.ok) {
      return NextResponse.json(
        {
          error: "Failed to fetch image",
          status: response.status,
        },
        { status: response.status }
      );
    }

    const contentType =
      response.headers.get("content-type") || "";

    if (!contentType.startsWith("image/")) {
      return NextResponse.json(
        { error: "Resource is not an image" },
        { status: 415 }
      );
    }

    const buffer = await response.arrayBuffer();

    return new NextResponse(buffer, {
      status: 200,
      headers: {
        "Content-Type": contentType,
        "Cache-Control":
          "public, max-age=3600, s-maxage=3600",
        "Access-Control-Allow-Origin": "*",
      },
    });
  } catch (error) {
    console.error("Image proxy error:", error);

    return NextResponse.json(
      { error: "Image proxy failed" },
      { status: 500 }
    );
  }
}