"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import {
  Play,
  Pause,
  Music2,
  Headphones,
  ShoppingCart,
  Zap,
} from "lucide-react";

import { Beat } from "@/redux/services/producerApiSlice";

interface BeatCardProps {
  beat: Beat;
}

const BeatCard = ({ beat }: BeatCardProps) => {
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const [isPlaying, setIsPlaying] = useState(false);

  const handlePlay = async () => {
    if (!beat.preview_audio) {
      console.error("Preview audio not found:", beat.id);
      return;
    }

    try {
      // اگر همین بیت در حال پخش است → Pause
      if (audioRef.current && isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
        return;
      }

      // اگر audio قبلی وجود دارد، متوقفش کن
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      }

      const audio = new Audio(beat.preview_audio);

      audioRef.current = audio;

      audio.addEventListener("ended", () => {
        setIsPlaying(false);
      });

      audio.addEventListener("error", (error) => {
        console.error("Beat preview error:", error);
        setIsPlaying(false);
      });

      await audio.play();

      setIsPlaying(true);
    } catch (error) {
      console.error("Could not play beat:", error);
      setIsPlaying(false);
    }
  };

  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  return (
    <div
      className="
        group
        relative
        w-full
        overflow-hidden
        rounded-2xl
        border border-white/10
        bg-white/[0.035]
        backdrop-blur-xl
        transition-all
        duration-300
        hover:border-white/20
        hover:bg-white/[0.055]
      "
    >
      <div className="flex gap-4 p-3.5">

        {/* Cover + Play */}
        <div
          onClick={handlePlay}
          className="
            relative
            w-24
            h-24
            shrink-0
            overflow-hidden
            rounded-xl
            bg-white/10
            cursor-pointer
          "
        >
          {beat.cover ? (
            <Image
              src={beat.cover}
              alt={beat.title}
              fill
              sizes="96px"
              className="
                object-cover
                transition-transform
                duration-500
                group-hover:scale-105
              "
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <Music2 className="w-8 h-8 text-white/30" />
            </div>
          )}

          {/* Play / Pause */}
          <div
            className={`
              absolute
              inset-0
              flex
              items-center
              justify-center
              bg-black/30
              transition-opacity
              ${isPlaying ? "opacity-100" : "opacity-0 group-hover:opacity-100"}
            `}
          >
            <div
              className="
                w-10
                h-10
                rounded-full
                bg-white
                flex
                items-center
                justify-center
                shadow-xl
              "
            >
              {isPlaying ? (
                <Pause
                  size={17}
                  fill="black"
                  className="text-black"
                />
              ) : (
                <Play
                  size={17}
                  fill="black"
                  className="text-black ml-0.5"
                />
              )}
            </div>
          </div>
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0 flex flex-col justify-between py-0.5">
          <div>
            <div className="flex items-start justify-between gap-2">
              
              <Link
                href={`/beats/${beat.id}`}
                className="
                  text-white
                  font-semibold
                  text-[15px]
                  truncate
                  hover:text-white/70
                  transition
                "
                onClick={(e) => e.stopPropagation()}
              >
                {beat.title}
              </Link>

              {beat.is_featured && (
                <div
                  className="
                    shrink-0
                    flex
                    items-center
                    gap-1
                    px-2
                    py-1
                    rounded-full
                    bg-white/10
                    text-white/70
                    text-[9px]
                    font-medium
                  "
                >
                  <Zap size={10} />
                  Featured
                </div>
              )}
            </div>

            <Link
              href={`/producers/${beat.producer.uuid}`}
              className="
                block
                mt-1
                text-white/45
                text-xs
                truncate
                hover:text-white/70
                transition
              "
              onClick={(e) => e.stopPropagation()}
            >
              {beat.producer.producer_name}
            </Link>
          </div>

          {/* Meta */}
          <div className="flex items-center gap-2 mt-2">
            <span
              className="
                px-2
                py-1
                rounded-md
                bg-white/7
                text-white/55
                text-[10px]
                uppercase
              "
            >
              {beat.genre}
            </span>

            {beat.bpm && (
              <span className="text-white/35 text-[10px]">
                {beat.bpm} BPM
              </span>
            )}

            <span className="text-white/25 text-[10px]">
              •
            </span>

            <span className="flex items-center gap-1 text-white/35 text-[10px]">
              <Headphones size={11} />
              {beat.plays}
            </span>
          </div>
        </div>
      </div>

      {/* Bottom */}
      <div
        className="
          flex
          items-center
          justify-between
          border-t
          border-white/7
          px-3.5
          py-3
          bg-black/10
        "
      >
        <div>
          <span className="text-[10px] text-white/35 block">
            Starting from
          </span>

          <span className="text-white font-semibold text-sm">
            {Number(beat.price).toLocaleString()} تومان
          </span>
        </div>

        <Link
          href={`/beats/${beat.id}`}
          onClick={(e) => e.stopPropagation()}
          className="
            flex
            items-center
            gap-2
            px-4
            py-2
            rounded-full
            bg-white
            text-black
            text-xs
            font-semibold
            transition-all
            duration-200
            hover:bg-white/85
            active:scale-95
          "
        >
          <ShoppingCart size={14} />
          Buy
        </Link>
      </div>
    </div>
  );
};

export default BeatCard;