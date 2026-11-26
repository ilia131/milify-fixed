import ArtistPopularMusic from "../ArtistTabs/ArtistPopularMusic";
import ArtistPick from "../ArtistTabs/ArtistPick/ArtistPick";
import ArtistPopularRelease from "./ArtistPopularRelease";
import ArtistFeaturing from "./ArtistFeaturing";
import { Song } from "@/redux/features/playerSlice";
import Link from "next/link";

import ArtistVerify from "./ArtistVerify";
import { useLanguage } from "@/i18n/LanguageProvider";
import type { ArtistYouTubeVideo } from "@/redux/services/artistApislice";
import ShortVideoSection from "./ShortVideoSection";
import { Artist, Shorts } from "@/redux/services/artistApislice";

export type ArtistPickProps = {
  artistpick: {
    image: string;
    title: string;
  };
};

export type ArtistPickProps2 = {
  image: string;
  title: string;
};

interface ArtistContentSectionProps {
  songs?: Song[];
  artistpick?: ArtistPickProps2;
  shorts?: Shorts[];
  artistname: string;
  data: Artist;
  youtube_videos: ArtistYouTubeVideo[] | null;
}

const ArtistContentSection = ({
  songs,
  artistpick,
  shorts,
  artistname,
  data,
  youtube_videos,
}: ArtistContentSectionProps) => {
  const { t } = useLanguage();

  return (
    <section className="grid pb-50 overflow-hidden">
      <ArtistPopularMusic songs={songs} />

      {/* <ArtistPick artistpick={artistpick} /> */}

      <ArtistPopularRelease />

      <ArtistFeaturing
        songs={songs ?? []}
        artistname={artistname}
      />

      {(shorts?.length ?? 0) > 0 && (
        <ShortVideoSection
          shortvideo={shorts}
          artistname={artistname}
        />
      )}

      <ArtistVerify data={data ?? []} />

      {/* YouTube Videos */}
      {(youtube_videos?.length ?? 0) > 0 && (
  <div className="w-107.5 max-[430px]:w-full   pt-10">
    <div className="flex flex-col gap-6">
      {youtube_videos
        ?.filter((video) => video.is_active)
        .map((video) => (
          <div
            key={video.id}
            className="relative w-full aspect-video overflow-hidden   bg-black"
          >
            <iframe
              src={video.embed_url.replace(/&amp;/g, "&")}
              title={video.title || `${artistname} YouTube`}
              className="absolute inset-0 w-full h-full border-0"
              loading="lazy"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              allowFullScreen
            />
          </div>
        ))}
    </div>
  </div>
)}

      {/* Discography */}
      <div className="w-107.5 max-[430px]:w-full flex justify-center pt-10">
        <Link
          href={`/artist/discography/${artistname}`}
          className="
            h-12 w-40
            rounded-full
            border border-white/20
            flex items-center justify-center
            text-white text-sm font-medium
            hover:bg-white hover:text-black
            transition-all duration-200
          "
        >
          {t("artist.discography")}
        </Link>
      </div>
    </section>
  );
};

export default ArtistContentSection;