import { LucideIcon } from "lucide-react";

interface DashboardStatCardProps {
  title: string;
  value: string;
  description: string;
  icon: LucideIcon;
}

export default function DashboardStatCard({
  title,
  value,
  description,
  icon: Icon,
}: DashboardStatCardProps) {
  return (
    <div className="group rounded-2xl border border-white/[0.06] bg-[#0b0b0f] p-5 transition hover:border-white/[0.1]">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-zinc-600">
            {title}
          </p>

          <p className="mt-2 text-2xl font-semibold tracking-tight">
            {value}
          </p>
        </div>

        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/[0.04] text-zinc-500 transition group-hover:text-white">
          <Icon size={17} />
        </div>
      </div>

      <p className="mt-4 text-[11px] text-zinc-700">
        {description}
      </p>
    </div>
  );
}