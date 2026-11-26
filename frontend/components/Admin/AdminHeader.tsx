"use client";

import { usePathname } from "next/navigation";
import {
  Bell,
  ChevronDown,
  Search,
  Command,
  Activity,
  Radio,
  ShieldCheck,
} from "lucide-react";
import { useState } from "react";

const pageTitles: Record<string, string> = {
  "/admin": "Dashboard",
  "/admin/users": "Users",
  "/admin/artists": "Artists",
  "/admin/songs": "Songs",
  "/admin/playlists": "Playlists",
  "/admin/subscriptions": "Subscriptions",
  "/admin/payments": "Payments",
  "/admin/revenue": "Revenue",
  "/admin/advertisements": "Advertisements",
  "/admin/settings": "Settings",
};

export default function AdminHeader() {
  const pathname = usePathname();

  const [openProfile, setOpenProfile] = useState(false);

  const currentTitle =
    pageTitles[pathname] ||
    Object.entries(pageTitles).find(
      ([path]) =>
        path !== "/admin" &&
        pathname.startsWith(path)
    )?.[1] ||
    "Admin";

  return (
    <header
      className="
        sticky
        top-0
        z-40
        flex
        h-[76px]
        items-center
        border-b
        border-violet-400/[0.08]
        bg-[#030305]/80
        px-6
        backdrop-blur-2xl
      "
    >

      {/* Header top glow */}

      <div
        className="
          pointer-events-none
          absolute
          left-0
          right-0
          top-0
          h-px
          bg-gradient-to-r
          from-transparent
          via-violet-400/50
          to-transparent
        "
      />

      <div className="flex w-full items-center justify-between gap-6">

        {/* LEFT */}

        <div>

          <div className="flex items-center gap-2">

            <span
              className="
                text-[9px]
                font-bold
                uppercase
                tracking-[0.22em]
                text-violet-400/50
              "
            >
              MILIFY
            </span>

            <span className="text-zinc-800">
              {"//"}
            </span>

            <span
              className="
                text-[9px]
                font-bold
                uppercase
                tracking-[0.20em]
                text-zinc-600
              "
            >
              CONTROL
            </span>

          </div>

          <div className="mt-1 flex items-center gap-2">

            <h1
              className="
                text-lg
                font-semibold
                tracking-[-0.02em]
                text-white
              "
            >
              {currentTitle}
            </h1>

            <span
              className="
                rounded-md
                border
                border-violet-400/[0.12]
                bg-violet-400/[0.05]
                px-1.5
                py-0.5
                text-[8px]
                font-bold
                tracking-[0.15em]
                text-violet-400/60
              "
            >
              LIVE
            </span>

          </div>

        </div>

        {/* RIGHT */}

        <div className="flex items-center gap-2">

          {/* System status */}

          <div
            className="
              hidden
              items-center
              gap-2
              rounded-xl
              border
              border-emerald-400/[0.12]
              bg-emerald-400/[0.025]
              px-3
              py-2
              md:flex
            "
          >

            <div className="relative flex h-2 w-2">

              <span
                className="
                  absolute
                  inline-flex
                  h-full
                  w-full
                  animate-ping
                  rounded-full
                  bg-emerald-400
                  opacity-50
                "
              />

              <span
                className="
                  relative
                  h-2
                  w-2
                  rounded-full
                  bg-emerald-400
                  shadow-[0_0_10px_#39FF88]
                "
              />

            </div>

            <span className="text-[9px] font-bold tracking-[0.12em] text-emerald-400/70">
              ONLINE
            </span>

          </div>

          {/* Search */}

          <button
            type="button"
            className="
              hidden
              h-10
              w-[240px]
              items-center
              gap-3
              rounded-xl
              border
              border-violet-400/[0.10]
              bg-white/[0.02]
              px-3
              text-left
              text-zinc-600
              transition
              hover:border-violet-400/[0.20]
              hover:bg-violet-500/[0.03]
              md:flex
            "
          >

            <Search size={15} />

            <span className="flex-1 text-[11px]">
              Search command...
            </span>

            <span
              className="
                flex
                items-center
                gap-1
                rounded-md
                border
                border-white/[0.07]
                bg-white/[0.035]
                px-1.5
                py-1
                text-[8px]
                text-zinc-600
              "
            >

              <Command size={8} />

              K

            </span>

          </button>

          {/* Live activity */}

          <button
            type="button"
            className="
              hidden
              h-10
              w-10
              items-center
              justify-center
              rounded-xl
              border
              border-white/[0.07]
              bg-white/[0.02]
              text-zinc-500
              transition
              hover:border-violet-400/[0.15]
              hover:bg-violet-500/[0.04]
              hover:text-violet-300
              sm:flex
            "
          >

            <Radio size={16} />

          </button>

          {/* Notifications */}

          <button
            type="button"
            className="
              relative
              flex
              h-10
              w-10
              items-center
              justify-center
              rounded-xl
              border
              border-white/[0.07]
              bg-white/[0.02]
              text-zinc-500
              transition
              hover:border-violet-400/[0.15]
              hover:bg-violet-500/[0.04]
              hover:text-white
            "
          >

            <Bell size={16} />

            <span
              className="
                absolute
                right-2.5
                top-2
                h-1.5
                w-1.5
                rounded-full
                bg-[#FF2BD6]
                shadow-[0_0_9px_#FF2BD6]
              "
            />

          </button>

          {/* Divider */}

          <div className="mx-1 h-7 w-px bg-white/[0.07]" />

          {/* Profile */}

          <div className="relative">

            <button
              type="button"
              onClick={() =>
                setOpenProfile((prev) => !prev)
              }
              className="
                flex
                items-center
                gap-2
                rounded-xl
                border
                border-transparent
                p-1.5
                transition
                hover:border-violet-400/[0.10]
                hover:bg-violet-500/[0.035]
              "
            >

              <div
                className="
                  relative
                  flex
                  h-9
                  w-9
                  items-center
                  justify-center
                  rounded-full
                  border
                  border-violet-400/20
                  bg-violet-500/[0.08]
                  text-xs
                  font-black
                  text-violet-300
                "
              >

                M

                <span
                  className="
                    absolute
                    bottom-0
                    right-0
                    h-2.5
                    w-2.5
                    rounded-full
                    border-2
                    border-[#030305]
                    bg-[#39FF88]
                    shadow-[0_0_8px_#39FF88]
                  "
                />

              </div>

              <div className="hidden text-left lg:block">

                <div className="text-[11px] font-semibold text-white">
                  Milify Admin
                </div>

                <div className="mt-0.5 text-[8px] text-violet-400/50">
                  ROOT ACCESS
                </div>

              </div>

              <ChevronDown
                size={13}
                className={`
                  hidden
                  text-zinc-600
                  transition-transform
                  lg:block
                  ${openProfile ? "rotate-180" : ""}
                `}
              />

            </button>

            {/* Dropdown */}

            {openProfile && (

              <div
                className="
                  absolute
                  right-0
                  top-[52px]
                  w-[230px]
                  overflow-hidden
                  rounded-2xl
                  border
                  border-violet-400/[0.14]
                  bg-[#09090D]
                  p-1.5
                  shadow-[0_20px_60px_rgba(0,0,0,0.65),0_0_30px_rgba(139,92,246,0.05)]
                "
              >

                <div className="border-b border-white/[0.06] px-3 py-3">

                  <div className="flex items-center gap-2">

                    <ShieldCheck
                      size={14}
                      className="text-violet-400"
                    />

                    <div className="text-xs font-semibold text-white">
                      Milify Admin
                    </div>

                  </div>

                  <div className="mt-1 text-[9px] text-zinc-600">
                    Full system access
                  </div>

                </div>

                <button
                  type="button"
                  className="
                    mt-1
                    flex
                    w-full
                    items-center
                    rounded-xl
                    px-3
                    py-2.5
                    text-left
                    text-[11px]
                    text-zinc-400
                    transition
                    hover:bg-violet-500/[0.05]
                    hover:text-white
                  "
                >
                  Account Settings
                </button>

                <button
                  type="button"
                  className="
                    flex
                    w-full
                    items-center
                    rounded-xl
                    px-3
                    py-2.5
                    text-left
                    text-[11px]
                    text-red-400
                    transition
                    hover:bg-red-500/[0.06]
                  "
                >
                  Sign out
                </button>

              </div>

            )}

          </div>

        </div>

      </div>

    </header>
  );
}