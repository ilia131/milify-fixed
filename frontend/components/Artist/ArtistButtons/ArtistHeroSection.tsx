"use client";

import Image from "next/image";
import ArtistName from "../ArtistName";
import ArtistButtons from "./ArtistButtons";
import type { Viewport } from "next";
import { Artist } from "@/redux/services/artistApislice";
import { Song } from "@/redux/features/playerSlice";
import { useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: "cover",
};

interface ArtistHeroSectionProps {
  image: string | undefined;
  artistname: string | undefined;
  data: Artist;
  songs?: Song[];
}

const ArtistHeroSection = ({
  image,
  artistname,
  data,
  songs,
}: ArtistHeroSectionProps) => {
  const router = useRouter();

  return (
    <section className="relative w-full h-117 overflow-hidden -mt-[env(safe-area-inset-top)]">
      <Image
        src={image ?? "/item.jpg"}
        alt={artistname || ""}
        fill
        className="object-cover"
        priority
      />

      {/* Back Button */}
      <button
        type="button"
        onClick={() => router.back()}
        aria-label="Back"
        className="
          absolute
          left-4
          z-30
          flex
          h-10
          w-10
          items-center
          justify-center
          rounded-full
          bg-black/30
          text-white
          backdrop-blur-md
          transition
          active:scale-90
        "
        style={{
          top: "calc(env(safe-area-inset-top, 0px) + 1rem)",
        }}
      >
        <ArrowLeft
          size={23}
          strokeWidth={2}
        />
      </button>

      <ArtistName artistname={artistname} />

      <ArtistButtons
        data={data}
        songs={songs ?? []}
      />
    </section>
  );
};

export default ArtistHeroSection;