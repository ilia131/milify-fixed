"use client";

import { X, MessageCircle } from "lucide-react";

import CommentItem from "./CommentItem";
import CommentInput from "./CommentInput";

import type { ReelComment } from "../../../../types/reels.types";

interface CommentsSheetProps {
  open: boolean;
  comments: ReelComment[];

  loading: boolean;
  commentCount: number;

  commentText: string;
  isCreatingComment: boolean;

  commentLikes: Record<number, boolean>;
  commentLikeCounts: Record<number, number>;

  onClose: () => void;
  onCommentTextChange: (value: string) => void;
  onSendComment: () => void;
  onCommentLike: (comment: ReelComment) => void;
}

const CommentsSheet = ({
  open,
  comments,
  loading,
  commentCount,
  commentText,
  isCreatingComment,
  commentLikes,
  commentLikeCounts,
  onClose,
  onCommentTextChange,
  onSendComment,
  onCommentLike,
}: CommentsSheetProps) => {
  if (!open) return null;

  return (
    <>
      {/* Overlay */}
      <div
        className="
          fixed
          inset-0
          z-[1100]
          bg-black/55
          backdrop-blur-[2px]
        "
        onClick={onClose}
      />

      {/* Sheet */}
      <div
        className="
          fixed
          bottom-0
          left-1/2
          z-[1101]
          flex
          w-full
          max-w-[440px]
          -translate-x-1/2
          flex-col
          rounded-t-[22px]
          bg-[#111111]
          text-white
          shadow-[0_-10px_40px_rgba(0,0,0,0.45)]
          animate-[slideUp_0.28s_ease-out]
        "
        style={{
          height: "min(72dvh, 620px)",
          paddingBottom:
            "env(safe-area-inset-bottom, 0px)",
        }}
        onClick={(e) =>
          e.stopPropagation()
        }
      >
        {/* Handle */}
        <div className="flex justify-center py-3">
          <div
            className="
              h-1
              w-10
              rounded-full
              bg-white/25
            "
          />
        </div>

        {/* Header */}
        <div
          className="
            relative
            flex
            h-12
            items-center
            justify-center
            border-b
            border-white/10
          "
        >
          <h2 className="text-[15px] font-bold">
            Comments

            {commentCount > 0 && (
              <span className="ml-1 text-white/40">
                {commentCount}
              </span>
            )}
          </h2>

          <button
            type="button"
            onClick={onClose}
            className="
              absolute
              right-3
              flex
              h-9
              w-9
              items-center
              justify-center
              rounded-full
              text-white/70
              transition
              hover:bg-white/10
              hover:text-white
              active:scale-90
            "
          >
            <X size={20} />
          </button>
        </div>

        {/* Comments */}
        <div
          className="
            min-h-0
            flex-1
            overflow-y-auto
            px-4
            py-3
          "
        >
          {loading ? (
            <div className="flex h-full items-center justify-center">
              <div
                className="
                  h-7
                  w-7
                  animate-spin
                  rounded-full
                  border-2
                  border-white/20
                  border-t-white
                "
              />
            </div>
          ) : comments.length === 0 ? (
            <div
              className="
                flex
                h-full
                flex-col
                items-center
                justify-center
                text-center
              "
            >
              <div
                className="
                  mb-4
                  flex
                  h-16
                  w-16
                  items-center
                  justify-center
                  rounded-full
                  border
                  border-white/15
                "
              >
                <MessageCircle
                  size={30}
                  strokeWidth={1.5}
                />
              </div>

              <p className="text-[15px] font-semibold">
                No comments yet
              </p>

              <p className="mt-1 text-xs text-white/40">
                Be the first to comment.
              </p>
            </div>
          ) : (
            <div className="space-y-5">
              {comments.map(
                (comment, index) => {
                  const commentId =
                    typeof comment.id ===
                    "number"
                      ? comment.id
                      : null;

                  const isLiked =
                    commentId !== null
                      ? commentLikes[
                          commentId
                        ] ??
                        comment.is_liked ??
                        false
                      : false;

                  const likeCount =
                    commentId !== null
                      ? commentLikeCounts[
                          commentId
                        ] ??
                        comment.likes_count ??
                        0
                      : comment.likes_count ??
                        0;

                  return (
                    <CommentItem
                      key={
                        comment.id ??
                        index
                      }
                      comment={comment}
                      isLiked={isLiked}
                      likeCount={likeCount}
                      onLike={() => {
                        if (
                          commentId !==
                          null
                        ) {
                          onCommentLike(
                            comment
                          );
                        }
                      }}
                    />
                  );
                }
              )}
            </div>
          )}
        </div>

        {/* Input */}
        <CommentInput
          value={commentText}
          disabled={isCreatingComment}
          onChange={onCommentTextChange}
          onSubmit={onSendComment}
        />
      </div>
    </>
  );
};

export default CommentsSheet;