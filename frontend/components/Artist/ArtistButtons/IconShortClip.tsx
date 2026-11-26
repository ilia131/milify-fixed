"use client";

import { useState } from "react";
import { useParams } from "next/navigation";

import images from "@/public/images";
import {
  useArtistDetailQuery,
  Shorts,
} from "@/redux/services/artistApislice";

import ReelsViewer from "@/features/explore/ui/reels-viewer";

const IconShortClip = () => {
  const params = useParams<{ artistname: string }>();

  const artistname = params.artistname
    ? decodeURIComponent(params.artistname)
    : "";

  const { data } = useArtistDetailQuery(artistname, {
    skip: !artistname,
  });

  const shorts = data?.shorts ?? [];

  // آخرین Short
  const latestShort = shorts[shorts.length - 1];

  const [isReelsOpen, setIsReelsOpen] = useState(false);

  // =========================================================
  // No Short
  // =========================================================

  if (!latestShort) {
    return (
      <img
        src={images.musiclogo.src}
        width={32}
        height={40}
        alt="shortartist"
        className="
          h-10
          w-8
          rounded-md
          border-[1.5px]
          border-solid
          border-[rgba(255,255,255,0.8)]
          object-cover
        "
      />
    );
  }

  // =========================================================
  // Convert API Short -> ReelsViewer Short
  // =========================================================

  const reelVideo: Shorts = {
    ...latestShort,
    video: latestShort.video_url,
  };

  // =========================================================
  // Render
  // =========================================================

  return (
    <>
      <button
        type="button"
        onClick={() => setIsReelsOpen(true)}
        className="
          relative
          h-10
          w-8
          shrink-0
          overflow-hidden
          rounded-md
          transition-transform
          active:scale-95
        "
      >
        <video
          src={latestShort.video_url}
          muted
          playsInline
          preload="metadata"
          className="
            h-10
            w-8
            rounded-md
            border-[1.5px]
            border-solid
            border-[rgba(255,255,255,0.8)]
            object-cover
          "
        />
      </button>

      {/* Reels Viewer */}
      {isReelsOpen && (
        <ReelsViewer
          videos={[reelVideo]}
          startIndex={0}
          onClose={() => setIsReelsOpen(false)}
        />
      )}
    </>
  );
};

export default IconShortClip;