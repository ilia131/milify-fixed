"use client";

export default function BeatCardSkeleton() {
  return (
    <div
      className="
        relative
        w-full
        overflow-hidden
        rounded-2xl
        border border-white/10
        bg-white/[0.035]
        backdrop-blur-xl
        animate-pulse
      "
    >
      {/* Main */}
      <div className="flex gap-4 p-3.5">
        {/* Cover */}
        <div
          className="
            relative
            w-24
            h-24
            shrink-0
            overflow-hidden
            rounded-xl
            bg-white/[0.08]
          "
        />

        {/* Info */}
        <div className="flex-1 min-w-0 flex flex-col justify-between py-0.5">
          <div>
            {/* Title */}
            <div className="h-4 w-32 bg-white/[0.08] rounded-md" />

            {/* Producer */}
            <div className="mt-2 h-3 w-24 bg-white/[0.06] rounded-md" />
          </div>

          {/* Meta */}
          <div className="flex items-center gap-2 mt-2">
            {/* Genre */}
            <div className="h-5 w-12 bg-white/[0.07] rounded-md" />

            {/* BPM */}
            <div className="h-3 w-14 bg-white/[0.05] rounded-md" />

            {/* Plays */}
            <div className="h-3 w-10 bg-white/[0.05] rounded-md" />
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
        {/* Price */}
        <div>
          <div className="h-2.5 w-20 bg-white/[0.05] rounded mb-2" />
          <div className="h-4 w-28 bg-white/[0.08] rounded-md" />
        </div>

        {/* Buy button */}
        <div
          className="
            w-20
            h-9
            rounded-full
            bg-white/[0.08]
          "
        />
      </div>
    </div>
  );
}