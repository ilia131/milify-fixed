"use client";

import { Heart } from "lucide-react";

import type { ReelComment } from "../../../../types/reels.types";

interface CommentItemProps {
  comment: ReelComment;

  isLiked: boolean;
  likeCount: number;

  onLike: () => void;
}

const CommentItem = ({
  comment,
  isLiked,
  likeCount,
  onLike,
}: CommentItemProps) => {
  const username =
    comment.user?.username ??
    comment.username ??
    "user";

  const text =
    comment.text ??
    comment.comment ??
    "";

  return (
    <div className="flex gap-3">
      {/* Avatar */}
      <div
        className="
          flex
          h-9
          w-9
          shrink-0
          items-center
          justify-center
          rounded-full
          bg-white/10
          text-xs
          font-bold
        "
      >
        {username[0]?.toUpperCase()}
      </div>

      {/* Content */}
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span className="text-[13px] font-bold">
            @{username}
          </span>

          {comment.created_at && (
            <span className="text-[10px] text-white/35">
              {new Date(
                comment.created_at
              ).toLocaleDateString("en-US")}
            </span>
          )}
        </div>

        <p
          className="
            mt-1
            text-[13px]
            leading-5
            text-white/85
          "
        >
          {text}
        </p>

        {Boolean(comment.replies_count) && (
          <button
            type="button"
            className="
              mt-2
              text-[11px]
              font-semibold
              text-white/40
            "
          >
            View {comment.replies_count} replies
          </button>
        )}
      </div>

      {/* Like */}
      <div className="flex flex-col items-center">
        <button
          type="button"
          disabled={typeof comment.id !== "number"}
          onClick={onLike}
          className="
            self-center
            text-white/40
            transition
            active:scale-75
            disabled:opacity-30
          "
        >
          <Heart
            size={16}
            fill={
              isLiked
                ? "#ff3040"
                : "none"
            }
            strokeWidth={
              isLiked ? 0 : 1.8
            }
            className={
              isLiked
                ? "text-[#ff3040]"
                : ""
            }
          />
        </button>

        {likeCount > 0 && (
          <span
            className="
              mt-0.5
              text-[9px]
              text-white/40
            "
          >
            {likeCount.toLocaleString("en-US")}
          </span>
        )}
      </div>
    </div>
  );
};

export default CommentItem;