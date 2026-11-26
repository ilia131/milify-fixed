"use client";

import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import Link from "next/link";

import {
  Search,
  SlidersHorizontal,
  Play,
  Pause,
  ShoppingBag,
  ChevronRight,
  Sparkles,
  Music2,
} from "lucide-react";

import {
  useGetBeatsQuery,
  type Beat,
} from "@/redux/services/producerApiSlice";

/* =========================================================
   GENRES
========================================================= */

const genres = [
  { label: "All" },
  { label: "Trap", value: "TRAP" as const },
  { label: "Hip Hop", value: "HIPHOP" as const },
  { label: "Drill", value: "DRILL" as const },
  { label: "R&B", value: "RNB" as const },
  { label: "Pop", value: "POP" as const },
  { label: "Lo-Fi", value: "LOFI" as const },
];

type Genre =
  | "TRAP"
  | "HIPHOP"
  | "DRILL"
  | "RNB"
  | "POP"
  | "LOFI";

/* =========================================================
   PAGE
========================================================= */

export default function BeatsPage() {
  const [search, setSearch] = useState("");

  const [genre, setGenre] = useState<
    Genre | undefined
  >(undefined);

  const [playingId, setPlayingId] =
    useState<number | null>(null);

  const [isPlaying, setIsPlaying] =
    useState(false);

  const audioRef =
    useRef<HTMLAudioElement | null>(null);

  /* =======================================================
     GET BEATS
  ======================================================= */

  const {
    data: beats = [],
    isLoading,
    isFetching,
    isError,
  } = useGetBeatsQuery({
    search: search.trim() || undefined,
    genre,
    ordering: "-created_at",
  });

  /* =======================================================
     FEATURED
  ======================================================= */

  const featured = useMemo(
    () =>
      beats.filter(
        (beat) => beat.is_featured
      ),
    [beats]
  );

  /* =======================================================
     CLEANUP AUDIO
  ======================================================= */

  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.src = "";
      }
    };
  }, []);

  /* =======================================================
     PLAY PREVIEW
  ======================================================= */

  const handlePlay = async (beat: Beat) => {
    if (!beat.preview_audio) {
      return;
    }

    /* Same beat */
    if (
      playingId === beat.id &&
      audioRef.current
    ) {
      if (audioRef.current.paused) {
        try {
          await audioRef.current.play();
          setIsPlaying(true);
        } catch {
          setIsPlaying(false);
        }
      } else {
        audioRef.current.pause();
        setIsPlaying(false);
      }

      return;
    }

    /* Stop previous audio */
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current.src = "";
    }

    const audio =
      new Audio(beat.preview_audio);

    audio.preload = "metadata";

    audio.onplay = () => {
      setPlayingId(beat.id);
      setIsPlaying(true);
    };

    audio.onpause = () => {
      setIsPlaying(false);
    };

    audio.onended = () => {
      setPlayingId(null);
      setIsPlaying(false);
    };

    audio.onerror = () => {
      setPlayingId(null);
      setIsPlaying(false);
    };

    audioRef.current = audio;

    try {
      await audio.play();

      setPlayingId(beat.id);
      setIsPlaying(true);
    } catch {
      setPlayingId(null);
      setIsPlaying(false);
    }
  };

  /* =======================================================
     STOP PREVIEW
  ======================================================= */

  const handleStop = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }

    setPlayingId(null);
    setIsPlaying(false);
  };

  /* =======================================================
     UI
  ======================================================= */

  return (
    <main className="min-h-screen w-full min-w-0 overflow-x-hidden bg-[#050505] pb-28 text-white">
      {/* ===================================================
          HERO
      =================================================== */}

      <section className="px-3 pt-5 min-[360px]:px-4 min-[360px]:pt-7">
        <div className="relative overflow-hidden rounded-3xl border border-white/[0.06] bg-gradient-to-br from-[#111] via-[#090909] to-[#07130b] p-4 min-[360px]:p-5">
          <div className="absolute -right-12 -top-12 h-32 w-32 rounded-full bg-[#1ed760]/10 blur-3xl" />

          <div className="relative">
            <div className="mb-2 flex items-center gap-2">
              <Music2
                size={13}
                className="text-[#1ed760]"
              />

              <span className="text-[9px] font-bold tracking-[0.18em] text-[#1ed760] min-[360px]:text-[10px]">
                MILIFY MARKETPLACE
              </span>
            </div>

            <h1 className="max-w-[320px] text-[29px] font-bold leading-[1.04] tracking-tight min-[360px]:text-[34px]">
              Find your next
              <span className="text-[#1ed760]">
                {" "}
                sound.
              </span>
            </h1>

            <p className="mt-3 max-w-[330px] text-[11px] leading-5 text-white/40 min-[360px]:text-xs min-[360px]:leading-5">
              Discover beats from independent
              producers and build your next track.
            </p>

            <Link
              href="/sell"
              className="mt-5 inline-flex h-10 items-center justify-center gap-2 rounded-full bg-[#1ed760] px-4 text-[11px] font-bold text-black transition active:scale-95 min-[360px]:h-11 min-[360px]:px-5 min-[360px]:text-xs"
            >
              <ShoppingBag size={15} />
              Sell your beats
            </Link>
          </div>
        </div>
      </section>

      {/* ===================================================
          SEARCH
      =================================================== */}

      <section className="mt-5 px-3 min-[360px]:px-4">
        <div className="flex gap-2">
          <div className="relative min-w-0 flex-1">
            <Search
              size={16}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30"
            />

            <input
              value={search}
              onChange={(e) =>
                setSearch(e.target.value)
              }
              placeholder="Search beats..."
              className="h-11 w-full rounded-xl border border-white/[0.08] bg-white/[0.04] pl-9 pr-3 text-xs text-white outline-none placeholder:text-white/25 focus:border-[#1ed760]/40 min-[360px]:text-sm"
            />
          </div>

          <button
            type="button"
            className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-white/[0.08] bg-white/[0.04] text-white/50 active:scale-95"
          >
            <SlidersHorizontal size={17} />
          </button>
        </div>
      </section>

      {/* ===================================================
          GENRES
      =================================================== */}

      <section className="mt-4 w-full overflow-x-auto">
        <div className="flex w-max gap-1.5 px-3 min-[360px]:gap-2 min-[360px]:px-4">
          {genres.map((item) => {
            const active =
              genre === item.value ||
              (!genre && !item.value);

            return (
              <button
                key={item.label}
                type="button"
                onClick={() => {
                  if (item.value) {
                    setGenre(item.value);
                  } else {
                    setGenre(undefined);
                  }
                }}
                className={`shrink-0 rounded-full px-3 py-1.5 text-[10px] font-medium transition min-[360px]:px-4 min-[360px]:py-2 min-[360px]:text-xs ${
                  active
                    ? "bg-white text-black"
                    : "bg-white/[0.06] text-white/45 active:bg-white/10"
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </div>
      </section>

      {/* ===================================================
          FETCHING INDICATOR
      =================================================== */}

      {isFetching && !isLoading && (
        <div className="px-3 pt-3 min-[360px]:px-4">
          <div className="h-1 overflow-hidden rounded-full bg-white/[0.05]">
            <div className="h-full w-1/3 animate-pulse rounded-full bg-[#1ed760]" />
          </div>
        </div>
      )}

      {/* ===================================================
          ERROR
      =================================================== */}

      {isError && !isLoading && (
        <section className="mt-5 px-3 min-[360px]:px-4">
          <div className="rounded-2xl border border-red-500/10 bg-red-500/[0.05] px-4 py-5 text-center">
            <p className="text-xs text-red-300/70">
              Failed to load beats.
            </p>

            <p className="mt-1 text-[10px] text-white/25">
              Please try again.
            </p>
          </div>
        </section>
      )}

      {/* ===================================================
          FEATURED
      =================================================== */}

      {featured.length > 0 && (
        <section className="mt-7 px-3 min-[360px]:px-4">
          <SectionHeader
            title="Featured"
            subtitle="Hand-picked sounds"
            icon={<Sparkles size={15} />}
          />

          <div className="grid grid-cols-2 gap-2.5 min-[360px]:gap-3">
            {featured.map((beat) => (
              <BeatCard
                key={beat.id}
                beat={beat}
                playingId={playingId}
                isPlaying={isPlaying}
                onPlay={handlePlay}
                onStop={handleStop}
              />
            ))}
          </div>
        </section>
      )}

      {/* ===================================================
          ALL BEATS
      =================================================== */}

      <section className="mt-8 px-3 min-[360px]:px-4">
        <SectionHeader
          title="Explore beats"
          subtitle={`${beats.length} beats available`}
          action={
            <Link
              href="/producers"
              className="flex items-center gap-0.5 text-[10px] text-white/40 min-[360px]:text-xs"
            >
              Producers
              <ChevronRight size={13} />
            </Link>
          }
        />

        {isLoading ? (
          <BeatSkeleton />
        ) : beats.length === 0 ? (
          <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] px-4 py-14 text-center">
            <Music2
              size={28}
              className="mx-auto text-white/15"
            />

            <p className="mt-3 text-xs text-white/35">
              No beats found.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-2.5 min-[360px]:gap-3">
            {beats.map((beat) => (
              <BeatCard
                key={beat.id}
                beat={beat}
                playingId={playingId}
                isPlaying={isPlaying}
                onPlay={handlePlay}
                onStop={handleStop}
              />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

/* =========================================================
   SECTION HEADER
========================================================= */

function SectionHeader({
  title,
  subtitle,
  action,
  icon,
}: {
  title: string;
  subtitle: string;
  action?: React.ReactNode;
  icon?: React.ReactNode;
}) {
  return (
    <div className="mb-3 flex items-end justify-between gap-3">
      <div className="min-w-0">
        <div className="flex items-center gap-1.5">
          <h2 className="text-base font-bold min-[360px]:text-lg">
            {title}
          </h2>

          {icon && (
            <span className="text-[#1ed760]">
              {icon}
            </span>
          )}
        </div>

        <p className="mt-1 truncate text-[9px] text-white/30 min-[360px]:text-[10px]">
          {subtitle}
        </p>
      </div>

      {action}
    </div>
  );
}

/* =========================================================
   BEAT CARD
========================================================= */

function BeatCard({
  beat,
  playingId,
  isPlaying,
  onPlay,
  onStop,
}: {
  beat: Beat;
  playingId: number | null;
  isPlaying: boolean;
  onPlay: (beat: Beat) => void;
  onStop: () => void;
}) {
  const playing =
    playingId === beat.id && isPlaying;

  const hasPreview =
    Boolean(beat.preview_audio);

  return (
    <article className="min-w-0 overflow-hidden rounded-2xl border border-white/[0.07] bg-[#0d0d0d]">
      {/* ===================================================
          COVER
      =================================================== */}

      <div className="relative aspect-square overflow-hidden bg-[#151515]">
        <Link
          href={`/beats/${beat.id}`}
          className="absolute inset-0 z-0"
        >
          {beat.cover ? (
            <img
              src={beat.cover}
              alt={beat.title}
              className="h-full w-full object-cover transition duration-500"
            />
          ) : (
            <div className="flex h-full items-center justify-center bg-gradient-to-br from-[#171717] to-[#252525]">
              <span className="text-3xl font-bold text-white/15">
                {beat.title?.charAt(0)}
              </span>
            </div>
          )}
        </Link>

        {/* PLAY */}
        <button
          type="button"
          disabled={!hasPreview}
          aria-label={
            playing
              ? `Pause ${beat.title}`
              : `Play ${beat.title}`
          }
          onClick={() => {
            if (playing) {
              onStop();
            } else {
              onPlay(beat);
            }
          }}
          className={`absolute bottom-2 right-2 z-10 flex h-8 w-8 items-center justify-center rounded-full text-black shadow-lg transition active:scale-90 min-[360px]:h-9 min-[360px]:w-9 ${
            hasPreview
              ? "bg-[#1ed760]"
              : "cursor-not-allowed bg-white/20 text-white/30"
          }`}
        >
          {playing ? (
            <Pause
              size={13}
              fill="currentColor"
            />
          ) : (
            <Play
              size={13}
              fill="currentColor"
              className="ml-0.5"
            />
          )}
        </button>

        {/* PREVIEW LABEL */}

        {hasPreview && (
          <div className="absolute left-2 top-2 z-10 rounded-full border border-white/10 bg-black/60 px-2 py-1 backdrop-blur-md">
            <span className="text-[8px] font-medium text-white/70">
              PREVIEW
            </span>
          </div>
        )}
      </div>

      {/* ===================================================
          INFO
      =================================================== */}

      <div className="p-2.5 min-[360px]:p-3">
        <Link
          href={`/beats/${beat.id}`}
          className="block truncate text-[11px] font-semibold min-[360px]:text-xs"
        >
          {beat.title}
        </Link>

        <Link
          href={`/producers/${beat.producer.uuid}`}
          className="mt-1 block truncate text-[9px] text-white/35 min-[360px]:text-[10px]"
        >
          {beat.producer.producer_name}
        </Link>

        <div className="mt-2 flex items-center justify-between gap-1">
          <span className="shrink-0 text-[8px] text-white/25 min-[360px]:text-[9px]">
            {beat.bpm ?? "--"} BPM
          </span>

          <span className="min-w-0 truncate text-[9px] font-bold text-[#1ed760] min-[360px]:text-[10px]">
            {Number(
              beat.price
            ).toLocaleString()}{" "}
            تومان
          </span>
        </div>
      </div>
    </article>
  );
}

/* =========================================================
   SKELETON
========================================================= */

function BeatSkeleton() {
  return (
    <div className="grid grid-cols-2 gap-2.5 min-[360px]:gap-3">
      {Array.from({ length: 8 }).map(
        (_, i) => (
          <div
            key={i}
            className="overflow-hidden rounded-2xl bg-white/[0.04]"
          >
            <div className="aspect-square animate-pulse bg-white/[0.06]" />

            <div className="space-y-2 p-3">
              <div className="h-3 animate-pulse rounded bg-white/[0.06]" />

              <div className="h-2.5 w-2/3 animate-pulse rounded bg-white/[0.06]" />
            </div>
          </div>
        )
      )}
    </div>
  );
}