import { useEffect, useState } from "react";

import {
  useGetShortVideoCommentsQuery,
  useCreateShortVideoCommentMutation,
  useDeleteShortVideoCommentMutation,
  useShortVideoCommentLikeMutation,
} from "@/redux/services/shortApi";

import { useToast } from "@/components/ToastProvider/ToastProvider";

import type { Shorts } from "@/redux/services/artistApislice";

export interface CommentItem {
  id?: number | string;

  username?: string;

  user?: {
    username?: string;
    avatar?: string;
  };

  text?: string;
  comment?: string;
  created_at?: string;

  likes_count?: number;
  is_liked?: boolean;

  replies_count?: number;
}

export type DetailComments = {
  comments_count?: number;
} | null | undefined | Shorts;

export function useVideoComments(
  currentVideo: Shorts | undefined,
  detail: DetailComments,
  showComments: boolean
) {
  const { success, error: showError } = useToast();

  const {
    data: commentsData,
    isLoading: commentsLoading,
  } = useGetShortVideoCommentsQuery(
    currentVideo?.uuid ?? "",
    {
      skip: !currentVideo || !showComments,
    }
  );

  const [
    createShortVideoComment,
    { isLoading: isCreatingComment },
  ] = useCreateShortVideoCommentMutation();

  const [deleteShortVideoComment] =
    useDeleteShortVideoCommentMutation();

  const [shortVideoCommentLike] =
    useShortVideoCommentLikeMutation();

  const [commentText, setCommentText] =
    useState("");

  const [commentLikes, setCommentLikes] =
    useState<Record<number, boolean>>({});

  const [commentLikeCounts, setCommentLikeCounts] =
    useState<Record<number, number>>({});

  const [commentCounts, setCommentCounts] =
    useState<Record<string, number>>({});

  useEffect(() => {
    if (!currentVideo) return;

    const uuid = currentVideo.uuid;
    const apiCount = commentsData?.count;

    const detailCount = Number(
      detail?.comments_count ?? 0
    );

    const count =
      apiCount !== undefined
        ? Number(apiCount)
        : detailCount;

    // eslint-disable-next-line react-hooks/set-state-in-effect
    setCommentCounts((prev) => {
      if (
        prev[uuid] !== undefined &&
        count < prev[uuid]
      ) {
        return prev;
      }

      return {
        ...prev,
        [uuid]: Math.max(0, count),
      };
    });
  }, [
    currentVideo?.uuid,
    commentsData?.count,
    detail,
  ]);

  const comments =
    (commentsData?.results ?? []) as CommentItem[];

  const commentCount = currentVideo
    ? commentCounts[currentVideo.uuid] ??
      commentsData?.count ??
      Number(detail?.comments_count ?? 0)
    : 0;

  const handleSendComment = async () => {
    if (!currentVideo) return;

    const text = commentText.trim();

    if (!text || isCreatingComment) return;

    const uuid = currentVideo.uuid;

    const previousCount =
      commentCounts[uuid] ??
      Number(
        commentsData?.count ??
          detail?.comments_count ??
          0
      );

    try {
      await createShortVideoComment({
        uuid,
        text,
      }).unwrap();

      setCommentText("");

      setCommentCounts((prev) => ({
        ...prev,
        [uuid]: Math.max(
          0,
          previousCount + 1
        ),
      }));

      success("Comment added successfully.");
    } catch (err) {
      console.error(err);
      showError("Failed to add comment.");
    }
  };

  const handleCommentLike = async (
    comment: CommentItem
  ) => {
    if (typeof comment.id !== "number") {
      return;
    }

    const commentId = comment.id;

    const currentlyLiked =
      commentLikes[commentId] ??
      comment.is_liked ??
      false;

    const previousCount =
      commentLikeCounts[commentId] ??
      comment.likes_count ??
      0;

    const nextLiked = !currentlyLiked;

    setCommentLikes((prev) => ({
      ...prev,
      [commentId]: nextLiked,
    }));

    setCommentLikeCounts((prev) => ({
      ...prev,
      [commentId]: Math.max(
        0,
        previousCount +
          (nextLiked ? 1 : -1)
      ),
    }));

    try {
      const response =
        await shortVideoCommentLike(
          commentId
        ).unwrap();

      setCommentLikes((prev) => ({
        ...prev,
        [commentId]: response.liked,
      }));

      setCommentLikeCounts((prev) => ({
        ...prev,
        [commentId]: Math.max(
          0,
          Number(
            response.likes_count ?? 0
          )
        ),
      }));
    } catch (err) {
      console.error(err);

      setCommentLikes((prev) => ({
        ...prev,
        [commentId]: currentlyLiked,
      }));

      setCommentLikeCounts((prev) => ({
        ...prev,
        [commentId]: previousCount,
      }));

      showError("Failed to like comment.");
    }
  };

  const handleDeleteComment = async (
    commentId: number
  ) => {
    if (!currentVideo) return;

    try {
      await deleteShortVideoComment({
        commentId,
        uuid: currentVideo.uuid,
      }).unwrap();

      setCommentCounts((prev) => ({
        ...prev,
        [currentVideo.uuid]: Math.max(
          0,
          (prev[currentVideo.uuid] ?? 0) - 1
        ),
      }));

      success("Comment deleted.");
    } catch (err) {
      console.error(err);
      showError("Failed to delete comment.");
    }
  };

  return {
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
    handleDeleteComment,
  };
}