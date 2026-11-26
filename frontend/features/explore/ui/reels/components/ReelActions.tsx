"use client";

import {
  Heart,
  MessageCircle,
  Send,
  MoreHorizontal,
} from "lucide-react";

interface ReelActionsProps {
  isLiked: boolean;
  likeCount: number;
  commentCount: number;

  onLike: () => void;
  onComments: () => void;
  onShare: () => void;
  onMore?: () => void;
}

const ReelActions = ({
  isLiked,
  likeCount,
  commentCount,
  onLike,
  onComments,
  onShare,
  onMore,
}: ReelActionsProps) => {
  return (
    <div
      className="
        absolute
        right-3
        z-30
        flex
        flex-col
        items-center
        gap-5
      "
      style={{
        bottom:
          "calc(env(safe-area-inset-bottom, 0px) + 7rem)",
      }}
    >
      {/* Like */}
      <div className="flex flex-col items-center">
        <button
          type="button"
          aria-label="Like"
          onClick={onLike}
          className="
            flex
            h-11
            w-11
            items-center
            justify-center
            rounded-full
            transition
            active:scale-75
          "
        >
          <Heart
            size={30}
            strokeWidth={isLiked ? 0 : 2}
            fill={isLiked ? "#ff3040" : "none"}
            className={
              isLiked
                ? "text-[#ff3040]"
                : "text-white"
            }
          />
        </button>

        <span
          className="
            mt-0.5
            text-[12px]
            font-semibold
            text-white
            drop-shadow-md
          "
        >
          {likeCount.toLocaleString("en-US")}
        </span>
      </div>

      {/* Comments */}
      <div className="flex flex-col items-center">
        <button
          type="button"
          aria-label="Comments"
          onClick={onComments}
          className="
            flex
            h-11
            w-11
            items-center
            justify-center
            rounded-full
            text-white
            transition
            active:scale-75
          "
        >
          <MessageCircle
            size={30}
            strokeWidth={2}
          />
        </button>

        <span
          className="
            mt-0.5
            text-[12px]
            font-semibold
            text-white
            drop-shadow-md
          "
        >
          {commentCount.toLocaleString("en-US")}
        </span>
      </div>

      {/* Share */}
      <button
        type="button"
        aria-label="Share"
        onClick={onShare}
        className="
          flex
          h-11
          w-11
          items-center
          justify-center
          rounded-full
          text-white
          transition
          active:scale-75
        "
      >
        <Send
          size={29}
          strokeWidth={2}
        />
      </button>

      {/* More */}
      <button
        type="button"
        aria-label="More"
        onClick={onMore}
        className="
          flex
          h-11
          w-11
          items-center
          justify-center
          rounded-full
          text-white
          transition
          active:scale-75
        "
      >
        <MoreHorizontal size={28} />
      </button>
    </div>
  );
};

export default ReelActions;