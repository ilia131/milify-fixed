"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useRouter } from "next/navigation";

import { useAppSelector } from "@/redux/hook";
import { Song } from "@/redux/features/playerSlice";
import { useDominantColorFromImage } from "@/shared/hooks/useDominantColorFromImage";
import { ParallaxCover } from "../../../shared/ui/Parallexcover/parallax-cover";
import { useLanguage } from "@/i18n/LanguageProvider";
import PlayShuffle from "@/components/Artist/ArtistButtons/PlayShuffle";

interface Props {
  image: string;
  songs: Song[];
}

export default function FreshTrackHero({
  image,
  songs,
}: Props) {
  useDominantColorFromImage(image);

  const router = useRouter();

  const { color, darkColor } = useAppSelector(
    (state) => state.player
  );

  const { t, locale } = useLanguage();

  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const update = () => {
      setScrollY(Math.min(window.scrollY * 0.12, 45));
    };

    window.addEventListener("scroll", update, {
      passive: true,
    });

    return () => {
      window.removeEventListener("scroll", update);
    };
  }, []);

  const isEnglish = locale === "en";

  return (
    <section className="relative h-[430px] w-full overflow-hidden">
      {/* =====================================================
          BACKGROUND
      ====================================================== */}

      <div
        className="absolute inset-0"
        style={{
          background: `
            linear-gradient(
              180deg,
              ${color} 0%,
              ${darkColor} 48%,
              #121212 100%
            )
          `,
          transition:
            "background 900ms cubic-bezier(0.4,0,0.2,1)",
        }}
      />

      {/* Blurred Cover */}
      <div
        className="absolute inset-0 overflow-hidden"
        style={{
          transform: `translateY(${scrollY}px) scale(1.05)`,
        }}
      >
        <Image
          src={image}
          alt=""
          fill
          priority
          className="
            scale-[1.35]
            object-cover
            blur-[70px]
            opacity-25
          "
        />
      </div>

      {/* Color Glow */}
      <div
        className="absolute inset-0"
        style={{
          background: `
            radial-gradient(
              ellipse at 50% 20%,
              ${color}99 0%,
              ${color}44 35%,
              transparent 70%
            )
          `,
        }}
      />

      {/* Dark Overlay */}
      <div className="absolute inset-0 bg-black/20" />

      {/* Bottom Gradient */}
      <div
        className="
          absolute
          inset-x-0
          bottom-0
          h-52
          bg-gradient-to-t
          from-[#121212]
          via-[#121212]/70
          to-transparent
        "
      />

      {/* =====================================================
          BACK BUTTON
      ====================================================== */}

      <button
        type="button"
        onClick={() => router.back()}
        aria-label="Go back"
        className="
          absolute
          left-4
          top-5
          z-30
          flex
          h-9
          w-9
          items-center
          justify-center
          rounded-full
          bg-black/40
          text-white
          backdrop-blur-md
          transition
          hover:bg-black/60
          active:scale-95
        "
      >
        {isEnglish ? (
          <ChevronLeft size={23} strokeWidth={2.2} />
        ) : (
          <ChevronRight size={23} strokeWidth={2.2} />
        )}
      </button>

      {/* =====================================================
          HERO CONTENT
      ====================================================== */}

      <div
        className="
          absolute
          inset-x-0
          bottom-16
          z-20
          flex
          flex-col
          items-center
          px-6
          text-center
        "
      >
        {/* Cover */}
        <div
          className="transition-transform duration-300"
          style={{
            transform: `translateY(${scrollY * 0.35}px)`,
          }}
        >
          <ParallaxCover src={image} />
        </div>

        {/* Type */}
        <p
          className="
            mt-5
            text-[11px]
            font-semibold
            uppercase
            tracking-[0.18em]
            text-white/70
          "
        >
          {t("home.playlist")}
        </p>

        {/* Title */}
        <h1
          className="
            mt-1
            text-[30px]
            font-bold
            leading-tight
            tracking-[-0.7px]
            text-white
            drop-shadow-2xl
          "
        >
          {t("home.freshTracksTitle")}
        </h1>

        {/* Description */}
        <p className="mt-1 text-[13px] text-white/65">
          {t("home.updatedWeekly")} • 2026
        </p>
      </div>

      {/* =====================================================
          PLAY / SHUFFLE
      ====================================================== */}

      <div
        className="
          absolute
          bottom-3
          left-0
          right-0
          z-30
          flex
          justify-end
          px-5
        "
      >
        <PlayShuffle songs={songs ?? []} />
      </div>
    </section>
  );
}