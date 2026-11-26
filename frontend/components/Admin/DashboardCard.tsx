import { ArrowUpRight, LucideIcon } from "lucide-react";

interface DashboardCardProps {
  title: string;
  description: string;
  icon: LucideIcon;
  href: string;
  children: React.ReactNode;
}

export default function DashboardCard({
  title,
  description,
  icon: Icon,
  href,
  children,
}: DashboardCardProps) {
  return (
    <div className="rounded-2xl border border-white/[0.06] bg-[#0b0b0f] p-5">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/[0.04] text-zinc-500">
            <Icon size={17} />
          </div>

          <div>
            <h2 className="text-sm font-semibold">
              {title}
            </h2>

            <p className="mt-0.5 text-[11px] text-zinc-600">
              {description}
            </p>
          </div>
        </div>

        <a
          href={href}
          className="text-zinc-600 transition hover:text-white"
          aria-label={`Open ${title}`}
        >
          <ArrowUpRight size={16} />
        </a>
      </div>

      {children}
    </div>
  );
}