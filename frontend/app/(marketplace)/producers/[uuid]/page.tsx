"use client";

import {
  use,
  useEffect,
  useRef,
  useState,
} from "react";
import Link from "next/link";

import {
  ArrowLeft,
  BadgeCheck,
  ChevronRight,
  Instagram,
  Youtube,
  Play,
  Pause,
  Music2,
  UserRound,
  ShoppingBag,
} from "lucide-react";

import {
  useGetProducerProfileQuery,
  useGetProducerBeatsQuery,
  type Beat,
} from "@/redux/services/producerApiSlice";

export default function ProducerDetailPage({
  params,
}: {
  params: Promise<{ uuid: string }>;
}) {
  const { uuid } = use(params);

  const [search] = useState("");

  const [playingId, setPlayingId] =
    useState<number | null>(null);

  const [isPlaying, setIsPlaying] =
    useState(false);

  const audioRef =
    useRef<HTMLAudioElement | null>(null);

  const {
    data: producer,
    isLoading: producerLoading,
    isError: producerError,
  } = useGetProducerProfileQuery(uuid);

  const {
    data: beats = [],
    isLoading: beatsLoading,
  } = useGetProducerBeatsQuery({
    uuid,
    search: search || undefined,
    ordering: "-created_at",
  });

  /* =======================================================
     CLEANUP AUDIO
  ======================================================= */

  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.src = "";
        audioRef.current = null;
      }
    };
  }, []);

  /* =======================================================
     PLAY PREVIEW
  ======================================================= */

  const handlePlayPreview = async (
    beat: Beat
  ) => {
    if (!beat.preview_audio) {
      return;
    }

    /*
     * Same beat
     */
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

    /*
     * Stop previous audio
     */
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current.src = "";
      audioRef.current = null;
    }

    /*
     * Create new audio
     */
    const audio = new Audio(
      beat.preview_audio
    );

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
     LOADING
  ======================================================= */

  if (producerLoading) {
    return <ProducerDetailSkeleton />;
  }

  /* =======================================================
     ERROR
  ======================================================= */

  if (producerError || !producer) {
    return (
      <main className="min-h-screen bg-[#050505] px-4 py-6 text-white">
        <Link
          href="/producers"
          className="inline-flex items-center gap-2 text-xs text-white/50"
        >
          <ArrowLeft size={16} />
          Back to producers
        </Link>

        <div className="mt-20 text-center">
          <UserRound
            size={32}
            className="mx-auto text-white/15"
          />

          <h1 className="mt-4 text-lg font-bold">
            Producer not found
          </h1>

          <p className="mt-2 text-xs text-white/30">
            This producer may no longer be available.
          </p>
        </div>
      </main>
    );
  }

  /* =======================================================
     PAGE
  ======================================================= */

  return (
    <main className="min-h-screen w-full overflow-x-hidden bg-[#050505] pb-28 text-white pb-50">
      <div className="mx-auto w-full max-w-6xl px-3 pt-4 min-[360px]:px-4 sm:px-6 lg:px-8">

        {/* =================================================
            TOP BAR
        ================================================= */}

        <header className="flex items-center justify-between">
          <Link
            href="/producers"
            className="flex h-9 items-center gap-2 rounded-full border border-white/[0.08] bg-white/[0.04] px-3 text-[10px] text-white/60 transition active:scale-95 min-[360px]:text-xs"
          >
            <ArrowLeft size={15} />
            <span>Producers</span>
          </Link>

          <Link
            href="/sell"
            className="flex h-9 items-center gap-1.5 rounded-full bg-[#1ed760] px-3 text-[10px] font-bold text-black transition active:scale-95 min-[360px]:h-10 min-[360px]:px-4 min-[360px]:text-xs"
          >
            <ShoppingBag size={14} />
            Sell
          </Link>
        </header>

        {/* =================================================
            COVER
        ================================================= */}

        <section className="relative mt-4 overflow-hidden rounded-3xl border border-white/[0.07] bg-[#101010]">
          <div className="relative h-[155px] min-[360px]:h-[175px] sm:h-[260px]">
            {producer.cover_image ? (
              <img
                src={producer.cover_image}
                alt=""
                className="h-full w-full object-cover"
              />
            ) : (
              <div className="h-full w-full bg-[radial-gradient(circle_at_30%_20%,rgba(30,215,96,0.22),transparent_35%),radial-gradient(circle_at_80%_70%,rgba(130,70,255,0.20),transparent_40%),#101010]" />
            )}

            <div className="absolute inset-0 bg-gradient-to-t from-black via-black/20 to-transparent" />
          </div>

          {/* AVATAR */}

          <div className="absolute bottom-[-1px] left-4 flex translate-y-1/2 items-end min-[360px]:left-5">
            <div className="flex h-[70px] w-[70px] items-center justify-center overflow-hidden rounded-full border-4 border-[#050505] bg-[#151515] min-[360px]:h-[78px] min-[360px]:w-[78px]">
              {producer.profile_pic ? (
                <img
                  src={producer.profile_pic}
                  alt={producer.producer_name}
                  className="h-full w-full object-cover"
                />
              ) : (
                <UserRound
                  size={30}
                  className="text-white/20"
                />
              )}
            </div>
          </div>
        </section>

        {/* =================================================
            PRODUCER INFO
        ================================================= */}

        <section className="px-1 pt-12 min-[360px]:pt-14">
          <div className="flex min-w-0 items-center gap-1.5">
            <h1 className="min-w-0 truncate text-[25px] font-bold tracking-tight min-[360px]:text-[29px]">
              {producer.producer_name}
            </h1>

            {producer.is_verified && (
              <BadgeCheck
                size={19}
                className="shrink-0 text-[#1ed760]"
                fill="#1ed760"
                strokeWidth={1.5}
              />
            )}
          </div>

          {producer.bio && (
            <p className="mt-2 max-w-2xl text-[11px] leading-5 text-white/40 min-[360px]:text-xs">
              {producer.bio}
            </p>
          )}

          {/* SOCIALS */}

          {(producer.instagram ||
            producer.youtube) && (
            <div className="mt-4 flex items-center gap-2">
              {producer.instagram && (
                <a
                  href={producer.instagram}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex h-9 w-9 items-center justify-center rounded-full border border-white/[0.08] bg-white/[0.04] text-white/50 transition hover:text-white"
                >
                  <Instagram size={16} />
                </a>
              )}

              {producer.youtube && (
                <a
                  href={producer.youtube}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex h-9 w-9 items-center justify-center rounded-full border border-white/[0.08] bg-white/[0.04] text-white/50 transition hover:text-white"
                >
                  <Youtube size={17} />
                </a>
              )}
            </div>
          )}

          {/* STATS */}

          <div className="mt-5 grid grid-cols-3 gap-2">
            <Stat
              label="Sales"
              value={producer.total_sales}
            />

            <Stat
              label="Revenue"
              value={formatPrice(
                producer.total_revenue
              )}
            />

            <Stat
              label="Status"
              value={
                producer.is_active
                  ? "Active"
                  : "Offline"
              }
            />
          </div>
        </section>

        {/* =================================================
            BEATS
        ================================================= */}

        <section className="mt-8">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[9px] font-bold tracking-[0.16em] text-[#1ed760]">
                MARKETPLACE
              </p>

              <h2 className="mt-1 text-xl font-bold">
                Beats
              </h2>
            </div>

            <span className="text-[10px] text-white/25">
              {beats.length} beats
            </span>
          </div>

          <div className="mt-4">
            {beatsLoading ? (
              <BeatSkeleton />
            ) : beats.length === 0 ? (
              <div className="rounded-2xl border border-white/[0.07] bg-white/[0.02] py-14 text-center">
                <Music2
                  size={28}
                  className="mx-auto text-white/15"
                />

                <p className="mt-3 text-xs text-white/30">
                  No beats available yet.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-2.5 min-[360px]:gap-3 sm:grid-cols-3 lg:grid-cols-4">
                {beats.map((beat) => (
                  <BeatCard
                    key={beat.id}
                    beat={beat}
                    playingId={playingId}
                    isPlaying={isPlaying}
                    onPlay={handlePlayPreview}
                  />
                ))}
              </div>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}

/* =========================================================
   STAT
========================================================= */

function Stat({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="min-w-0 rounded-2xl border border-white/[0.07] bg-white/[0.035] p-3">
      <p className="text-[9px] text-white/30">
        {label}
      </p>

      <p className="mt-1 truncate text-[11px] font-bold min-[360px]:text-xs">
        {value}
      </p>
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
}: {
  beat: Beat;
  playingId: number | null;
  isPlaying: boolean;
  onPlay: (beat: Beat) => void;
}) {
  const playing =
    playingId === beat.id &&
    isPlaying;

  const hasPreview =
    Boolean(beat.preview_audio);

  return (
    <article className="group min-w-0 overflow-hidden rounded-2xl border border-white/[0.07] bg-[#0d0d0d] p-2.5 transition hover:bg-[#111] min-[360px]:p-3">
      {/* COVER */}

      <div className="relative aspect-square overflow-hidden rounded-xl bg-white/[0.05]">
        <Link
          href={`/beats/${beat.id}`}
          className="absolute inset-0"
        >
          {beat.cover ? (
            <img
              src={beat.cover}
              alt={beat.title}
              loading="lazy"
              className="h-full w-full object-cover transition duration-300 group-hover:scale-105"
            />
          ) : (
            <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-white/[0.07] to-white/[0.02]">
              <Music2
                size={27}
                className="text-white/15"
              />
            </div>
          )}
        </Link>

        {/* PREVIEW */}

        <button
          type="button"
          disabled={!hasPreview}
          aria-label={
            playing
              ? `Pause ${beat.title}`
              : `Play ${beat.title}`
          }
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();

            onPlay(beat);
          }}
          className={`absolute bottom-2 right-2 z-10 flex h-8 w-8 items-center justify-center rounded-full shadow-lg transition active:scale-90 min-[360px]:h-9 min-[360px]:w-9 ${
            hasPreview
              ? "bg-[#1ed760] text-black"
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

        {/* PREVIEW */}

        {/* {hasPreview && (
          <div className="absolute left-2 top-2 z-10 rounded-full border border-white/10 bg-black/60 px-2 py-1 backdrop-blur-md">
            <span className="text-[8px] font-medium text-white/70">
              PREVIEW
            </span>
          </div>
        )} */}
      </div>

      {/* INFO */}

      <Link href={`/beats/${beat.id}`}>
        <div className="mt-2.5 min-w-0">
          <h3 className="truncate text-[11px] font-bold min-[360px]:text-xs">
            {beat.title}
          </h3>

          <div className="mt-1 flex min-w-0 items-center justify-between gap-2">
            <span className="truncate text-[9px] text-white/30">
              {beat.genre}
            </span>

            <span className="shrink-0 text-[9px] font-bold text-[#1ed760]">
              {formatPrice(beat.price)}
            </span>
          </div>

          <div className="mt-2 flex items-center justify-between text-[8px] text-white/20">
            <span>
              {beat.bpm ?? "--"} BPM
            </span>

            <span className="flex items-center gap-0.5">
              Open
              <ChevronRight size={9} />
            </span>
          </div>
        </div>
      </Link>
    </article>
  );
}

/* =========================================================
   SKELETON
========================================================= */

function BeatSkeleton() {
  return (
    <div className="grid grid-cols-2 gap-2.5 min-[360px]:gap-3 sm:grid-cols-3 lg:grid-cols-4">
      {Array.from({ length: 6 }).map(
        (_, i) => (
          <div
            key={i}
            className="rounded-2xl border border-white/[0.05] bg-white/[0.025] p-2.5 min-[360px]:p-3"
          >
            <div className="aspect-square animate-pulse rounded-xl bg-white/[0.06]" />

            <div className="mt-3 h-3 w-3/4 animate-pulse rounded bg-white/[0.06]" />

            <div className="mt-2 h-2.5 w-1/2 animate-pulse rounded bg-white/[0.05]" />
          </div>
        )
      )}
    </div>
  );
}

/* =========================================================
   PAGE SKELETON
========================================================= */

function ProducerDetailSkeleton() {
  return (
    <main className="min-h-screen bg-[#050505] pb-28 text-white">
      <div className="px-3 pt-4 min-[360px]:px-4">
        <div className="h-9 w-24 animate-pulse rounded-full bg-white/[0.05]" />

        <div className="mt-4 h-[155px] animate-pulse rounded-3xl bg-white/[0.05] min-[360px]:h-[175px]" />

        <div className="mt-14">
          <div className="h-7 w-40 animate-pulse rounded bg-white/[0.06]" />

          <div className="mt-3 h-3 w-full animate-pulse rounded bg-white/[0.04]" />

          <div className="mt-2 h-3 w-2/3 animate-pulse rounded bg-white/[0.04]" />
        </div>

        <div className="mt-5 grid grid-cols-3 gap-2">
          <div className="h-16 animate-pulse rounded-2xl bg-white/[0.04]" />
          <div className="h-16 animate-pulse rounded-2xl bg-white/[0.04]" />
          <div className="h-16 animate-pulse rounded-2xl bg-white/[0.04]" />
        </div>
      </div>
    </main>
  );
}

/* =========================================================
   HELPERS
========================================================= */

function formatPrice(
  value: number | string
) {
  return Number(
    value || 0
  ).toLocaleString("en-US");
}