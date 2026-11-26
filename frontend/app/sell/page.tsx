"use client";

import Link from "next/link";
import {
  ArrowLeft,
  Music2,
  Upload,
  DollarSign,
  BarChart3,
  ShieldCheck,
  ChevronRight,
} from "lucide-react";

export default function SellPage() {
  return (
    <main className="min-h-screen overflow-x-hidden bg-[#050505] pb-28 text-white">
      <div className="px-3 pt-5 min-[360px]:px-4">
        <Link
          href="/beats"
          className="inline-flex items-center gap-1.5 text-[11px] text-white/40 min-[360px]:text-xs"
        >
          <ArrowLeft size={15} />
          Marketplace
        </Link>

        {/* HERO */}

        <section className="mt-5 overflow-hidden rounded-3xl border border-white/[0.07] bg-gradient-to-br from-[#111] to-[#07130b] p-5 min-[360px]:p-6">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#1ed760] text-black">
            <Music2 size={22} />
          </div>

          <h1 className="mt-5 text-[29px] font-bold leading-[1.05] min-[360px]:text-[34px]">
            Sell your sound
            <span className="text-[#1ed760]">
              .
            </span>
          </h1>

          <p className="mt-3 text-xs leading-5 text-white/40 min-[360px]:text-sm">
            Upload your beats, reach artists,
            and earn from every sale.
          </p>

          <button
            type="button"
            className="mt-5 flex h-12 w-full items-center justify-center gap-2 rounded-full bg-[#1ed760] text-xs font-bold text-black min-[360px]:text-sm"
          >
            <Upload size={17} />
            Start selling
          </button>
        </section>

        {/* FEATURES */}

        <section className="mt-6 grid grid-cols-1 gap-2.5">
          <Feature
            icon={
              <Upload size={18} />
            }
            title="Upload your beats"
            description="Showcase your sounds with previews, covers and licenses."
          />

          <Feature
            icon={
              <DollarSign size={18} />
            }
            title="Set your price"
            description="Create different license options for your beats."
          />

          <Feature
            icon={
              <BarChart3 size={18} />
            }
            title="Track your sales"
            description="Keep an eye on your sales and marketplace revenue."
          />

          <Feature
            icon={
              <ShieldCheck size={18} />
            }
            title="Secure payments"
            description="Milify handles the platform transaction flow."
          />
        </section>

        {/* CTA */}

        <section className="mt-6 rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
          <p className="text-[10px] font-bold text-[#1ed760]">
            MILIFY PRODUCERS
          </p>

          <h2 className="mt-2 text-base font-bold">
            Ready to put your beats out there?
          </h2>

          <p className="mt-2 text-[10px] leading-5 text-white/35">
            Build your producer profile and
            start creating your marketplace
            catalog.
          </p>

          <button
            type="button"
            className="mt-4 flex h-10 w-full items-center justify-between rounded-xl bg-white/[0.05] px-3 text-xs font-semibold"
          >
            Create producer profile

            <ChevronRight size={15} />
          </button>
        </section>
      </div>
    </main>
  );
}

function Feature({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="flex min-w-0 gap-3 rounded-2xl border border-white/[0.07] bg-[#0d0d0d] p-3.5">
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#1ed760]/10 text-[#1ed760]">
        {icon}
      </div>

      <div className="min-w-0">
        <h3 className="text-xs font-bold min-[360px]:text-sm">
          {title}
        </h3>

        <p className="mt-1 text-[9px] leading-4 text-white/30 min-[360px]:text-[10px] min-[360px]:leading-5">
          {description}
        </p>
      </div>
    </div>
  );
}