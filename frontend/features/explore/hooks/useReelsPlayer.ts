import { useEffect, useRef, useState } from "react";
import { useAppSelector } from "@/redux/hook";
import type { Shorts } from "@/redux/services/artistApislice";

export function useReelsPlayer(videos: Shorts[], startIndex: number) {
  const isMusicPlaying = useAppSelector(
    (state) => state.player.isPlaying
  );

  const [currentIndex, setCurrentIndex] = useState(startIndex);
  const [loadedVideos, setLoadedVideos] = useState<
    Record<number, boolean>
  >({});

  const scrollContainerRef = useRef<HTMLDivElement | null>(null);
  const videoRefs = useRef<(HTMLVideoElement | null)[]>([]);
  const containerRefs = useRef<(HTMLDivElement | null)[]>([]);

  // Scroll to initial index
  useEffect(() => {
    const container = scrollContainerRef.current;
    if (!container) return;

    requestAnimationFrame(() => {
      container.scrollTo({
        top: startIndex * container.clientHeight,
        behavior: "auto",
      });
    });
  }, [startIndex]);

  // Intersection Observer → change currentIndex
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;

          const index = Number(
            entry.target.getAttribute("data-index")
          );

          if (!Number.isNaN(index)) {
            setCurrentIndex(index);
          }
        });
      },
      { threshold: 0.8 }
    );

    containerRefs.current.forEach((el) => {
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, [videos.length]);

  // Play / Pause + mute based on music player
  useEffect(() => {
    videoRefs.current.forEach((video, index) => {
      if (!video) return;

      video.muted = isMusicPlaying;

      if (index === currentIndex) {
        video.play().catch(() => {});
      } else {
        video.pause();
        try {
          video.currentTime = 0;
        } catch {
          // ignore
        }
      }
    });
  }, [currentIndex, isMusicPlaying]);

  const handleVideoLoaded = (index: number) => {
    setLoadedVideos((prev) => ({ ...prev, [index]: true }));
  };

  return {
    currentIndex,
    currentVideo: videos[currentIndex] as Shorts | undefined,
    loadedVideos,
    isMusicPlaying,
    scrollContainerRef,
    videoRefs,
    containerRefs,
    handleVideoLoaded,
  };
}