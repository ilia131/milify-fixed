import type { ReelDetail } from "../types/reels.types";

export const adaptReelDetail = (
  detail: unknown
): ReelDetail => {
  if (
    !detail ||
    typeof detail !== "object"
  ) {
    return {};
  }

  const data =
    detail as Record<string, unknown>;

  const user =
    data.user &&
    typeof data.user === "object"
      ? (
          data.user as Record<
            string,
            unknown
          >
        )
      : undefined;

  return {
    uuid:
      typeof data.uuid === "string"
        ? data.uuid
        : undefined,

    caption:
      typeof data.caption === "string"
        ? data.caption
        : undefined,

    is_liked:
      Boolean(data.is_liked),

    liked:
      Boolean(data.liked),

    likes_count:
      Number(data.likes_count ?? 0),

    comments_count:
      Number(
        data.comments_count ?? 0
      ),

    user: user
      ? {
          username:
            typeof user.username ===
            "string"
              ? user.username
              : undefined,

          avatar:
            typeof user.avatar ===
            "string"
              ? user.avatar
              : undefined,
        }
      : undefined,
  };
};