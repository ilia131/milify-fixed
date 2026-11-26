"use client";

import Image from "next/image";
import { useState } from "react";
import Link from "next/link";
import { useDispatch } from "react-redux";
import { setQueue, Song } from "@/redux/features/playerSlice";

interface CardProps {
  item: Song;
  title: string;
  songs?: Song[];
  index?: number;
  isArtist?: boolean;
  variant?: "track" | "artist";
  variant2?: "trending" | "freshtrack";
}

const FreshTrackCard = ({
  item,
  title,
  songs,
  index,
  isArtist,
  variant,
  variant2,
}: CardProps) => {
  const [loaded, setLoaded] = useState(false);

  const dispatch = useDispatch();

  const handlePlay = () => {
    dispatch(
      setQueue({
        songs: songs?.length ? songs : [item],
        startIndex: index ?? 0,
      })
    );
  };

  const getTrackRoute = () => {
    if (variant2 === "trending") {
      return "/trending";
    }

    if (variant2 === "freshtrack") {
      return "/freshtrack";
    }

    return `/track/${item.unique_id}`;
  };

  const artistName =
    item.artistname ||
    item.artists?.[0] ||
    "";

  const songUniqueId =
    item.unique_id 

  const shouldPlayOnClick =
    variant === "track" &&
    variant2 !== "freshtrack" &&
    variant2 !== "trending";

  return (
    <div className="grid h-50.75 w-39.5 gap-3 snap-start shrink-0">
      {shouldPlayOnClick || isArtist ? (
        <div
          onClick={handlePlay}
          className="w-39.5 h-37.75 overflow-hidden rounded-lg cursor-pointer"
        >
          {!loaded && (
            <div className="absolute w-39.5 h-37.75 animate-pulse bg-zinc-800 rounded-lg" />
          )}

          <Image
            src={item.image_url ?? "/item.png"}
            width={158}
            height={151}
            alt={item.title || "Cover"}
            unoptimized
            onLoad={() => setLoaded(true)}
            className="w-full h-full object-cover rounded-lg"
          />
        </div>
      ) : (
        <Link
          href={getTrackRoute()}
          className="relative block w-39.5 h-37.75 overflow-hidden rounded-lg"
        >
          {!loaded && (
            <div className="absolute inset-0 animate-pulse bg-zinc-800 rounded-lg" />
          )}

          <Image
            src={item.image_url}
            width={158}
            height={151}
            alt={item.title || "Cover"}
            unoptimized
            onLoad={() => setLoaded(true)}
            className="w-full h-full object-cover rounded-lg"
          />
        </Link>
      )}

      <div className="flex flex-col min-w-0">
        {artistName && (
          <Link
            href={`/artist/${encodeURIComponent(artistName)}`}
            className="text-[rgba(255_255_255/0.55)] text-[15px] line-clamp-2 pl-0"
          >
            {item.artists?.length
              ? item.artists.join(", ")
              : artistName}
          </Link>
        )}

        {songUniqueId ? (
          <Link
            href={`/track/${songUniqueId}`}
            className="text-[rgba(255_255_255/0.55)] text-[13px] line-clamp-2 pl-0"
          >
            {item.title}
          </Link>
        ) : (
          <span className="text-[rgba(255_255_255/0.55)] text-[13px] line-clamp-2">
            {item.title}
          </span>
        )}
      </div>
    </div>
  );
};

export default FreshTrackCard;