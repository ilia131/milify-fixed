"use client";

import {
  X,
  Play,
  GripVertical,
  Trash2,
  ListMusic,
  MoreHorizontal,
} from "lucide-react";

import Image from "next/image";

import {
  useAppDispatch,
  useAppSelector,
} from "@/redux/hook";

import {
  setQueue,
} from "@/redux/features/playerSlice";

type QueueSheetProps = {
  onClose: () => void;
};

const QueueSheet = ({
  onClose,
}: QueueSheetProps) => {
  const dispatch = useAppDispatch();

  const {
    queue,
    currentIndex,
    isPlaying,
  } = useAppSelector(
    (state) => state.player
  );

  const currentSong =
    queue[currentIndex];

  /* =========================
     Play Song
  ========================= */

  const handlePlaySong = (
    index: number
  ) => {
    const song = queue[index];

    if (!song) return;

    dispatch(
      setQueue({
        songs: queue,
        startIndex: index,
      })
    );
  };

  /* =========================
     Remove Song
  ========================= */

  const handleRemoveSong = (
    index: number
  ) => {
    const newQueue = queue.filter(
      (_, i) => i !== index
    );

    if (!newQueue.length) {
      onClose();
      return;
    }

    let newIndex = currentIndex;

    if (index < currentIndex) {
      newIndex = currentIndex - 1;
    }

    if (
      index === currentIndex &&
      newIndex >= newQueue.length
    ) {
      newIndex = newQueue.length - 1;
    }

    dispatch(
      setQueue({
        songs: newQueue,
        startIndex: newIndex,
      })
    );
  };

  /* =========================
     Empty Queue
  ========================= */

  if (!queue.length) {
    return (
      <div
        className="
          fixed
          inset-0
          z-[999]
          flex
          items-end
          justify-center
          bg-black/70
          backdrop-blur-md
          animate-in
          fade-in
          duration-200
        "
        onClick={onClose}
      >
        <div
          onClick={(e) =>
            e.stopPropagation()
          }
          className="
            relative
            w-full
            max-w-2xl
            overflow-hidden
            rounded-t-[32px]
            border
            border-white/10
            bg-[#0d0d0d]/95
            px-6
            pb-10
            pt-4
            text-white
            shadow-[0_-20px_80px_rgba(0,0,0,0.6)]
            backdrop-blur-2xl
            animate-in
            slide-in-from-bottom
            duration-300
          "
        >
          {/* Top glow */}

          <div
            className="
              pointer-events-none
              absolute
              left-1/2
              top-[-100px]
              h-[220px]
              w-[220px]
              -translate-x-1/2
              rounded-full
              bg-green-500/10
              blur-[100px]
            "
          />

          {/* Handle */}

          <div
            className="
              relative
              mx-auto
              mb-6
              h-1
              w-12
              rounded-full
              bg-white/20
            "
          />

          {/* Header */}

          <div className="relative flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div
                className="
                  flex
                  h-11
                  w-11
                  items-center
                  justify-center
                  rounded-2xl
                  bg-white/10
                  text-green-400
                "
              >
                <ListMusic size={22} />
              </div>

              <div>
                <h2 className="text-lg font-bold">
                  Queue
                </h2>

                <p className="text-xs text-zinc-500">
                  Nothing playing next
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={onClose}
              className="
                flex
                h-10
                w-10
                items-center
                justify-center
                rounded-full
                bg-white/5
                text-zinc-400
                transition
                hover:bg-white/10
                hover:text-white
                active:scale-90
              "
            >
              <X size={19} />
            </button>
          </div>

          {/* Empty */}

          <div
            className="
              flex
              min-h-[260px]
              flex-col
              items-center
              justify-center
              text-center
            "
          >
            <div
              className="
                mb-5
                flex
                h-20
                w-20
                items-center
                justify-center
                rounded-full
                border
                border-white/10
                bg-white/5
                text-zinc-600
              "
            >
              <ListMusic size={34} />
            </div>

            <h3 className="text-base font-semibold">
              Your queue is empty
            </h3>

            <p className="mt-2 max-w-xs text-sm text-zinc-500">
              Add songs to your queue and
              they'll appear here.
            </p>
          </div>
        </div>
      </div>
    );
  }

  /* =========================
     Queue
  ========================= */

  return (
    <div
      className="
        fixed
        inset-0
        z-[999]
        flex
        items-end
        justify-center
        bg-black/70
        backdrop-blur-md
        animate-in
        fade-in
        duration-200
      "
      onClick={onClose}
    >
      <div
        onClick={(e) =>
          e.stopPropagation()
        }
        className="
          relative
          max-h-[88vh]
          w-full
          max-w-2xl
          overflow-hidden
          rounded-t-[32px]
          border
          border-white/10
          bg-[#0d0d0d]/95
          text-white
          shadow-[0_-20px_100px_rgba(0,0,0,0.7)]
          backdrop-blur-2xl
          animate-in
          slide-in-from-bottom
          duration-300
        "
      >
        {/* =================
            Background Glow
        ================= */}

        <div
          className="
            pointer-events-none
            absolute
            left-1/2
            top-[-180px]
            h-[350px]
            w-[350px]
            -translate-x-1/2
            rounded-full
            bg-green-500/10
            blur-[120px]
          "
        />

        {/* =================
            Header
        ================= */}

        <div className="relative px-5 pb-4 pt-4">
          {/* Handle */}

          <div
            className="
              mx-auto
              mb-6
              h-1
              w-12
              rounded-full
              bg-white/20
            "
          />

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div
                className="
                  flex
                  h-11
                  w-11
                  items-center
                  justify-center
                  rounded-2xl
                  border
                  border-white/10
                  bg-white/5
                  text-green-400
                "
              >
                <ListMusic size={22} />
              </div>

              <div>
                <h2 className="text-xl font-bold">
                  Queue
                </h2>

                <p className="mt-0.5 text-xs text-zinc-500">
                  {queue.length}{" "}
                  {queue.length === 1
                    ? "song"
                    : "songs"}{" "}
                  in queue
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={onClose}
              aria-label="Close queue"
              className="
                flex
                h-10
                w-10
                items-center
                justify-center
                rounded-full
                bg-white/5
                text-zinc-400
                transition
                hover:bg-white/10
                hover:text-white
                active:scale-90
              "
            >
              <X size={19} />
            </button>
          </div>
        </div>

        {/* =================
            Current Song
        ================= */}

        {currentSong && (
          <div className="relative px-5 pb-4">
            <div
              className="
                relative
                overflow-hidden
                rounded-2xl
                border
                border-green-400/10
                bg-gradient-to-r
                from-green-500/10
                via-white/[0.04]
                to-transparent
                p-3
              "
            >
              <div className="flex items-center gap-3">
                {/* Cover */}

                <div
                  className="
                    relative
                    h-14
                    w-14
                    shrink-0
                    overflow-hidden
                    rounded-xl
                    shadow-lg
                  "
                >
                  <Image
                    src={
                      currentSong.image_url
                    }
                    alt={
                      currentSong.title
                    }
                    fill
                    sizes="56px"
                    className="object-cover"
                  />

                  <div
                    className="
                      absolute
                      inset-0
                      flex
                      items-center
                      justify-center
                      bg-black/35
                    "
                  >
                    <div className="flex items-end gap-[3px]">
                      <span className="h-2 w-[3px] animate-pulse rounded-full bg-green-400" />

                      <span className="h-4 w-[3px] animate-pulse rounded-full bg-green-400 [animation-delay:150ms]" />

                      <span className="h-3 w-[3px] animate-pulse rounded-full bg-green-400 [animation-delay:300ms]" />
                    </div>
                  </div>
                </div>

                {/* Info */}

                <div className="min-w-0 flex-1">
                  <p className="mb-1 text-[10px] font-semibold uppercase tracking-wider text-green-400">
                    Now Playing
                  </p>

                  <p className="truncate text-sm font-bold text-white">
                    {currentSong.title}
                  </p>

                  <p className="truncate text-xs text-zinc-500">
                    {currentSong.artistname ||
                      "Unknown Artist"}
                  </p>
                </div>

                <div
                  className="
                    shrink-0
                    rounded-full
                    bg-green-400/10
                    px-3
                    py-1
                    text-[10px]
                    font-bold
                    text-green-400
                  "
                >
                  PLAYING
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Divider */}

        <div className="mx-5 h-px bg-white/[0.06]" />

        {/* =================
            Queue List
        ================= */}

        <div
          className="
            relative
            max-h-[55vh]
            overflow-y-auto
            px-3
            pb-8
            pt-3
            scrollbar-thin
            scrollbar-track-transparent
            scrollbar-thumb-white/10
          "
        >
          {queue.map((song, index) => {
            const isCurrent =
              index === currentIndex;

            return (
              <div
                key={`${song.unique_id}-${index}`}
                className={`
                  group
                  relative
                  flex
                  items-center
                  gap-2
                  rounded-2xl
                  px-2
                  py-2
                  transition-all
                  duration-200
                  ${
                    isCurrent
                      ? "bg-white/[0.07]"
                      : "hover:bg-white/[0.04]"
                  }
                `}
              >
                {/* Drag */}

                <div
                  className="
                    flex
                    w-6
                    shrink-0
                    items-center
                    justify-center
                    text-zinc-700
                    transition
                    group-hover:text-zinc-400
                  "
                >
                  <GripVertical
                    size={17}
                  />
                </div>

                {/* Cover */}

                <button
                  type="button"
                  onClick={() =>
                    handlePlaySong(index)
                  }
                  className="
                    relative
                    h-12
                    w-12
                    shrink-0
                    overflow-hidden
                    rounded-xl
                  "
                >
                  <Image
                    src={song.image_url}
                    alt={song.title}
                    fill
                    sizes="48px"
                    className="
                      object-cover
                      transition
                      duration-300
                      group-hover:scale-110
                    "
                  />

                  <div
                    className={`
                      absolute
                      inset-0
                      flex
                      items-center
                      justify-center
                      bg-black/40
                      transition
                      ${
                        isCurrent
                          ? "opacity-100"
                          : "opacity-0 group-hover:opacity-100"
                      }
                    `}
                  >
                    <Play
                      size={17}
                      fill="white"
                      className="text-white"
                    />
                  </div>
                </button>

                {/* Number */}

                <div className="hidden w-5 text-center text-xs text-zinc-600 sm:block">
                  {String(index + 1).padStart(
                    2,
                    "0"
                  )}
                </div>

                {/* Info */}

                <button
                  type="button"
                  onClick={() =>
                    handlePlaySong(index)
                  }
                  className="min-w-0 flex-1 text-left"
                >
                  <p
                    className={`
                      truncate
                      text-sm
                      font-semibold
                      transition
                      ${
                        isCurrent
                          ? "text-green-400"
                          : "text-zinc-200 group-hover:text-white"
                      }
                    `}
                  >
                    {song.title}
                  </p>

                  <p className="mt-1 truncate text-xs text-zinc-500">
                    {song.artistname ||
                      "Unknown Artist"}
                  </p>
                </button>

                {/* Current */}

                {isCurrent && (
                  <div className="mr-2 flex items-end gap-[3px]">
                    <span className="h-2 w-[3px] animate-pulse rounded-full bg-green-400" />

                    <span className="h-4 w-[3px] animate-pulse rounded-full bg-green-400 [animation-delay:150ms]" />

                    <span className="h-3 w-[3px] animate-pulse rounded-full bg-green-400 [animation-delay:300ms]" />
                  </div>
                )}

                {/* More */}

                <button
                  type="button"
                  aria-label={`Options for ${song.title}`}
                  className="
                    flex
                    h-9
                    w-9
                    shrink-0
                    items-center
                    justify-center
                    rounded-full
                    text-zinc-600
                    opacity-0
                    transition
                    hover:bg-white/10
                    hover:text-white
                    group-hover:opacity-100
                  "
                  onClick={(e) =>
                    e.stopPropagation()
                  }
                >
                  <MoreHorizontal
                    size={19}
                  />
                </button>

                {/* Delete */}

                <button
                  type="button"
                  aria-label={`Remove ${song.title} from queue`}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRemoveSong(index);
                  }}
                  className="
                    flex
                    h-9
                    w-9
                    shrink-0
                    items-center
                    justify-center
                    rounded-full
                    text-zinc-600
                    transition
                    hover:bg-red-500/10
                    hover:text-red-400
                  "
                >
                  <Trash2 size={17} />
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default QueueSheet;