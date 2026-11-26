"use client";

import Link from "next/link";
import {
  Download,
  Music2,
  ArrowLeft,
  ShoppingBag,
} from "lucide-react";

import {
  useGetMyBeatPurchasesQuery,
  useLazyDownloadBeatQuery,
} from "@/redux/services/producerApiSlice";

export default function PurchasesPage() {
  const {
    data: purchases = [],
    isLoading,
  } = useGetMyBeatPurchasesQuery();

  const [
    downloadBeat,
    { isFetching },
  ] = useLazyDownloadBeatQuery();

  async function handleDownload(
    purchaseId: string
  ) {
    try {
      const result =
        await downloadBeat(
          purchaseId
        ).unwrap();

      if (result.audio_file) {
        window.open(
          result.audio_file,
          "_blank"
        );
      }
    } catch {
      alert(
        "Could not get download link."
      );
    }
  }

  return (
    <main className="min-h-screen overflow-x-hidden bg-[#050505] pb-28 text-white">
      <div className="px-3 pt-6 min-[360px]:px-4">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-[9px] font-bold tracking-[0.16em] text-[#1ed760]">
              LIBRARY
            </p>

            <h1 className="mt-1 text-[27px] font-bold min-[360px]:text-[32px]">
              My purchases
            </h1>
          </div>

          <Link
            href="/beats"
            className="flex h-9 shrink-0 items-center gap-1 rounded-full bg-white/[0.06] px-3 text-[10px] text-white/60 min-[360px]:h-10 min-[360px]:text-xs"
          >
            Marketplace
            <ArrowLeft size={12} />
          </Link>
        </div>

        {isLoading ? (
          <PurchaseSkeleton />
        ) : purchases.length === 0 ? (
          <div className="mt-8 rounded-3xl border border-white/[0.07] bg-white/[0.025] px-5 py-16 text-center">
            <ShoppingBag
              size={30}
              className="mx-auto text-white/15"
            />

            <h2 className="mt-4 text-sm font-bold">
              No purchases yet
            </h2>

            <p className="mt-2 text-[10px] leading-5 text-white/30">
              Find a beat and start building
              your next track.
            </p>

            <Link
              href="/beats"
              className="mt-5 inline-flex h-10 items-center rounded-full bg-[#1ed760] px-5 text-xs font-bold text-black"
            >
              Explore beats
            </Link>
          </div>
        ) : (
          <div className="mt-6 space-y-2.5">
            {purchases.map(
              (purchase) => (
                <article
                  key={purchase.id}
                  className="flex min-w-0 gap-3 rounded-2xl border border-white/[0.07] bg-[#0d0d0d] p-2.5 min-[360px]:p-3"
                >
                  <Link
                    href={`/beats/${purchase.beat.id}`}
                    className="h-16 w-16 shrink-0 overflow-hidden rounded-xl bg-white/[0.05] min-[360px]:h-[70px] min-[360px]:w-[70px]"
                  >
                    {purchase.beat.cover ? (
                      <img
                        src={purchase.beat.cover}
                        alt={purchase.beat.title}
                        className="h-full w-full object-cover"
                      />
                    ) : (
                      <div className="flex h-full items-center justify-center">
                        <Music2
                          size={20}
                          className="text-white/15"
                        />
                      </div>
                    )}
                  </Link>

                  <div className="min-w-0 flex-1">
                    <Link
                      href={`/beats/${purchase.beat.id}`}
                      className="block truncate text-xs font-bold min-[360px]:text-sm"
                    >
                      {purchase.beat.title}
                    </Link>

                    <p className="mt-1 truncate text-[9px] text-white/30 min-[360px]:text-[10px]">
                      {purchase.beat.producer.producer_name}
                    </p>

                    <div className="mt-2 flex items-center justify-between gap-2">
                      <span className="truncate text-[9px] text-white/30">
                        {Number(
                          purchase.price
                        ).toLocaleString()}{" "}
                        تومان
                      </span>

                      <button
                        type="button"
                        onClick={() =>
                          handleDownload(
                            purchase.id
                          )
                        }
                        disabled={isFetching}
                        className="flex h-8 shrink-0 items-center gap-1.5 rounded-full bg-[#1ed760] px-3 text-[9px] font-bold text-black disabled:opacity-40 min-[360px]:text-[10px]"
                      >
                        <Download size={12} />

                        {isFetching
                          ? "..."
                          : "Download"}
                      </button>
                    </div>
                  </div>
                </article>
              )
            )}
          </div>
        )}
      </div>
    </main>
  );
}

function PurchaseSkeleton() {
  return (
    <div className="mt-6 space-y-2.5">
      {Array.from({ length: 5 }).map(
        (_, i) => (
          <div
            key={i}
            className="flex gap-3 rounded-2xl bg-white/[0.04] p-3"
          >
            <div className="h-[70px] w-[70px] shrink-0 animate-pulse rounded-xl bg-white/[0.06]" />

            <div className="flex-1 space-y-3 pt-1">
              <div className="h-3 w-2/3 animate-pulse rounded bg-white/[0.06]" />
              <div className="h-2.5 w-1/3 animate-pulse rounded bg-white/[0.06]" />
              <div className="h-2.5 w-1/2 animate-pulse rounded bg-white/[0.06]" />
            </div>
          </div>
        )
      )}
    </div>
  );
}