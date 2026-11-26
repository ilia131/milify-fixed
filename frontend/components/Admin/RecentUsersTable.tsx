"use client";

import {
  ArrowLeft,
  ArrowRight,
  ArrowUpRight,
  Power,
} from "lucide-react";

import { useRouter } from "next/navigation";

import { useDashboard } from "../../features/admin/hooks/useDashboard";
import { formatDate } from "../../features/admin/utils/formatDate";

interface UserRowProps {
  user: {
    id: number;
    username: string;
    email: string;
    first_name?: string;
    last_name?: string;
    is_artist: boolean;
    is_active: boolean;
    created_at: string;
  };

  onToggleActive: (id: number) => void;
  isToggling: boolean;
}

function UserRow({
  user,
  onToggleActive,
  isToggling,
}: UserRowProps) {
  const router = useRouter();

  const displayName =
    user.first_name || user.last_name
      ? `${user.first_name ?? ""} ${
          user.last_name ?? ""
        }`.trim()
      : user.username;

  const initial = (
    user.first_name?.[0] ||
    user.username?.[0] ||
    "U"
  ).toUpperCase();

  const handleRowClick = () => {
    router.push(`/admin/users/${user.id}`);
  };

  return (
    <tr
      onClick={handleRowClick}
      className="group cursor-pointer border-b border-white/[0.04] transition hover:bg-white/[0.03]"
    >
      {/* User */}

      <td className="px-5 py-4">
        <div className="flex items-center gap-3">

          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white/[0.06] text-xs font-semibold text-zinc-300">
            {initial}
          </div>

          <div>
            <div className="text-sm font-medium text-zinc-200 group-hover:text-white">
              {displayName}
            </div>

            <div className="text-xs text-zinc-600">
              @{user.username}
            </div>
          </div>

        </div>
      </td>

      {/* Email */}

      <td className="px-5 py-4 text-sm text-zinc-500">
        {user.email}
      </td>

      {/* Type */}

      <td className="px-5 py-4">

        <span className="rounded-lg bg-white/[0.05] px-2.5 py-1 text-[11px] text-zinc-400">
          {user.is_artist
            ? "Artist"
            : "Listener"}
        </span>

      </td>

      {/* Status */}

      <td className="px-5 py-4">

        <span className="flex w-fit items-center gap-1.5 text-xs">

          <span
            className={`h-1.5 w-1.5 rounded-full ${
              user.is_active
                ? "bg-emerald-400"
                : "bg-red-400"
            }`}
          />

          <span
            className={
              user.is_active
                ? "text-zinc-400"
                : "text-red-400"
            }
          >
            {user.is_active
              ? "Active"
              : "Inactive"}
          </span>

        </span>

      </td>

      {/* Joined */}

      <td className="px-5 py-4 text-xs text-zinc-600">
        {formatDate(user.created_at)}
      </td>

      {/* Action */}

      <td
        className="px-5 py-4"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          type="button"
          disabled={isToggling}
          onClick={() =>
            onToggleActive(user.id)
          }
          title={
            user.is_active
              ? "Deactivate user"
              : "Activate user"
          }
          className={`
            inline-flex
            items-center
            gap-1.5
            rounded-lg
            border
            px-2.5
            py-1.5
            text-[11px]
            font-medium
            transition
            disabled:cursor-not-allowed
            disabled:opacity-40
            ${
              user.is_active
                ? "border-red-500/10 bg-red-500/5 text-red-400 hover:bg-red-500/10"
                : "border-emerald-500/10 bg-emerald-500/5 text-emerald-400 hover:bg-emerald-500/10"
            }
          `}
        >
          <Power size={12} />

          {isToggling
            ? "Updating..."
            : user.is_active
              ? "Deactivate"
              : "Activate"}
        </button>
      </td>
    </tr>
  );
}


/* ───────────────────────────────────── */
/* Loading */
/* ───────────────────────────────────── */

function LoadingRow() {
  return (
    <tr>
      <td
        colSpan={6}
        className="px-5 py-10 text-center text-sm text-zinc-600"
      >
        Loading users...
      </td>
    </tr>
  );
}


/* ───────────────────────────────────── */
/* Empty */
/* ───────────────────────────────────── */

function EmptyRow() {
  return (
    <tr>
      <td
        colSpan={6}
        className="px-5 py-10 text-center text-sm text-zinc-600"
      >
        No users found.
      </td>
    </tr>
  );
}


/* ───────────────────────────────────── */
/* Table */
/* ───────────────────────────────────── */

export default function RecentUsersTable() {
  const {
    users,
    isLoading,
    isFetching,

    page,

    hasNextPage,
    hasPreviousPage,

    nextPage,
    previousPage,

    toggleUserActive,
    isTogglingUser,
  } = useDashboard();

  return (
    <div className="rounded-2xl border border-white/[0.06] bg-[#0b0b0f]">

      {/* Header */}

      <div className="flex items-center justify-between border-b border-white/[0.06] px-5 py-4">

        <div>
          <h2 className="text-sm font-semibold">
            Users
          </h2>

          <p className="mt-1 text-xs text-zinc-600">
            Manage registered accounts
          </p>
        </div>

        <a
          href="/admin/users"
          onClick={(e) =>
            e.stopPropagation()
          }
          className="flex items-center gap-1 text-xs text-zinc-500 transition hover:text-white"
        >
          View all

          <ArrowUpRight size={13} />
        </a>

      </div>

      {/* Table */}

      <div className="overflow-x-auto">

        <table className="w-full min-w-[850px]">

          <thead>

            <tr className="border-b border-white/[0.05] text-left">

              <th className="px-5 py-3 text-[10px] font-medium uppercase tracking-wider text-zinc-600">
                User
              </th>

              <th className="px-5 py-3 text-[10px] font-medium uppercase tracking-wider text-zinc-600">
                Email
              </th>

              <th className="px-5 py-3 text-[10px] font-medium uppercase tracking-wider text-zinc-600">
                Type
              </th>

              <th className="px-5 py-3 text-[10px] font-medium uppercase tracking-wider text-zinc-600">
                Status
              </th>

              <th className="px-5 py-3 text-[10px] font-medium uppercase tracking-wider text-zinc-600">
                Joined
              </th>

              <th className="px-5 py-3 text-[10px] font-medium uppercase tracking-wider text-zinc-600">
                Action
              </th>

            </tr>

          </thead>

          <tbody>

            {isLoading ? (
              <LoadingRow />
            ) : users.length ? (
              users.map((user) => (
                <UserRow
                  key={user.id}
                  user={user}
                  onToggleActive={
                    toggleUserActive
                  }
                  isToggling={
                    isTogglingUser
                  }
                />
              ))
            ) : (
              <EmptyRow />
            )}

          </tbody>

        </table>

      </div>

      {/* Pagination */}

      <div className="flex items-center justify-between border-t border-white/[0.06] px-5 py-4">

        <div className="text-xs text-zinc-600">
          Page{" "}
          <span className="text-zinc-300">
            {page}
          </span>
        </div>

        <div className="flex items-center gap-2">

          <button
            type="button"
            onClick={previousPage}
            disabled={
              !hasPreviousPage ||
              isFetching
            }
            className="
              inline-flex
              h-9
              items-center
              gap-2
              rounded-lg
              border
              border-white/[0.06]
              bg-white/[0.02]
              px-3
              text-xs
              text-zinc-400
              transition
              hover:bg-white/[0.05]
              hover:text-white
              disabled:cursor-not-allowed
              disabled:opacity-30
            "
          >
            <ArrowLeft size={13} />
            Previous
          </button>

          <button
            type="button"
            onClick={nextPage}
            disabled={
              !hasNextPage ||
              isFetching
            }
            className="
              inline-flex
              h-9
              items-center
              gap-2
              rounded-lg
              border
              border-white/[0.06]
              bg-white/[0.02]
              px-3
              text-xs
              text-zinc-400
              transition
              hover:bg-white/[0.05]
              hover:text-white
              disabled:cursor-not-allowed
              disabled:opacity-30
            "
          >
            Next
            <ArrowRight size={13} />
          </button>

        </div>

      </div>

    </div>
  );
}