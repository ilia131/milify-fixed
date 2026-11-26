"use client";

import { useState } from "react";
import Link from "next/link";

import {
  Search,
  ChevronRight,
  UserRound,
  BadgeCheck,
} from "lucide-react";
import { useRouter } from "next/navigation";
import {
  useGetProducersQuery,
  type ProducerProfile,
} from "@/redux/services/producerApiSlice";

export default function ProducersPage() {
  const [search, setSearch] = useState("");

  const {
    data: producers = [],
    isLoading,
    isFetching,
    isError,
  } = useGetProducersQuery({
    search: search.trim() || undefined,
    ordering: "-total_sales",
  });
  const router = useRouter();
  return (
    <main className="min-h-screen overflow-x-hidden bg-[#050505] pb-28 text-white">
      <div className="px-3 pt-6 min-[360px]:px-4 min-[360px]:pt-7">
        {/* =================================================
            HEADER
        ================================================= */}
<button
  type="button"
  onClick={() => router.push("/browse/albums")}
  className="
    mb-5
    flex
    h-9
    w-9
    items-center
    justify-center
    rounded-full
    border
    border-white/10
    bg-white/[0.05]
    text-white/70
    transition
    hover:bg-white/10
    hover:text-white
    active:scale-95
  "
  aria-label="Go back"
>
  <ChevronRight
    size={18}
    className="rotate-180"
  />
</button>
        <div className="flex items-end justify-between gap-3">
          
          <div className="min-w-0">
            <p className="text-[9px] font-bold tracking-[0.16em] text-[#1ed760]">
              MILIFY
            </p>

            <h1 className="mt-1 text-[28px] font-bold tracking-tight min-[360px]:text-[32px]">
              Producers
            </h1>

            <p className="mt-2 text-[11px] text-white/35 min-[360px]:text-xs">
              Discover independent beatmakers.
            </p>
          </div>

          <Link
            href="/sell"
            className="flex h-9 shrink-0 items-center gap-1.5 rounded-full bg-[#1ed760] px-3 text-[10px] font-bold text-black transition active:scale-95 min-[360px]:h-10 min-[360px]:px-4 min-[360px]:text-xs"
          >
            Sell
          </Link>
        </div>

        {/* =================================================
            SEARCH
        ================================================= */}

        <div className="relative mt-5">
          <Search
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30"
          />

          <input
            value={search}
            onChange={(e) =>
              setSearch(e.target.value)
            }
            placeholder="Search producers..."
            className="h-11 w-full rounded-xl border border-white/[0.08] bg-white/[0.04] pl-9 pr-3 text-xs outline-none placeholder:text-white/25 focus:border-[#1ed760]/40 min-[360px]:text-sm"
          />
        </div>

        {/* =================================================
            FETCHING
        ================================================= */}

        {isFetching && !isLoading && (
          <div className="mt-3 h-1 overflow-hidden rounded-full bg-white/[0.05]">
            <div className="h-full w-1/3 animate-pulse rounded-full bg-[#1ed760]" />
          </div>
        )}

        {/* =================================================
            GRID
        ================================================= */}

        <section className="mt-7">
          {isLoading ? (
            <ProducerSkeleton />
          ) : isError ? (
            <ProducerError />
          ) : producers.length === 0 ? (
            <EmptyProducers />
          ) : (
            <div className="grid grid-cols-2 gap-2.5 min-[360px]:gap-3">
              {producers.map((producer) => (
                <ProducerCard
                  key={producer.uuid}
                  producer={producer}
                />
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}

/* =========================================================
   PRODUCER CARD
========================================================= */

function ProducerCard({
  producer,
}: {
  producer: ProducerProfile;
}) {
  return (
    <Link
      href={`/producers/${producer.uuid}`}
      className="group min-w-0 overflow-hidden rounded-2xl border border-white/[0.07] bg-[#0d0d0d] p-3 transition active:scale-[0.98] min-[360px]:p-4"
    >
      {/* PROFILE IMAGE */}

      <div className="relative mx-auto aspect-square w-full max-w-[150px] overflow-hidden rounded-full bg-white/[0.05]">
        {producer.profile_pic ? (
          <img
            src={producer.profile_pic}
            alt={producer.producer_name}
            loading="lazy"
            className="h-full w-full object-cover transition duration-500 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full items-center justify-center">
            <UserRound
              size={35}
              className="text-white/15"
            />
          </div>
        )}

        {/* VERIFIED */}

        {producer.is_verified && (
          <div className="absolute bottom-1 right-1 flex h-6 w-6 items-center justify-center rounded-full border border-black/50 bg-[#1ed760] text-black">
            <BadgeCheck
              size={14}
              fill="currentColor"
            />
          </div>
        )}
      </div>

      {/* INFO */}

      <div className="mt-3 text-center">
        <div className="flex min-w-0 items-center justify-center gap-1">
          <h2 className="min-w-0 truncate text-xs font-bold min-[360px]:text-sm">
            {producer.producer_name}
          </h2>

          {producer.is_verified && (
            <BadgeCheck
              size={13}
              className="shrink-0 text-[#1ed760]"
            />
          )}
        </div>

        <p className="mt-1 text-[9px] text-white/30 min-[360px]:text-[10px]">
          {Number(
            producer.total_sales
          ).toLocaleString()}{" "}
          sales
        </p>

        {Number(producer.total_revenue) > 0 && (
          <p className="mt-1 text-[8px] text-[#1ed760]/60 min-[360px]:text-[9px]">
            {Number(
              producer.total_revenue
            ).toLocaleString()}{" "}
            تومان revenue
          </p>
        )}

        <div className="mt-3 flex items-center justify-center gap-1 text-[9px] text-white/30 transition group-hover:text-white/60 min-[360px]:text-[10px]">
          View profile

          <ChevronRight
            size={12}
            className="transition-transform group-hover:translate-x-0.5"
          />
        </div>
      </div>
    </Link>
  );
}

/* =========================================================
   EMPTY
========================================================= */

function EmptyProducers() {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.02] px-4 py-16 text-center">
      <UserRound
        size={28}
        className="mx-auto text-white/15"
      />

      <p className="mt-3 text-xs text-white/35">
        No producers found.
      </p>

      <p className="mt-1 text-[10px] text-white/20">
        Try another search.
      </p>
    </div>
  );
}

/* =========================================================
   ERROR
========================================================= */

function ProducerError() {
  return (
    <div className="rounded-2xl border border-red-500/10 bg-red-500/[0.04] px-4 py-16 text-center">
      <UserRound
        size={28}
        className="mx-auto text-red-300/30"
      />

      <p className="mt-3 text-xs text-red-300/70">
        Failed to load producers.
      </p>

      <p className="mt-1 text-[10px] text-white/25">
        Please try again.
      </p>
    </div>
  );
}

/* =========================================================
   SKELETON
========================================================= */

function ProducerSkeleton() {
  return (
    <div className="grid grid-cols-2 gap-2.5 min-[360px]:gap-3">
      {Array.from({ length: 6 }).map(
        (_, i) => (
          <div
            key={i}
            className="rounded-2xl bg-white/[0.04] p-3 min-[360px]:p-4"
          >
            <div className="mx-auto aspect-square max-w-[150px] animate-pulse rounded-full bg-white/[0.06]" />

            <div className="mx-auto mt-4 h-3 w-2/3 animate-pulse rounded bg-white/[0.06]" />

            <div className="mx-auto mt-2 h-2.5 w-1/3 animate-pulse rounded bg-white/[0.06]" />

            <div className="mx-auto mt-4 h-2.5 w-1/2 animate-pulse rounded bg-white/[0.06]" />
          </div>
        )
      )}
    </div>
  );
}