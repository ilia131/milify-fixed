"use client";

import Image from "next/image";
import { useParams } from "next/navigation";
import { useDominantColorFromImage } from "@/shared/hooks/useDominantColorFromImage";
import { useAppSelector, useAppDispatch } from "@/redux/hook";
import {
  playSingleSong,
  togglePlay,
  Lyrics,
} from "@/redux/features/playerSlice";
import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Heart,
  Share2,
  Disc3,
  Headphones,
  Loader2,
} from "lucide-react";

import {
  useToggleLikeSongMutation,
  useGetLikedStatusQuery,
} from "@/redux/services/likedSongs";

import { useGetSongDetailQuery } from "@/redux/services/songApiSlice";
import { toast } from "react-toastify";
import PlayGreenButton from "@/components/Artist/ArtistButtons/PlayGreenButton";

/* =========================================================
   IMAGE PROXY
   ========================================================= */

function getProxyImageUrl(imageUrl: string): string {
  return `/api/image-proxy?url=${encodeURIComponent(imageUrl)}`;
}

/* =========================================================
   COMPONENT
   ========================================================= */

export default function TrackDetail() {
  const dispatch = useAppDispatch();
  const params = useParams();
  const router = useRouter();
  // -----------------------------
  // PARAM GUARD
  // -----------------------------
  const handleArtistClick = () => {
    if (!artistName || artistName === "Unknown Artist") {
      return;
    }
  
    router.push(
      `/artist/${encodeURIComponent(artistName)}`
    );
  };
  const uniqueId =
    typeof params?.unique_id === "string"
      ? params.unique_id
      : "";

  const {
    data: song,
    isLoading,
    isError,
  } = useGetSongDetailQuery(uniqueId, {
    skip: !uniqueId,
  });

  // -----------------------------
  // PLAYER
  // -----------------------------

  const {
    color,
    darkColor,
    isPlaying,
    currentSong,
  } = useAppSelector((state) => state.player);

  // -----------------------------
  // LIKE
  // -----------------------------

  const [toggleLike, { isLoading: likeLoading }] =
    useToggleLikeSongMutation();

  const songId = song?.unique_id ?? "";

  const { data: likedStatus } =
    useGetLikedStatusQuery(
      songId ? [songId] : [],
      {
        skip: !songId,
      }
    );

  const liked = songId
    ? likedStatus?.[songId] ?? false
    : false;

  // -----------------------------
  // SHARE LOADING
  // -----------------------------

  const [isSharing, setIsSharing] = useState(false);

  // -----------------------------
  // IMAGE COLOR
  // -----------------------------

  useDominantColorFromImage(
    song?.image_url || ""
  );

  // -----------------------------
  // PLAY
  // -----------------------------

  const songIsPlaying =
    Boolean(
      song?.unique_id &&
        currentSong?.unique_id &&
        isPlaying &&
        currentSong.unique_id === song.unique_id
    );

  const handlePlay = () => {
    if (
      !song ||
      !song.unique_id ||
      !song.track_url
    ) {
      toast.error("This track is not available");
      return;
    }

    const isCurrentSong =
      currentSong?.unique_id === song.unique_id;

    if (isCurrentSong) {
      dispatch(togglePlay());
      return;
    }

    dispatch(
      playSingleSong({
        ...song,
        audioUrl: song.track_url,
      })
    );
  };

  // -----------------------------
  // LIKE
  // -----------------------------

  const handleLike = () => {
    if (!songId || likeLoading) return;

    toggleLike(songId);
  };

  // -----------------------------
  // SHARE STORY
  // -----------------------------

  const shareTrack = async () => {
    if (!song?.unique_id || !song.image_url) {
      toast.error("Track image is not available");
      return;
    }

    if (isSharing) return;

    setIsSharing(true);

    try {
      /*
       * IMPORTANT:
       * Do NOT send the Arvan URL directly to Canvas.
       *
       * Instead:
       *
       * Arvan image
       *      ↓
       * Next.js /api/image-proxy
       *      ↓
       * Same-origin image
       *      ↓
       * Canvas
       */

      const proxyImageUrl =
        getProxyImageUrl(song.image_url);

      

      const storyBlob =
        await createInstagramStory({
          imageUrl: proxyImageUrl,
          title:
            song.title || "Unknown Track",
          artist:
            song.artistname ||
            "Unknown Artist",
          album:
            song.album_name || "",
          trackUrl:
            `${window.location.origin}/track/${song.unique_id}`,
          primaryColor:
            color || "#6d28d9",
          secondaryColor:
            darkColor || "#111111",
        });

      const file = new File(
        [storyBlob],
        "milify-story.png",
        {
          type: "image/png",
        }
      );

      // -----------------------------
      // MOBILE WEB SHARE
      // -----------------------------

      if (
        typeof navigator !== "undefined" &&
        navigator.share &&
        navigator.canShare &&
        navigator.canShare({
          files: [file],
        })
      ) {
        await navigator.share({
          files: [file],
          title:
            `${song.artistname || ""} - ${
              song.title || ""
            }`,
          text: "Listen on Milify",
        });

        return;
      }

      // -----------------------------
      // FALLBACK DOWNLOAD
      // -----------------------------

      downloadStory(storyBlob);

      toast.info(
        "Story image created. Upload it to Instagram."
      );
    } catch (error) {
      console.error(
        "❌ Story share error:",
        error
      );

      // User cancelled native share.
      if (
        error instanceof DOMException &&
        error.name === "AbortError"
      ) {
        return;
      }

      toast.error(
        "Could not create the Instagram Story."
      );
    } finally {
      setIsSharing(false);
    }
  };

  // -----------------------------
  // LOADING
  // -----------------------------

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center text-white bg-[#121212]">
        Loading...
      </div>
    );
  }

  // -----------------------------
  // ERROR / EMPTY
  // -----------------------------

  if (
    isError ||
    !song ||
    !song.unique_id
  ) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center text-white bg-[#121212] px-5 text-center">
        <h1 className="text-2xl font-bold">
          Track not found
        </h1>

        <p className="text-zinc-500 mt-2">
          This track may have been removed or is
          temporarily unavailable.
        </p>
      </div>
    );
  }

  // -----------------------------
  // SAFE VALUES
  // -----------------------------

  const imageUrl =
    typeof song.image_url === "string" &&
    song.image_url.trim()
      ? song.image_url
      : "/images/default-song.png";

  const title =
    song.title?.trim() ||
    "Unknown Track";

  const artistName =
    song.artistname?.trim() ||
    "Unknown Artist";

  const albumName =
    song.album_name?.trim() ||
    "Single";

  const genreName =
    song.genre_name?.trim() ||
    "Unknown";

  const description =
    song.description?.trim() ||
    "No description available.";

  const lyrics = Array.isArray(song.lyrics)
    ? song.lyrics
    : [];

  const playCount =
    typeof song.play_count === "number"
      ? song.play_count
      : 0;

  const listeners =
    typeof song.unique_listeners === "number"
      ? song.unique_listeners
      : 0;

  const tempo =
    typeof song.tempo === "number"
      ? song.tempo
      : 0;

  const bgColor =
    color || "#181818";

  const bgDarkColor =
    darkColor || "#121212";

  // -----------------------------
  // UI
  // -----------------------------

  return (
    <main
      className="min-h-screen bg-[#121212] text-white pb-50"
      style={{
        background: `linear-gradient(
          180deg,
          ${bgColor} 0%,
          ${bgDarkColor} 40%,
          #121212 80%
        )`,
      }}
    >
      {/* HERO */}

      <section className="relative px-5 pt-8 pb-6">
        <div
          className="
            absolute
            inset-0
            opacity-30
            blur-3xl
            overflow-hidden
          "
        >
          <Image
            fill
            src={imageUrl}
            alt=""
            className="object-cover"
            sizes="100vw"
          />
        </div>

        <div className="relative flex flex-col items-center">
        <button
  type="button"
  onClick={handleArtistClick}
  aria-label={`View ${artistName} artist page`}
  className="
    block
    cursor-pointer
    rounded-md
    focus:outline-none
    focus-visible:ring-2
    focus-visible:ring-white/70
  "
>
  <Image
    src={imageUrl}
    alt={title}
    width={220}
    height={220}
    className="
      h-[220px]
      w-[220px]
      rounded-md
      object-cover
      shadow-2xl
      transition-transform
      duration-200
      hover:scale-[1.02]
    "
    priority
  />
</button>

          <div className="mt-6 text-center w-full">
            <p className="text-xs uppercase text-zinc-400">
              Song
            </p>

            <h1
              className="
                text-3xl
                font-black
                mt-2
                leading-tight
              "
            >
              {title}
            </h1>

            <div
  className="
    flex
    justify-center
    flex-wrap
    gap-2
    mt-3
    text-sm
    text-zinc-300
  "
>
  <button
    type="button"
    onClick={handleArtistClick}
    className="
      text-zinc-300
      transition-colors
      hover:text-white
      hover:underline
      cursor-pointer
    "
  >
    {artistName}
  </button>

  <span>•</span>

  <span>{albumName}</span>
</div>
          </div>
        </div>
      </section>

      {/* ACTIONS */}

      <section className="px-5 mt-2">
        <div className="flex items-center gap-5">
          <button
            type="button"
            onClick={handleLike}
            disabled={likeLoading}
            aria-label={
              liked
                ? "Unlike song"
                : "Like song"
            }
          >
            <Heart
              size={26}
              color={
                liked
                  ? "#1ed760"
                  : "#ffffff"
              }
              fill={
                liked
                  ? "#1ed760"
                  : "transparent"
              }
            />
          </button>

          <button
            type="button"
            onClick={shareTrack}
            disabled={isSharing}
            aria-label="Share track"
            className="
              flex
              items-center
              justify-center
              transition
              active:scale-90
              disabled:opacity-50
            "
          >
            {isSharing ? (
              <Loader2
                size={24}
                className="animate-spin"
              />
            ) : (
              <Share2 size={24} />
            )}
          </button>

          <div className="ml-auto">
            <PlayGreenButton
              onPlay={handlePlay}
              isPlaying={songIsPlaying}
            />
          </div>
        </div>
      </section>

      {/* STATS */}

      <section className="px-4 sm:px-6 md:px-8 mt-8">
        <h2 className="text-2xl md:text-3xl font-bold mb-5">
          About this track
        </h2>

        <div className="grid grid-cols-2 gap-3">
          <div className="bg-[#181818] rounded-lg p-4">
            <Disc3 />

            <p className="text-zinc-400 mt-3">
              Genre
            </p>

            <p className="font-semibold">
              {genreName}
            </p>
          </div>

          <div className="bg-[#181818] rounded-lg p-4">
            <Headphones />

            <p className="text-zinc-400 mt-3">
              Plays
            </p>

            <p className="font-semibold">
              {playCount}
            </p>
          </div>

          <div className="bg-[#181818] rounded-lg p-4">
            <p className="text-zinc-400">
              Tempo
            </p>

            <p className="font-semibold">
              {tempo} BPM
            </p>
          </div>

          <div className="bg-[#181818] rounded-lg p-4">
            <p className="text-zinc-400">
              Listeners
            </p>

            <p className="font-semibold">
              {listeners}
            </p>
          </div>
        </div>
      </section>

      {/* DESCRIPTION */}

      <section className="px-4 sm:px-6 md:px-8 mt-10">
        <h2 className="text-2xl md:text-3xl font-bold mb-4">
          Description
        </h2>

        <p className="text-zinc-400 leading-7">
          {description}
        </p>
      </section>

      {/* LYRICS */}

      <section className="px-4 sm:px-6 md:px-8 mt-10 pb-20">
        <h2 className="text-2xl md:text-3xl font-bold mb-4">
          Lyrics
        </h2>

        {lyrics.length > 0 ? (
          <div className="space-y-2">
            {lyrics.map(
              (
                line: Lyrics,
                index: number
              ) => (
                <p key={index}>
                  {line?.line || ""}
                </p>
              )
            )}
          </div>
        ) : (
          <div className="bg-[#181818] rounded-xl p-5">
            <p className="text-zinc-500">
              No lyrics available
            </p>
          </div>
        )}
      </section>
    </main>
  );
}

/* =========================================================
   INSTAGRAM STORY GENERATOR
   ========================================================= */

interface StoryOptions {
  imageUrl: string;
  title: string;
  artist: string;
  album: string;
  trackUrl: string;
  primaryColor: string;
  secondaryColor: string;
}

async function createInstagramStory({
  imageUrl,
  title,
  artist,
  album,
  trackUrl,
  primaryColor,
  secondaryColor,
}: StoryOptions): Promise<Blob> {
  const canvas =
    document.createElement("canvas");

  /*
   * Instagram Story:
   * 1080 × 1920
   */

  canvas.width = 1080;
  canvas.height = 1920;

  const ctx = canvas.getContext("2d");

  if (!ctx) {
    throw new Error(
      "Canvas is not supported"
    );
  }

  // -----------------------------
  // BACKGROUND
  // -----------------------------

  const gradient =
    ctx.createLinearGradient(
      0,
      0,
      0,
      canvas.height
    );

  gradient.addColorStop(
    0,
    primaryColor
  );

  gradient.addColorStop(
    0.45,
    secondaryColor
  );

  gradient.addColorStop(
    1,
    "#050505"
  );

  ctx.fillStyle = gradient;

  ctx.fillRect(
    0,
    0,
    canvas.width,
    canvas.height
  );

  // -----------------------------
  // DARK OVERLAY
  // -----------------------------

  const overlay =
    ctx.createLinearGradient(
      0,
      0,
      0,
      canvas.height
    );

  overlay.addColorStop(
    0,
    "rgba(0,0,0,0.10)"
  );

  overlay.addColorStop(
    0.55,
    "rgba(0,0,0,0.15)"
  );

  overlay.addColorStop(
    1,
    "rgba(0,0,0,0.75)"
  );

  ctx.fillStyle = overlay;

  ctx.fillRect(
    0,
    0,
    canvas.width,
    canvas.height
  );

  // -----------------------------
  // LOAD COVER
  // -----------------------------

  const cover =
    await loadImage(imageUrl);

  
  // -----------------------------
  // COVER SHADOW
  // -----------------------------

  ctx.save();

  ctx.shadowColor =
    "rgba(0,0,0,0.45)";

  ctx.shadowBlur = 60;

  ctx.shadowOffsetY = 30;

  roundRect(
    ctx,
    120,
    390,
    840,
    840,
    48
  );

  ctx.fillStyle =
    "rgba(0,0,0,0.35)";

  ctx.fill();

  ctx.restore();

  // -----------------------------
  // COVER
  // -----------------------------

  ctx.save();

  roundRect(
    ctx,
    120,
    390,
    840,
    840,
    48
  );

  ctx.clip();

  drawCoverCover(
    ctx,
    cover,
    120,
    390,
    840,
    840
  );

  ctx.restore();

  // -----------------------------
  // MILIFY LOGO
  // -----------------------------

  ctx.fillStyle =
    "rgba(255,255,255,0.95)";

  ctx.font =
    "bold 58px Arial";

  ctx.textAlign = "left";

  ctx.fillText(
    "milify",
    90,
    150
  );

  // -----------------------------
  // SMALL LABEL
  // -----------------------------

  ctx.fillStyle =
    "rgba(255,255,255,0.65)";

  ctx.font =
    "500 25px Arial";

  ctx.fillText(
    "LISTEN ON MILIFY",
    90,
    200
  );

  // -----------------------------
  // TRACK INFO
  // -----------------------------

  ctx.textAlign = "center";

  ctx.fillStyle = "#ffffff";

  ctx.font =
    "bold 58px Arial";

  const titleLines =
    wrapText(
      ctx,
      title,
      900
    );

  let titleY = 1360;

  for (const line of titleLines.slice(
    0,
    2
  )) {
    ctx.fillText(
      line,
      540,
      titleY
    );

    titleY += 70;
  }

  // -----------------------------
  // ARTIST
  // -----------------------------

  ctx.fillStyle =
    "rgba(255,255,255,0.82)";

  ctx.font =
    "500 38px Arial";

  ctx.fillText(
    artist,
    540,
    titleY + 15
  );

  // -----------------------------
  // ALBUM
  // -----------------------------

  if (album) {
    ctx.fillStyle =
      "rgba(255,255,255,0.52)";

    ctx.font =
      "400 27px Arial";

    ctx.fillText(
      album,
      540,
      titleY + 65
    );
  }

  // -----------------------------
  // CTA
  // -----------------------------

  const bottomY = 1740;

  ctx.fillStyle =
    "rgba(255,255,255,0.14)";

  roundRect(
    ctx,
    250,
    bottomY,
    580,
    90,
    45
  );

  ctx.fill();

  ctx.fillStyle = "#ffffff";

  ctx.font =
    "bold 28px Arial";

  ctx.fillText(
    "Open in Milify",
    540,
    bottomY + 58
  );
  // -----------------------------
  // EXPORT
  // -----------------------------

  return new Promise(
    (resolve, reject) => {
      canvas.toBlob(
        (blob) => {
          if (!blob) {
            reject(
              new Error(
                "Could not create image"
              )
            );

            return;
          }

          resolve(blob);
        },
        "image/png",
        1
      );
    }
  );
}

/* =========================================================
   IMAGE LOADER
   ========================================================= */

async function loadImage(
  src: string
): Promise<HTMLImageElement> {
  return new Promise(
    (resolve, reject) => {
      const img =
        new window.Image();

      /*
       * The proxy is same-origin,
       * but keeping anonymous here is safe.
       */

      img.crossOrigin = "anonymous";

      img.onload = () => {
        if (
          !img.naturalWidth ||
          !img.naturalHeight
        ) {
          console.error(
            "❌ Image loaded but has invalid dimensions:",
            {
              src,
              naturalWidth:
                img.naturalWidth,
              naturalHeight:
                img.naturalHeight,
            }
          );

          reject(
            new Error(
              "Image loaded but has invalid dimensions"
            )
          );

          return;
        }

   

        resolve(img);
      };

      img.onerror = (error) => {
        console.error(
          "❌ STORY IMAGE FAILED:",
          {
            src,
            error,
          }
        );

        reject(
          new Error(
            `Failed to load image: ${src}`
          )
        );
      };

      img.src = src;
    }
  );
}

/* =========================================================
   COVER DRAWER
   ========================================================= */

function drawCoverCover(
  ctx: CanvasRenderingContext2D,
  image: HTMLImageElement,
  x: number,
  y: number,
  width: number,
  height: number
) {
  const imageWidth =
    image.naturalWidth;

  const imageHeight =
    image.naturalHeight;

  if (
    !imageWidth ||
    !imageHeight
  ) {
    throw new Error(
      "Invalid image dimensions"
    );
  }

  const imageRatio =
    imageWidth / imageHeight;

  const targetRatio =
    width / height;

  let sourceWidth =
    imageWidth;

  let sourceHeight =
    imageHeight;

  let sourceX = 0;
  let sourceY = 0;

  if (
    imageRatio >
    targetRatio
  ) {
    sourceWidth =
      imageHeight *
      targetRatio;

    sourceX =
      (imageWidth -
        sourceWidth) /
      2;
  } else {
    sourceHeight =
      imageWidth /
      targetRatio;

    sourceY =
      (imageHeight -
        sourceHeight) /
      2;
  }

  ctx.drawImage(
    image,
    sourceX,
    sourceY,
    sourceWidth,
    sourceHeight,
    x,
    y,
    width,
    height
  );
}

/* =========================================================
   ROUNDED RECTANGLE
   ========================================================= */

function roundRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  width: number,
  height: number,
  radius: number
) {
  ctx.beginPath();

  ctx.moveTo(
    x + radius,
    y
  );

  ctx.lineTo(
    x + width - radius,
    y
  );

  ctx.quadraticCurveTo(
    x + width,
    y,
    x + width,
    y + radius
  );

  ctx.lineTo(
    x + width,
    y + height - radius
  );

  ctx.quadraticCurveTo(
    x + width,
    y + height,
    x + width - radius,
    y + height
  );

  ctx.lineTo(
    x + radius,
    y + height
  );

  ctx.quadraticCurveTo(
    x,
    y + height,
    x,
    y + height - radius
  );

  ctx.lineTo(
    x,
    y + radius
  );

  ctx.quadraticCurveTo(
    x,
    y,
    x + radius,
    y
  );

  ctx.closePath();
}

/* =========================================================
   TEXT WRAPPER
   ========================================================= */

function wrapText(
  ctx: CanvasRenderingContext2D,
  text: string,
  maxWidth: number
): string[] {
  const words =
    text.split(" ");

  const lines: string[] = [];

  let currentLine = "";

  for (const word of words) {
    const testLine =
      currentLine
        ? `${currentLine} ${word}`
        : word;

    const width =
      ctx.measureText(
        testLine
      ).width;

    if (
      width > maxWidth &&
      currentLine
    ) {
      lines.push(
        currentLine
      );

      currentLine = word;
    } else {
      currentLine = testLine;
    }
  }

  if (currentLine) {
    lines.push(
      currentLine
    );
  }

  return lines;
}

/* =========================================================
   DOWNLOAD FALLBACK
   ========================================================= */

function downloadStory(
  blob: Blob
) {
  const url =
    URL.createObjectURL(blob);

  const anchor =
    document.createElement("a");

  anchor.href = url;

  anchor.download =
    "milify-story.png";

  document.body.appendChild(
    anchor
  );

  anchor.click();

  anchor.remove();

  setTimeout(() => {
    URL.revokeObjectURL(url);
  }, 1000);
}