"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import {
  LayoutDashboard,
  Users,
  Mic2,
  Music2,
  ListMusic,
  CreditCard,
  Wallet,
  Megaphone,
  Settings,
  ChevronRight,
  Activity,
  Zap,
  Radio,
  Database,
} from "lucide-react";

const navigation = [
  {
    title: "CORE",
    items: [
      {
        label: "Dashboard",
        href: "/admin",
        icon: LayoutDashboard,
      },
    ],
  },

  {
    title: "IDENTITY",
    items: [
      {
        label: "Users",
        href: "/admin/users",
        icon: Users,
      },
      {
        label: "Artists",
        href: "/admin/artists",
        icon: Mic2,
      },
    ],
  },

  {
    title: "CONTENT",
    items: [
      {
        label: "Songs",
        href: "/admin/songs",
        icon: Music2,
      },
      {
        label: "Playlists",
        href: "/admin/playlists",
        icon: ListMusic,
      },
    ],
  },

  {
    title: "ECONOMY",
    items: [
      {
        label: "Subscriptions",
        href: "/admin/subscriptions",
        icon: CreditCard,
      },
      {
        label: "Payments",
        href: "/admin/payments",
        icon: Wallet,
      },
      {
        label: "Revenue",
        href: "/admin/revenue",
        icon: Wallet,
      },
    ],
  },

  {
    title: "GROWTH",
    items: [
      {
        label: "Advertisements",
        href: "/admin/advertisements",
        icon: Megaphone,
      },
    ],
  },
];

export default function AdminSidebar() {
  const pathname = usePathname();

  return (
    <aside
      className="
        fixed
        left-0
        top-0
        z-50
        flex
        h-screen
        w-[270px]
        flex-col
        overflow-hidden
        border-r
        border-violet-400/[0.10]
        bg-[#030305]/95
        backdrop-blur-2xl
      "
    >

      {/* Cyber glow */}

      <div
        className="
          pointer-events-none
          absolute
          left-[-120px]
          top-[80px]
          h-[300px]
          w-[300px]
          rounded-full
          bg-violet-600/[0.08]
          blur-[120px]
        "
      />

      <div
        className="
          pointer-events-none
          absolute
          bottom-[-100px]
          right-[-100px]
          h-[250px]
          w-[250px]
          rounded-full
          bg-emerald-400/[0.04]
          blur-[100px]
        "
      />

      {/* Top accent */}

      <div
        className="
          absolute
          left-0
          right-0
          top-0
          h-px
          bg-gradient-to-r
          from-transparent
          via-violet-400/80
          to-transparent
          shadow-[0_0_12px_rgba(139,92,246,0.8)]
        "
      />

      {/* Logo */}

      <div
        className="
          relative
          flex
          h-[78px]
          items-center
          border-b
          border-white/[0.06]
          px-5
        "
      >

        <div className="flex items-center gap-3">

          {/* Logo */}

          <div
            className="
              relative
              flex
              h-11
              w-11
              items-center
              justify-center
              rounded-xl
              border
              border-violet-400/30
              bg-violet-500/[0.08]
              text-violet-300
              shadow-[0_0_30px_rgba(139,92,246,0.20)]
            "
          >

            <span className="text-[18px] font-black">
              M
            </span>

            {/* status */}

            <span
              className="
                absolute
                right-[-2px]
                top-[-2px]
                h-2.5
                w-2.5
                rounded-full
                border
                border-[#030305]
                bg-[#39FF88]
                shadow-[0_0_12px_#39FF88]
              "
            />

          </div>

          <div>

            <div
              className="
                text-[17px]
                font-black
                tracking-[0.04em]
                text-white
              "
            >
              MILIFY
            </div>

            <div
              className="
                mt-0.5
                text-[8px]
                font-semibold
                uppercase
                tracking-[0.30em]
                text-violet-400/60
              "
            >
              Control System
            </div>

          </div>

        </div>

      </div>

      {/* Navigation */}

      <div className="relative flex-1 overflow-y-auto px-3 py-6">

        {navigation.map((section) => (

          <div
            key={section.title}
            className="mb-7"
          >

            <div
              className="
                mb-2
                flex
                items-center
                gap-2
                px-3
              "
            >

              <span
                className="
                  h-[1px]
                  w-3
                  bg-violet-500/40
                "
              />

              <span
                className="
                  text-[9px]
                  font-bold
                  tracking-[0.22em]
                  text-zinc-600
                "
              >
                {section.title}
              </span>

            </div>

            <div className="space-y-1">

              {section.items.map((item) => {

                const Icon = item.icon;

                const active =
                  pathname === item.href ||
                  (
                    item.href !== "/admin" &&
                    pathname.startsWith(item.href)
                  );

                return (

                  <Link
                    key={item.href}
                    href={item.href}
                    className={`
                      group
                      relative
                      flex
                      h-11
                      items-center
                      gap-3
                      overflow-hidden
                      rounded-xl
                      border
                      px-3
                      transition-all
                      duration-200

                      ${
                        active
                          ? `
                            border-violet-400/[0.18]
                            bg-violet-500/[0.10]
                            text-white
                            shadow-[inset_0_0_25px_rgba(139,92,246,0.04),0_0_20px_rgba(139,92,246,0.05)]
                          `
                          : `
                            border-transparent
                            text-zinc-500
                            hover:border-violet-400/[0.08]
                            hover:bg-violet-500/[0.04]
                            hover:text-zinc-200
                          `
                      }
                    `}
                  >

                    {/* active line */}

                    {active && (
                      <span
                        className="
                          absolute
                          left-0
                          top-1/2
                          h-6
                          w-[2px]
                          -translate-y-1/2
                          rounded-r-full
                          bg-violet-400
                          shadow-[0_0_12px_#8B5CF6]
                        "
                      />
                    )}

                    {/* scan effect */}

                    {active && (
                      <span
                        className="
                          pointer-events-none
                          absolute
                          inset-0
                          bg-gradient-to-r
                          from-violet-500/[0.04]
                          via-transparent
                          to-transparent
                        "
                      />
                    )}

                    {/* icon */}

                    <div
                      className={`
                        relative
                        flex
                        h-8
                        w-8
                        shrink-0
                        items-center
                        justify-center
                        rounded-lg
                        border
                        transition-all

                        ${
                          active
                            ? `
                              border-violet-400/20
                              bg-violet-400/[0.12]
                              text-violet-300
                              shadow-[0_0_15px_rgba(139,92,246,0.10)]
                            `
                            : `
                              border-white/[0.04]
                              bg-white/[0.02]
                              text-zinc-600
                              group-hover:border-violet-400/[0.12]
                              group-hover:text-violet-300
                            `
                        }
                      `}
                    >

                      <Icon
                        size={16}
                        strokeWidth={active ? 2.2 : 1.7}
                      />

                    </div>

                    <span
                      className="
                        relative
                        flex-1
                        text-[12px]
                        font-medium
                      "
                    >
                      {item.label}
                    </span>

                    {active && (
                      <ChevronRight
                        size={13}
                        className="relative text-violet-400/70"
                      />
                    )}

                  </Link>

                );
              })}

            </div>

          </div>

        ))}

      </div>

      {/* System */}

      <div className="relative px-3 pb-3">

        <div
          className="
            relative
            overflow-hidden
            rounded-xl
            border
            border-emerald-400/[0.12]
            bg-emerald-400/[0.025]
            p-3
          "
        >

          <div
            className="
              absolute
              left-0
              top-0
              h-px
              w-full
              bg-gradient-to-r
              from-transparent
              via-emerald-400/60
              to-transparent
            "
          />

          <div className="flex items-center gap-2">

            <div className="relative flex h-6 w-6 items-center justify-center rounded-md bg-emerald-400/[0.08]">

              <Activity
                size={13}
                className="text-emerald-400"
              />

              <span
                className="
                  absolute
                  right-0.5
                  top-0.5
                  h-1.5
                  w-1.5
                  rounded-full
                  bg-emerald-400
                  shadow-[0_0_8px_#39FF88]
                "
              />

            </div>

            <div>

              <div className="text-[10px] font-semibold text-zinc-300">
                SYSTEM ONLINE
              </div>

              <div className="mt-0.5 text-[8px] text-zinc-600">
                API · DB · STORAGE
              </div>

            </div>

          </div>

        </div>

        <Link
          href="/admin/settings"
          className="
            mt-2
            flex
            h-10
            items-center
            gap-3
            rounded-xl
            px-3
            text-zinc-600
            transition
            hover:bg-white/[0.03]
            hover:text-zinc-200
          "
        >

          <Settings size={16} />

          <span className="text-[12px]">
            Settings
          </span>

        </Link>

      </div>

      {/* Admin */}

      <div className="border-t border-white/[0.06] p-3">

        <div
          className="
            flex
            items-center
            gap-3
            rounded-xl
            border
            border-white/[0.05]
            bg-white/[0.025]
            p-2.5
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
                bottom-[-1px]
                right-[-1px]
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

          <div className="min-w-0 flex-1">

            <div className="truncate text-[11px] font-semibold text-zinc-200">
              Milify Admin
            </div>

            <div className="mt-0.5 flex items-center gap-1 text-[8px] text-violet-400/60">

              <Zap size={8} />

              ROOT ACCESS

            </div>

          </div>

        </div>

      </div>

    </aside>
  );
}