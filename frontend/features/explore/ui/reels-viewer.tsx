"use client";

import { useState } from "react";

import ReelActions from "../ui/reels/components/ReelActions";
import ReelInfo from "../ui/reels/components/ReelInfo";
import LikeAnimation from "../ui/reels/components/LikeAnimation";
import ReelVideo from "../ui/reels/components/ReelVideo";

import type { Shorts } from "@/redux/services/artistApislice";
import { useGetShortVideoDetailQuery } from "@/redux/services/artistApislice";
import { useShortVideoShareMutation } from "@/redux/services/shortApi";

import { useToast } from "@/components/ToastProvider/ToastProvider";
import { useAppSelector } from "@/redux/hook";

import {
  Heart,
  MessageCircle,
  X,
  SendHorizontal,
  LogIn,
} from "lucide-react";

import { useReelsPlayer } from "../hooks/useReelsPlayer";
import { useVideoLikes } from "../hooks/useVideoLikes";
import { useVideoComments } from "../hooks/useVideoComments";

interface Props {
  videos: Shorts[];
  startIndex: number;
  onClose: () => void;
}

const ReelsViewer = ({
  videos,
  startIndex,
  onClose,
}: Props) => {
  const { success, error: showError } = useToast();

  const [showComments, setShowComments] = useState(false);
  const [showLoginAlert, setShowLoginAlert] = useState(false);

  const [shortVideoShare] =
    useShortVideoShareMutation();

  // ─────────────────────────────────────────────
  // Authentication
  // ─────────────────────────────────────────────

  const isAuthenticated = useAppSelector(
    (state) => state.auth.isAuthenticated
  );

  // ─────────────────────────────────────────────
  // Player
  // ─────────────────────────────────────────────

  const {
    currentIndex,
    currentVideo,
    loadedVideos,
    isMusicPlaying,
    scrollContainerRef,
    videoRefs,
    containerRefs,
    handleVideoLoaded,
  } = useReelsPlayer(
    videos,
    startIndex
  );

  // ─────────────────────────────────────────────
  // Detail
  // ─────────────────────────────────────────────

  const { data: detail } =
    useGetShortVideoDetailQuery(
      currentVideo?.uuid ?? "",
      {
        skip: !currentVideo?.uuid,
      }
    );

  // ─────────────────────────────────────────────
  // Likes
  // ─────────────────────────────────────────────

  const {
    likedVideos,
    likeCounts,
    showLikeAnimation,
    handleLike,
    handleDoubleClick,
  } = useVideoLikes(
    currentVideo,
    detail
  );

  // ─────────────────────────────────────────────
  // Comments
  // ─────────────────────────────────────────────

  const {
    comments,
    commentsLoading,
    commentCount,
    commentText,
    setCommentText,
    isCreatingComment,
    commentLikes,
    commentLikeCounts,
    handleSendComment,
    handleCommentLike,
  } = useVideoComments(
    currentVideo,
    detail ,
    showComments
  );

  // ─────────────────────────────────────────────
  // Login guard
  // ─────────────────────────────────────────────

  const requireLogin = () => {
    setShowLoginAlert(true);
  };

  // ─────────────────────────────────────────────
  // Share
  // ─────────────────────────────────────────────

  const handleShare = async () => {
    if (!currentVideo) {
      return;
    }

    const url = `${window.location.origin}/reels/${currentVideo.uuid}`;

    try {
      if (navigator.share) {
        await navigator.share({
          title: "Milify",
          text:
            currentVideo.caption ||
            "Check this video on Milify",
          url,
        });
      } else {
        await navigator.clipboard.writeText(url);
      }

      await shortVideoShare(
        currentVideo.uuid
      ).unwrap();

      success("Link shared successfully.");
    } catch (err) {
      if (
        err instanceof DOMException &&
        err.name === "AbortError"
      ) {
        return;
      }

      console.error(err);

      showError(
        "Failed to share video."
      );
    }
  };

  return (
    <div
      className="fixed inset-0 z-[999] flex justify-center bg-black"
      style={{
        height: "100dvh",
        width: "100%",
      }}
    >
      <div
        ref={scrollContainerRef}
        className="relative h-[100dvh] w-110 max-[440px]:w-full overflow-y-scroll snap-y snap-mandatory overscroll-none"
        style={{
          scrollbarWidth: "none",
          msOverflowStyle: "none",
          WebkitOverflowScrolling:
            "touch",
        }}
      >
        {/* ─────────────────────────────────────── */}
        {/* Close */}
        {/* ─────────────────────────────────────── */}

        <button
          type="button"
          title="Close"
          aria-label="Close"
          onClick={onClose}
          className="fixed left-4 z-[1000] flex h-10 w-10 items-center justify-center rounded-full bg-black/30 text-white backdrop-blur-md transition active:scale-90"
          style={{
            top:
              "calc(env(safe-area-inset-top, 0px) + 1.5rem)",
          }}
        >
          <X
            size={24}
            strokeWidth={2}
          />
        </button>

        {/* ─────────────────────────────────────── */}
        {/* Videos */}
        {/* ─────────────────────────────────────── */}

        {videos.map((video, index) => {
          const isCurrent =
            index === currentIndex;

          const videoLiked =
            likedVideos[video.uuid] ??
            (isCurrent
              ? Boolean(
                  (
                    detail as
                      | {
                          is_liked?: boolean;
                        }
                      | undefined
                  )?.is_liked
                )
              : false);

          const videoLikeCount =
            likeCounts[video.uuid] ??
            (isCurrent
              ? Number(
                  (
                    detail as
                      | {
                          likes_count?: number;
                        }
                      | undefined
                  )?.likes_count ?? 0
                )
              : 0);

          return (
            <div
              key={video.uuid}
              data-index={index}
              ref={(el) => {
                containerRefs.current[index] =
                  el;
              }}
              className="relative flex h-[100dvh] w-full snap-start items-center justify-center overflow-hidden bg-black"
            >
              <ReelVideo
                src={video.video}
                isCurrent={isCurrent}
                isLoaded={Boolean(
                  loadedVideos[index]
                )}
                isMusicPlaying={
                  isMusicPlaying
                }
                videoRef={(el) => {
                  videoRefs.current[index] =
                    el;
                }}
                onLoaded={() =>
                  handleVideoLoaded(index)
                }
                onDoubleClick={
                  isCurrent
                    ? () => {
                        // Guest user
                        if (
                          !isAuthenticated
                        ) {
                          requireLogin();
                          return;
                        }

                        handleDoubleClick();
                      }
                    : undefined
                }
              />

              {/* Like animation */}

              <LikeAnimation
                visible={
                  isCurrent &&
                  showLikeAnimation
                }
              />

              {/* Actions */}

              {isCurrent && (
                <ReelActions
                  isLiked={videoLiked}
                  likeCount={
                    videoLikeCount
                  }
                  commentCount={
                    commentCount
                  }

                  // Like
                  onLike={() => {
                    if (
                      !isAuthenticated
                    ) {
                      requireLogin();
                      return;
                    }

                    void handleLike(
                      video.uuid
                    );
                  }}

                  // Comments
                  onComments={() => {
                    if (
                      !isAuthenticated
                    ) {
                      requireLogin();
                      return;
                    }

                    setShowComments(true);
                  }}

                  // Share
                  onShare={() =>
                    void handleShare()
                  }
                />
              )}

              {/* Reel info */}

              {isCurrent && detail && (
                <ReelInfo
                  username={
                    (
                      detail as {
                        user?: {
                          username?: string;
                        };
                      }
                    )?.user?.username
                  }
                  caption={
                    (
                      detail as {
                        caption?: string;
                      }
                    )?.caption
                  }
                />
              )}
            </div>
          );
        })}

        {/* ─────────────────────────────────────── */}
        {/* Comments Bottom Sheet */}
        {/* ─────────────────────────────────────── */}

        {showComments && (
          <>
            {/* Overlay */}

            <div
              className="fixed inset-0 z-[1100] bg-black/55 backdrop-blur-[2px]"
              onClick={() =>
                setShowComments(false)
              }
            />

            {/* Sheet */}

            <div
              className="fixed bottom-0 left-1/2 z-[1101] flex w-full max-w-[440px] -translate-x-1/2 flex-col rounded-t-[22px] bg-[#111111] text-white shadow-[0_-10px_40px_rgba(0,0,0,0.45)] animate-[slideUp_0.28s_ease-out]"
              style={{
                height:
                  "min(72dvh, 620px)",
                paddingBottom:
                  "env(safe-area-inset-bottom, 0px)",
              }}
              onClick={(e) =>
                e.stopPropagation()
              }
            >
              {/* Handle */}

              <div className="flex justify-center py-3">
                <div className="h-1 w-10 rounded-full bg-white/25" />
              </div>

              {/* Header */}

              <div className="relative flex h-12 items-center justify-center border-b border-white/10">
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
                  onClick={() =>
                    setShowComments(
                      false
                    )
                  }
                  className="absolute right-3 flex h-9 w-9 items-center justify-center rounded-full text-white/70 transition hover:bg-white/10 hover:text-white active:scale-90"
                >
                  <X size={20} />
                </button>
              </div>

              {/* List */}

              <div className="min-h-0 flex-1 overflow-y-auto px-4 py-3">
                {commentsLoading ? (
                  <div className="flex h-full items-center justify-center">
                    <div className="h-7 w-7 animate-spin rounded-full border-2 border-white/20 border-t-white" />
                  </div>
                ) : comments.length ===
                  0 ? (
                  <div className="flex h-full flex-col items-center justify-center text-center">
                    <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full border border-white/15">
                      <MessageCircle
                        size={30}
                        strokeWidth={
                          1.5
                        }
                      />
                    </div>

                    <p className="text-[15px] font-semibold">
                      No comments yet
                    </p>

                    <p className="mt-1 text-xs text-white/40">
                      Be the first to
                      comment.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-5">
                    {comments.map(
                      (
                        comment,
                        index
                      ) => {
                        const username =
                          comment.user
                            ?.username ??
                          comment.username ??
                          "user";

                        const text =
                          comment.text ??
                          comment.comment ??
                          "";

                        const commentId =
                          typeof comment.id ===
                          "number"
                            ? comment.id
                            : null;

                        const isCommentLiked =
                          commentId !==
                          null
                            ? commentLikes[
                                commentId
                              ] ??
                              comment.is_liked ??
                              false
                            : false;

                        const commentLikeCount =
                          commentId !==
                          null
                            ? commentLikeCounts[
                                commentId
                              ] ??
                              comment.likes_count ??
                              0
                            : comment.likes_count ??
                              0;

                        return (
                          <div
                            key={
                              comment.id ??
                              index
                            }
                            className="flex gap-3"
                          >
                            {/* Avatar */}

                            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-white/10 text-xs font-bold">
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
                                    ).toLocaleDateString(
                                      "en-US"
                                    )}
                                  </span>
                                )}
                              </div>

                              <p className="mt-1 text-[13px] leading-5 text-white/85">
                                {text}
                              </p>

                              {Boolean(
                                comment.replies_count
                              ) && (
                                <button
                                  type="button"
                                  className="mt-2 text-[11px] font-semibold text-white/40"
                                >
                                  View{" "}
                                  {
                                    comment.replies_count
                                  }{" "}
                                  replies
                                </button>
                              )}
                            </div>

                            {/* Like comment */}

                            <div className="flex flex-col items-center">
                              <button
                                type="button"
                                disabled={
                                  commentId ===
                                  null
                                }
                                onClick={() => {
                                  if (
                                    commentId ===
                                    null
                                  ) {
                                    return;
                                  }

                                  if (
                                    !isAuthenticated
                                  ) {
                                    requireLogin();
                                    return;
                                  }

                                  void handleCommentLike(
                                    comment
                                  );
                                }}
                                className="self-center text-white/40 transition active:scale-75 disabled:opacity-30"
                              >
                                <Heart
                                  size={16}
                                  fill={
                                    isCommentLiked
                                      ? "#ff3040"
                                      : "none"
                                  }
                                  strokeWidth={
                                    isCommentLiked
                                      ? 0
                                      : 1.8
                                  }
                                  className={
                                    isCommentLiked
                                      ? "text-[#ff3040]"
                                      : ""
                                  }
                                />
                              </button>

                              {commentLikeCount >
                                0 && (
                                <span className="mt-0.5 text-[9px] text-white/40">
                                  {commentLikeCount.toLocaleString(
                                    "en-US"
                                  )}
                                </span>
                              )}
                            </div>
                          </div>
                        );
                      }
                    )}
                  </div>
                )}
              </div>

              {/* Comment input */}

              <div className="border-t border-white/10 px-3 py-3">
                <div className="flex items-center gap-2 rounded-full bg-white/[0.07] px-3 py-1.5">
                  <input
                    type="text"
                    value={
                      commentText
                    }
                    onChange={(e) =>
                      setCommentText(
                        e.target.value
                      )
                    }
                    onKeyDown={(e) => {
                      if (
                        e.key ===
                        "Enter"
                      ) {
                        void handleSendComment();
                      }
                    }}
                    disabled={
                      isCreatingComment
                    }
                    placeholder="Add a comment..."
                    className="min-w-0 flex-1 bg-transparent py-2 text-[13px] text-white outline-none placeholder:text-white/35 disabled:opacity-50"
                  />

                  <button
                    type="button"
                    disabled={
                      !commentText.trim() ||
                      isCreatingComment
                    }
                    onClick={() =>
                      void handleSendComment()
                    }
                    className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-purple-400 transition active:scale-75 disabled:opacity-30"
                  >
                    <SendHorizontal
                      size={19}
                    />
                  </button>
                </div>
              </div>
            </div>
          </>
        )}

        {/* ─────────────────────────────────────── */}
        {/* Login Required Bottom Sheet */}
        {/* ─────────────────────────────────────── */}

        {showLoginAlert && (
          <>
            {/* Overlay */}

            <div
              className="fixed inset-0 z-[1200] bg-black/65 backdrop-blur-sm"
              onClick={() =>
                setShowLoginAlert(
                  false
                )
              }
            />

            {/* Login sheet */}

            <div
              className="fixed bottom-0 left-1/2 z-[1201] w-full max-w-[440px] -translate-x-1/2 rounded-t-[24px] bg-[#111111] px-5 pb-8 pt-4 text-white shadow-[0_-10px_40px_rgba(0,0,0,0.5)] animate-[slideUp_0.28s_ease-out]"
              onClick={(e) =>
                e.stopPropagation()
              }
            >
              {/* Handle */}

              <div className="mb-6 flex justify-center">
                <div className="h-1 w-10 rounded-full bg-white/20" />
              </div>

              {/* Icon */}

              <div className="flex justify-center">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-purple-500/15">
                  <LogIn
                    size={28}
                    className="text-purple-400"
                  />
                </div>
              </div>

              {/* Text */}

              <div className="mt-5 text-center">
                <h2 className="text-lg font-bold">
                  Login required
                </h2>

                <p className="mx-auto mt-2 max-w-[320px] text-sm leading-6 text-white/50">
                  Please log in to like
                  videos and leave
                  comments on Milify.
                </p>
              </div>

              {/* Login button */}

              <button
                type="button"
                onClick={() => {
                  setShowLoginAlert(
                    false
                  );

                  window.location.href =
                    "/auth/login";
                }}
                className="mt-6 h-12 w-full rounded-full bg-purple-600 text-sm font-bold text-white transition hover:bg-purple-500 active:scale-[0.98]"
              >
                Log in
              </button>

              {/* Cancel */}

              <button
                type="button"
                onClick={() =>
                  setShowLoginAlert(
                    false
                  )
                }
                className="mt-2 h-11 w-full rounded-full text-sm font-medium text-white/50 transition hover:bg-white/5 active:scale-[0.98]"
              >
                Maybe later
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ReelsViewer;
