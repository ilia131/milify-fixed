"use client";

import {
  useShortVideoShareMutation,
} from "@/redux/services/shortApi";

import {
  useToast,
} from "@/components/ToastProvider/ToastProvider";

interface UseReelsShareParams {
  origin?: string;
}

export const useReelsShare = ({
  origin,
}: UseReelsShareParams = {}) => {
  const {
    success,
    error: showError,
  } = useToast();

  // 👇 اسم mutation مشخص و جدا
  const [shareVideo] =
    useShortVideoShareMutation();

  const share = async (
    uuid: string,
    caption?: string
  ) => {
    const baseUrl =
      origin ??
      window.location.origin;

    const url =
      `${baseUrl}/reels/${uuid}`;

    try {
      if (navigator.share) {
        await navigator.share({
          title: "Milify",
          text:
            caption ||
            "Check this video on Milify",
          url,
        });
      } else {
        await navigator.clipboard.writeText(
          url
        );
      }

      // 👇 اینجا mutation واقعی RTK Query اجرا میشه
      await shareVideo(uuid).unwrap();

      success(
        "Link shared successfully."
      );
    } catch (error) {
      if (
        error instanceof DOMException &&
        error.name === "AbortError"
      ) {
        return;
      }

      console.error(error);

      showError(
        "Failed to share video."
      );
    }
  };

  return {
    share,
  };
};