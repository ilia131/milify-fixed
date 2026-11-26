"use client";

import {
  Users,
  Mic2,
  Music2,
  Wallet,
} from "lucide-react";

import DashboardStatCard from "./DashboardStatCard";
import { useDashboard } from "../../features/admin/hooks/useDashboard";

export default function DashboardStats() {
  const {
    totalUsers,
    isLoading,
  } = useDashboard();

  const stats = [
    {
      title: "Total Users",
      value: isLoading
        ? "..."
        : totalUsers.toLocaleString(),
      description: "Registered users",
      icon: Users,
    },
    {
      title: "Artists",
      value: "—",
      description: "Artist accounts",
      icon: Mic2,
    },
    {
      title: "Total Songs",
      value: "—",
      description: "Published tracks",
      icon: Music2,
    },
    {
      title: "Revenue",
      value: "—",
      description: "Total platform revenue",
      icon: Wallet,
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {stats.map((stat) => (
        <DashboardStatCard
          key={stat.title}
          {...stat}
        />
      ))}
    </div>
  );
}