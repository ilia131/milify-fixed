import { useState } from "react";
import { useShortVideoLikeMutation } from "@/redux/services/shortApi";
import { useToast } from "@/components/ToastProvider/ToastProvider";
import type { Shorts } from "@/redux/services/artistApislice";

type DetailLike = {
  is_liked?: boolean;
  liked?: boolean;
  likes_count?: number;
} | null | undefined;

export function useVideoLikes(
  currentVideo: Shorts | undefined,
  detail: DetailLike
) {
  const { error: showError } = useToast();
  const [shortVideoLike] = useShortVideoLikeMutation();

  const [likedOverrides, setLikedVideos] = useState<
    Record<string, boolean>
  >({});
  const [countOverrides, setLikeCounts] = useState<
    Record<string, number>
  >({});
  const [showLikeAnimation, setShowLikeAnimation] =
    useState(false);

  const likedVideos = currentVideo ? {
    [currentVideo.uuid]: Boolean(detail?.is_liked ?? detail?.liked),
    ...likedOverrides,
  } : likedOverrides;
  const likeCounts = currentVideo ? {
    [currentVideo.uuid]: Math.max(0, Number(detail?.likes_count ?? 0)),
    ...countOverrides,
  } : countOverrides;

  const handleLike = async (uuid: string, forceLike = false) => {
    const currentlyLiked = likedVideos[uuid] ?? false;

    // Double-tap on already liked → only animation
    if (forceLike && currentlyLiked) {
      setShowLikeAnimation(true);
      setTimeout(() => setShowLikeAnimation(false), 700);
      return;
    }

    const currentCount =
      likeCounts[uuid] ??
      (uuid === currentVideo?.uuid
        ? Number(detail?.likes_count ?? 0)
        : 0);

    const nextLiked = forceLike ? true : !currentlyLiked;

    // Optimistic update
    setLikedVideos((prev) => ({ ...prev, [uuid]: nextLiked }));
    setLikeCounts((prev) => ({
      ...prev,
      [uuid]: Math.max(
        0,
        currentCount + (nextLiked ? 1 : currentlyLiked ? -1 : 0)
      ),
    }));

    try {
      const response = await shortVideoLike(uuid).unwrap();

      setLikedVideos((prev) => ({
        ...prev,
        [uuid]: response.liked,
      }));
      setLikeCounts((prev) => ({
        ...prev,
        [uuid]: Math.max(0, Number(response.likes_count ?? 0)),
      }));
    } catch (err) {
      console.error(err);

      // Rollback
      setLikedVideos((prev) => ({
        ...prev,
        [uuid]: currentlyLiked,
      }));
      setLikeCounts((prev) => ({
        ...prev,
        [uuid]: currentCount,
      }));

      showError("Failed to like video.");
    }
  };

  const handleDoubleClick = () => {
    if (!currentVideo) return;

    const alreadyLiked = likedVideos[currentVideo.uuid] ?? false;

    if (!alreadyLiked) {
      void handleLike(currentVideo.uuid, true);
    }

    setShowLikeAnimation(true);
    setTimeout(() => setShowLikeAnimation(false), 700);
  };

  return {
    likedVideos,
    likeCounts,
    showLikeAnimation,
    handleLike,
    handleDoubleClick,
  };
}