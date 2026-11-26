"use client";

import {
  ArrowLeft,
  Check,
  Download,
  Loader2,
  Music2,
  ShoppingCart,
} from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  useBuyBeatMutation,
  useGetBeatDetailQuery,
  useGetMyBeatPurchasesQuery,
  useLazyDownloadBeatQuery,
} from "@/redux/services/producerApiSlice";

export default function BeatDetailPage() {
  const params = useParams();

  const id = Number(params.id);

  /* =========================================================
     API
  ========================================================= */

  const {
    data: beat,
    isLoading,
    isError,
  } = useGetBeatDetailQuery(id, {
    skip: !id,
  });

  const {
    data: purchases = [],
    isLoading: purchasesLoading,
  } = useGetMyBeatPurchasesQuery();

  const [buyBeat, { isLoading: buying }] =
    useBuyBeatMutation();

  const [
    downloadBeat,
    { isFetching: downloading },
  ] = useLazyDownloadBeatQuery();

  /* =========================================================
     STATE
  ========================================================= */

  const [selectedLicense, setSelectedLicense] =
    useState<number | null>(null);

  const [message, setMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  /* =========================================================
     LICENSES
  ========================================================= */

  const licenses = useMemo(() => {
    if (!beat?.licenses) {
      return [];
    }

    return beat.licenses.filter(
      (license) => license.is_active
    );
  }, [beat]);

  /* =========================================================
     EXISTING PURCHASE
  ========================================================= */

  const existingPurchase = useMemo(() => {
    if (!beat || !purchases.length) {
      return null;
    }

    return (
      purchases.find(
        (purchase) =>
          purchase.beat?.id === beat.id &&
          purchase.status === "COMPLETED"
      ) ?? null
    );
  }, [beat, purchases]);

  /* =========================================================
     DEFAULT LICENSE
  ========================================================= */

  useEffect(() => {
    if (
      licenses.length > 0 &&
      selectedLicense === null
    ) {
      setSelectedLicense(licenses[0].id);
    }
  }, [licenses, selectedLicense]);

  /* =========================================================
     BUY
  ========================================================= */

  async function handleBuy() {
    if (!beat) {
      return;
    }

    if (!selectedLicense) {
      setMessage({
        type: "error",
        text: "Please select a license first.",
      });

      return;
    }

    setMessage(null);

    try {
      const response = await buyBeat({
        beat_id: beat.id,
        license_id: selectedLicense,
      }).unwrap();

      setMessage({
        type: "success",
        text:
          response.message ||
          "Beat purchased successfully.",
      });
    } catch (error: any) {
      setMessage({
        type: "error",
        text:
          error?.data?.detail ||
          error?.data?.message ||
          "Purchase failed.",
      });
    }
  }

  /* =========================================================
     DOWNLOAD
  ========================================================= */

  async function handleDownload() {
    if (!existingPurchase?.id) {
      setMessage({
        type: "error",
        text: "Purchase information was not found.",
      });

      return;
    }

    setMessage(null);

    try {
      const response = await downloadBeat(
        existingPurchase.id
      ).unwrap();

      if (!response?.audio_file) {
        setMessage({
          type: "error",
          text: "Download file was not found.",
        });

        return;
      }

      window.open(
        response.audio_file,
        "_blank",
        "noopener,noreferrer"
      );
    } catch (error: any) {
      setMessage({
        type: "error",
        text:
          error?.data?.detail ||
          error?.data?.message ||
          "Download failed.",
      });
    }
  }

  /* =========================================================
     LOADING
  ========================================================= */

  if (isLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-black text-white">
        <div className="flex items-center gap-3 text-sm text-white/60">
          <Loader2
            size={20}
            className="animate-spin"
          />

          Loading beat...
        </div>
      </main>
    );
  }

  /* =========================================================
     ERROR
  ========================================================= */

  if (isError || !beat) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-black px-5 text-white">
        <div className="text-center">
          <Music2
            size={42}
            className="mx-auto mb-4 text-white/30"
          />

          <h1 className="text-lg font-bold">
            Beat not found
          </h1>

          <p className="mt-2 text-sm text-white/50">
            This beat may have been removed or is
            unavailable.
          </p>

          <Link
            href="/producers"
            className="mt-6 inline-flex h-11 items-center justify-center rounded-full bg-white px-6 text-sm font-semibold text-black"
          >
            Back to beats
          </Link>
        </div>
      </main>
    );
  }

  /* =========================================================
     RENDER
  ========================================================= */

  return (
    <main className="min-h-screen bg-black text-white">
      {/* =====================================================
          PAGE CONTAINER
      ===================================================== */}

      <div
        className="
          mx-auto
          w-full
          max-w-3xl
          px-3
          pt-4
          min-[360px]:px-4
          min-[400px]:px-5
          sm:px-6
          lg:px-8
        "
      >
        {/* ===================================================
            BACK
        =================================================== */}

        <Link
          href="/browse/albums"
          className="
            inline-flex
            items-center
            gap-2
            text-sm
            text-white/60
            transition
            hover:text-white
          "
        >
          <ArrowLeft size={17} />

          Back to beats
        </Link>

        {/* ===================================================
            MAIN CONTENT

            IMPORTANT:
            ALWAYS SINGLE COLUMN
            NO GRID
            NO FLEX ROW
            NO BREAKPOINT
        =================================================== */}

        <div className="mt-5 flex w-full flex-col gap-8">
          {/* =================================================
              COVER + PREVIEW
          ================================================= */}

          <section className="w-full min-w-0">
            {/* COVER */}

            <div
              className="
                aspect-square
                w-full
                overflow-hidden
                rounded-2xl
                bg-white/5
              "
            >
              {beat.cover ? (
                <Image
                  alt={beat.title}
                  width={1000}
                  height={1000}
                  src={beat.cover}
                  className="h-full w-full object-cover"
                  priority
                />
              ) : (
                <div className="flex h-full w-full items-center justify-center">
                  <Music2
                    size={80}
                    className="text-white/20"
                  />
                </div>
              )}
            </div>

            {/* PREVIEW */}

            <div
              className="
                mt-4
                rounded-2xl
                border
                border-white/10
                bg-white/[0.03]
                p-4
              "
            >
              <div className="mb-3 flex items-center gap-2">
                <Music2 size={17} />

                <span className="text-sm font-semibold">
                  Beat preview
                </span>
              </div>

              {beat.preview_audio ? (
                <audio
                  controls
                  preload="metadata"
                  src={beat.preview_audio}
                  className="w-full"
                />
              ) : (
                <p className="text-sm text-white/40">
                  Preview unavailable.
                </p>
              )}
            </div>
          </section>

          {/* =================================================
              BEAT INFORMATION
          ================================================= */}

          <section className="w-full min-w-0">
            {/* =================================================
                PRODUCER
            ================================================= */}

            <div className="flex min-w-0 items-center gap-3">
              {beat.producer?.profile_pic ? (
                <Image
                  src={beat.producer.profile_pic}
                  alt={
                    beat.producer.producer_name
                  }
                  width={44}
                  height={44}
                  className="
                    h-11
                    w-11
                    shrink-0
                    rounded-full
                    object-cover
                  "
                />
              ) : (
                <div
                  className="
                    flex
                    h-11
                    w-11
                    shrink-0
                    items-center
                    justify-center
                    rounded-full
                    bg-white/10
                  "
                >
                  <Music2 size={19} />
                </div>
              )}

              <div className="min-w-0">
                <p className="truncate text-xs text-white/50">
                  Produced by
                </p>

                <Link
                  href={`/producers/${beat.producer.uuid}`}
                  className="
                    block
                    truncate
                    text-sm
                    font-semibold
                    hover:underline
                  "
                >
                  {beat.producer.producer_name}
                </Link>
              </div>

              {beat.producer.is_verified && (
                <div
                  className="
                    flex
                    h-5
                    w-5
                    shrink-0
                    items-center
                    justify-center
                    rounded-full
                    bg-[#1ed760]
                    text-black
                  "
                >
                  <Check
                    size={12}
                    strokeWidth={3}
                  />
                </div>
              )}
            </div>

            {/* =================================================
                TITLE
            ================================================= */}

            <div className="mt-5 min-w-0">
              <h1
                className="
                  break-words
                  text-2xl
                  font-black
                  leading-tight
                  sm:text-3xl
                "
              >
                {beat.title}
              </h1>

              <div
                className="
                  mt-3
                  flex
                  flex-wrap
                  items-center
                  gap-2
                  text-xs
                  text-white/50
                "
              >
                <span className="rounded-full bg-white/10 px-3 py-1">
                  {beat.genre}
                </span>

                {beat.bpm && (
                  <span className="rounded-full bg-white/10 px-3 py-1">
                    {beat.bpm} BPM
                  </span>
                )}

                {beat.key && (
                  <span className="rounded-full bg-white/10 px-3 py-1">
                    {beat.key}
                  </span>
                )}

                <span className="rounded-full bg-white/10 px-3 py-1">
                  {beat.plays} plays
                </span>
              </div>
            </div>

            {/* =================================================
                DESCRIPTION
            ================================================= */}

            {beat.description && (
              <div className="mt-6">
                <h2 className="text-sm font-bold">
                  About this beat
                </h2>

                <p
                  className="
                    mt-2
                    whitespace-pre-wrap
                    break-words
                    text-sm
                    leading-6
                    text-white/55
                  "
                >
                  {beat.description}
                </p>
              </div>
            )}

            {/* =================================================
                LICENSES
            ================================================= */}

            <div className="mt-7">
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-sm font-bold">
                  Select a license
                </h2>

                {licenses.length > 0 && (
                  <span className="text-xs text-white/40">
                    {licenses.length} available
                  </span>
                )}
              </div>

              {licenses.length === 0 ? (
                <div
                  className="
                    mt-3
                    rounded-2xl
                    border
                    border-white/10
                    bg-white/[0.03]
                    p-4
                  "
                >
                  <p className="text-sm text-white/50">
                    No licenses are currently
                    available.
                  </p>
                </div>
              ) : (
                <div className="mt-3 flex w-full flex-col gap-2">
                  {licenses.map((license) => {
                    const isSelected =
                      selectedLicense ===
                      license.id;

                    return (
                      <button
                        key={license.id}
                        type="button"
                        onClick={() =>
                          setSelectedLicense(
                            license.id
                          )
                        }
                        className={[
                          "relative w-full min-w-0 rounded-2xl border p-4 text-left transition",
                          isSelected
                            ? "border-[#1ed760] bg-[#1ed760]/10"
                            : "border-white/10 bg-white/[0.03] hover:border-white/20",
                        ].join(" ")}
                      >
                        {isSelected && (
                          <div
                            className="
                              absolute
                              right-3
                              top-3
                              flex
                              h-5
                              w-5
                              items-center
                              justify-center
                              rounded-full
                              bg-[#1ed760]
                              text-black
                            "
                          >
                            <Check
                              size={12}
                              strokeWidth={3}
                            />
                          </div>
                        )}

                        <div className="pr-7">
                          <p className="truncate text-sm font-bold">
                            {license.name}
                          </p>

                          <p className="mt-1 text-xs uppercase text-white/40">
                            {
                              license.license_type
                            }
                          </p>
                        </div>

                        <p className="mt-4 text-lg font-black">
                          {Number(
                            license.price
                          ).toLocaleString()}
                        </p>

                        <div className="mt-3 space-y-1">
                          <div className="flex items-center gap-2 text-xs text-white/50">
                            <Check size={13} />

                            <span>
                              {license.commercial_use
                                ? "Commercial use"
                                : "Personal use"}
                            </span>
                          </div>

                          <div className="flex items-center gap-2 text-xs text-white/50">
                            <Check size={13} />

                            <span>
                              {license.stems_included
                                ? "Stems included"
                                : "No stems"}
                            </span>
                          </div>

                          {license.exclusive && (
                            <div className="flex items-center gap-2 text-xs text-white/50">
                              <Check size={13} />

                              <span>
                                Exclusive
                              </span>
                            </div>
                          )}
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>

            {/* =================================================
                MESSAGE
            ================================================= */}

            {message && (
              <div
                className={[
                  "mt-4 rounded-2xl border px-4 py-3 text-sm",
                  message.type === "success"
                    ? "border-[#1ed760]/30 bg-[#1ed760]/10 text-[#1ed760]"
                    : "border-red-500/30 bg-red-500/10 text-red-400",
                ].join(" ")}
              >
                {message.text}
              </div>
            )}

            {/* =================================================
                PURCHASE / DOWNLOAD
            ================================================= */}

            <div className="mt-5">
              {existingPurchase ? (
                <>
                  <div
                    className="
                      mb-3
                      rounded-2xl
                      border
                      border-[#1ed760]/20
                      bg-[#1ed760]/5
                      px-4
                      py-3
                    "
                  >
                    <div className="flex items-center gap-2">
                      <div
                        className="
                          flex
                          h-6
                          w-6
                          shrink-0
                          items-center
                          justify-center
                          rounded-full
                          bg-[#1ed760]
                          text-black
                        "
                      >
                        <Check
                          size={14}
                          strokeWidth={3}
                        />
                      </div>

                      <div className="min-w-0">
                        <p className="text-sm font-bold text-[#1ed760]">
                          You own this beat
                        </p>

                        <p className="text-xs text-white/40">
                          Your purchase is ready
                          to download.
                        </p>
                      </div>
                    </div>
                  </div>

                  <button
                    type="button"
                    disabled={
                      downloading ||
                      purchasesLoading
                    }
                    onClick={
                      handleDownload
                    }
                    className="
                      flex
                      h-12
                      w-full
                      items-center
                      justify-center
                      gap-2
                      rounded-full
                      bg-[#1ed760]
                      text-xs
                      font-bold
                      text-black
                      transition
                      active:scale-[0.98]
                      disabled:cursor-not-allowed
                      disabled:opacity-50
                      min-[360px]:h-14
                      min-[360px]:text-sm
                    "
                  >
                    {downloading ? (
                      <Loader2
                        size={18}
                        className="animate-spin"
                      />
                    ) : (
                      <Download size={18} />
                    )}

                    {downloading
                      ? "Preparing download..."
                      : "DOWNLOAD BEAT"}
                  </button>
                </>
              ) : (
                <button
                  type="button"
                  disabled={
                    !selectedLicense ||
                    buying ||
                    licenses.length === 0
                  }
                  onClick={handleBuy}
                  className="
                    flex
                    h-12
                    w-full
                    items-center
                    justify-center
                    gap-2
                    rounded-full
                    bg-[#1ed760]
                    text-xs
                    font-bold
                    text-black
                    transition
                    active:scale-[0.98]
                    disabled:cursor-not-allowed
                    disabled:opacity-30
                    min-[360px]:h-14
                    min-[360px]:text-sm
                  "
                >
                  {buying ? (
                    <Loader2
                      size={18}
                      className="animate-spin"
                    />
                  ) : (
                    <ShoppingCart
                      size={18}
                    />
                  )}

                  {buying
                    ? "Processing..."
                    : selectedLicense
                      ? "BUY THIS BEAT"
                      : "SELECT A LICENSE"}
                </button>
              )}
            </div>

            {/* =================================================
                STATS
            ================================================= */}

            <div className="mt-6 flex w-full flex-col gap-2">
              <div
                className="
                  rounded-2xl
                  border
                  border-white/10
                  bg-white/[0.03]
                  p-4
                "
              >
                <p className="text-xs text-white/40">
                  Plays
                </p>

                <p className="mt-1 text-lg font-bold">
                  {beat.plays.toLocaleString()}
                </p>
              </div>

              <div
                className="
                  rounded-2xl
                  border
                  border-white/10
                  bg-white/[0.03]
                  p-4
                "
              >
                <p className="text-xs text-white/40">
                  Sales
                </p>

                <p className="mt-1 text-lg font-bold">
                  {beat.sales.toLocaleString()}
                </p>
              </div>

              <div
                className="
                  rounded-2xl
                  border
                  border-white/10
                  bg-white/[0.03]
                  p-4
                "
              >
                <p className="text-xs text-white/40">
                  Producer
                </p>

                <p className="mt-1 truncate text-sm font-bold">
                  {
                    beat.producer
                      .producer_name
                  }
                </p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
