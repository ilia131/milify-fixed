import {
  RefObject,
  useEffect,
} from "react";

import {
  Song,
} from "@/redux/features/playerSlice";

import {
  useGetSongSubscriptionAccessQuery,
} from "@/redux/services/artistApislice";

export function useAudioCore(
  audioRef: RefObject<HTMLAudioElement | null>,
  song: Song | undefined,
  isPlaying: boolean,
  volume: number
) {
  const {
    currentData: access,
    isLoading: accessLoading,
    isFetching: accessFetching,
  } = useGetSongSubscriptionAccessQuery(song?.unique_id ?? "", {
    skip: !song?.unique_id || !song.is_subscription_only,
    refetchOnMountOrArgChange: true,
  });

  const source = song?.is_subscription_only
    ? access?.can_play && !accessFetching
      ? access.track_url
      : null
    : song?.track_url;
  const canPlay = Boolean(source);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    if (!source) {
      audio.pause();
      if (audio.hasAttribute("src")) {
        audio.removeAttribute("src");
        audio.load();
      }
      return;
    }

    if (audio.getAttribute("src") !== source) {
      audio.pause();
      audio.src = source;
      audio.load();
    }

    if (isPlaying) {
      audio.play()?.catch((error: unknown) => {
        if (!(error instanceof DOMException && error.name === "AbortError")) {
          console.error("Audio play failed:", error);
        }
      });
    } else {
      audio.pause();
    }
  }, [audioRef, source, isPlaying]);

  /*
   * --------------------------------------------------
   * Volume
   * --------------------------------------------------
   */

  useEffect(() => {
    const audio = audioRef.current;

    if (!audio) {
      return;
    }

    audio.volume = Math.min(
      1,
      Math.max(0, volume)
    );
  }, [
    audioRef,
    volume,
  ]);

  /*
   * --------------------------------------------------
   * Seek
   * --------------------------------------------------
   */

  const seek = (percent: number) => {
    const audio = audioRef.current;

    if (!audio || !canPlay) {
      return;
    }

    const duration = audio.duration;

    if (
      !duration ||
      Number.isNaN(duration)
    ) {
      return;
    }

    const safePercent = Math.min(
      1,
      Math.max(0, percent)
    );

    audio.currentTime =
      safePercent * duration;
  };

  /*
   * --------------------------------------------------
   * Seek From Event
   * --------------------------------------------------
   */

  const seekFromEvent = (
    e: React.MouseEvent<HTMLDivElement>
  ) => {
    if (!canPlay) {
      return;
    }

    const rect =
      e.currentTarget.getBoundingClientRect();

    if (!rect.width) {
      return;
    }

    const percent =
      (e.clientX - rect.left) /
      rect.width;

    seek(percent);
  };

  return {
    seek,
    seekFromEvent,
    canPlay,
    accessLoading,
    accessFetching,
  };
}