"use client";

import type { RefCallback } from "react";

interface ReelVideoProps {
  src: string;
  isCurrent: boolean;
  isLoaded: boolean;
  isMusicPlaying: boolean;

  videoRef: RefCallback<HTMLVideoElement>;
  onLoaded: () => void;
  onDoubleClick?: () => void;
}

const ReelVideo = ({
  src,
  isCurrent,
  isLoaded,
  isMusicPlaying,
  videoRef,
  onLoaded,
  onDoubleClick,
}: ReelVideoProps) => {
  return (
    <>
      {/* Skeleton */}
      {!isLoaded && (
        <div
          className="
            absolute
            inset-0
            z-10
            animate-pulse
            bg-neutral-900
          "
        >
          <div
            className="
              absolute
              inset-0
              bg-gradient-to-b
              from-neutral-800/40
              via-neutral-900
              to-black
            "
          />

          <div
            className="
              absolute
              inset-0
              flex
              items-center
              justify-center
            "
          >
            <div
              className="
                h-10
                w-10
                animate-spin
                rounded-full
                border-2
                border-white/20
                border-t-white/80
              "
            />
          </div>

          <div
            className="
              absolute
              left-4
              space-y-3
            "
            style={{
              bottom:
                "calc(env(safe-area-inset-bottom, 0px) + 5rem)",
            }}
          >
            <div
              className="
                h-4
                w-32
                rounded
                bg-white/10
              "
            />

            <div
              className="
                h-3
                w-48
                rounded
                bg-white/10
              "
            />
          </div>
        </div>
      )}

      {/* Video */}
      <video
        ref={videoRef}
        src={src}
        className={`
          h-full
          w-full
          object-cover
          transition-opacity
          duration-300
          ${isLoaded ? "opacity-100" : "opacity-0"}
        `}
        loop
        playsInline
        muted={isMusicPlaying}
        preload={isCurrent ? "auto" : "metadata"}
        onLoadedData={onLoaded}
        onDoubleClick={onDoubleClick}
      />
    </>
  );
};

export default ReelVideo;