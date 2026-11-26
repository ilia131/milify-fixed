import { Activity } from "lucide-react";

export default function DashboardHeader() {
  return (
    <div className="flex items-end justify-between">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">
          Overview
        </h1>

        <p className="mt-1 text-sm text-zinc-500">
          Welcome back. Here's what's happening on Milify.
        </p>
      </div>

      <div className="hidden items-center gap-2 rounded-lg border border-white/[0.06] bg-white/[0.02] px-3 py-2 text-xs text-zinc-500 sm:flex">
        <Activity size={14} />

        System operational
      </div>
    </div>
  );
}