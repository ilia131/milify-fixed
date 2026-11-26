"use client";

import {
  ArrowUpRight,
  CreditCard,
  Megaphone,
  Music2,
  Users,
  Mic2,
  Wallet,
} from "lucide-react";

import DashboardCard from "./DashboardCard";
import MetricRow from "./MetricRow";

import { useDashboard } from "../../features/admin/hooks/useDashboard";

import {
  useGetAdminRevenueQuery,
} from "@/redux/services/admin/adminRevenueApi";

import {
  useGetAdminAdsQuery,
} from "@/redux/services/admin/adminAdsApi";

import {
  useGetAdminArtistsQuery,
} from "@/redux/services/admin/adminArtistsApi";

import {
  useGetAdminSongsQuery,
} from "@/redux/services/admin/adminSongsApi";


export default function DashboardOverviewCards() {

  /* =========================================================
     USERS
  ========================================================= */

  const {
    totalUsers,
    isLoading: usersLoading,
  } = useDashboard();


  /* =========================================================
     REVENUE
  ========================================================= */

  const {
    data: revenue,
    isLoading: revenueLoading,
  } = useGetAdminRevenueQuery();


  /* =========================================================
     ARTISTS
  ========================================================= */

  const {
    data: artists,
    isLoading: artistsLoading,
  } = useGetAdminArtistsQuery({
    page: 1,
  });


  /* =========================================================
     SONGS
  ========================================================= */

  const {
    data: songs,
    isLoading: songsLoading,
  } = useGetAdminSongsQuery({
    page: 1,
  });


  /* =========================================================
     ADVERTISEMENTS
  ========================================================= */

  const {
    data: ads,
    isLoading: adsLoading,
  } = useGetAdminAdsQuery({
    page: 1,
    // page_size: 100,
  });


  /* =========================================================
     COUNTS
  ========================================================= */

  const artistCount =
    artists?.count ?? 0;

  const songCount =
    songs?.count ?? 0;

  const advertisementCount =
    ads?.count ?? 0;

  const activeAdvertisementCount =
    ads?.results?.filter(
      (ad) => ad.is_active
    ).length ?? 0;


  /* =========================================================
     REVENUE
  ========================================================= */

  const totalRevenue =
    Number(
      revenue?.total_revenue ?? 0
    );

  const monthlyRevenue =
    Number(
      revenue?.monthly_revenue ?? 0
    );


  /* =========================================================
     SUBSCRIPTIONS
  ========================================================= */

  const activeSubscriptions =
    revenue?.active_subscriptions ?? 0;


  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">


      {/* =====================================================
          USERS
      ===================================================== */}

      <DashboardCard
        title="Users"
        description="User activity overview"
        icon={Users}
        href="/admin/users"
      >

        <div className="mt-6">

          <div className="flex items-end justify-between">

            <div>

              <div className="text-3xl font-semibold tracking-tight">

                {usersLoading
                  ? "..."
                  : totalUsers.toLocaleString()}

              </div>

              <div className="mt-1 text-xs text-zinc-600">
                Total registered users
              </div>

            </div>


            <div className="flex items-center gap-1 rounded-lg bg-white/[0.05] px-2 py-1 text-xs text-zinc-400">

              <ArrowUpRight size={12} />

              View

            </div>

          </div>


          <div className="mt-7 flex h-20 items-end gap-1.5">

            {[
              35,
              50,
              42,
              65,
              52,
              75,
              68,
              82,
              58,
              70,
              88,
              76,
            ].map(
              (height, index) => (

                <div
                  key={index}
                  className="flex-1 rounded-t-md bg-white/[0.08]"
                  style={{
                    height: `${height}%`,
                  }}
                />

              )
            )}

          </div>

        </div>

      </DashboardCard>


      {/* =====================================================
          ARTISTS
      ===================================================== */}

      <DashboardCard
        title="Artists"
        description="Artist ecosystem"
        icon={Mic2}
        href="/admin/artists"
      >

        <div className="mt-6">


          <div className="text-3xl font-semibold tracking-tight">

            {artistsLoading
              ? "..."
              : artistCount.toLocaleString()}

          </div>


          <div className="mt-1 text-xs text-zinc-600">
            Registered artists
          </div>


          <div className="mt-7 space-y-3">

            <MetricRow
              label="Total artists"
              value={
                artistsLoading
                  ? "..."
                  : artistCount.toLocaleString()
              }
            />

            <MetricRow
              label="Featured"
              value={
                artistsLoading
                  ? "..."
                  : (
                      artists?.results?.filter(
                        (artist) =>
                          artist.is_featured
                      ).length ?? 0
                    ).toLocaleString()
              }
            />

            <MetricRow
              label="Active"
              value={
                artistsLoading
                  ? "..."
                  : (
                      artists?.results?.filter(
                        (artist) =>
                          artist.is_active
                      ).length ?? 0
                    ).toLocaleString()
              }
            />

          </div>

        </div>

      </DashboardCard>


      {/* =====================================================
          SONGS
      ===================================================== */}

      <DashboardCard
        title="Songs"
        description="Music catalog"
        icon={Music2}
        href="/admin/songs"
      >

        <div className="mt-6">


          <div className="text-3xl font-semibold tracking-tight">

            {songsLoading
              ? "..."
              : songCount.toLocaleString()}

          </div>


          <div className="mt-1 text-xs text-zinc-600">
            Total songs
          </div>


          <div className="mt-7 space-y-3">

            <MetricRow
              label="Published"
              value={
                songsLoading
                  ? "..."
                  : (
                      songs?.results?.filter(
                        (song) =>
                          song.is_published
                      ).length ?? 0
                    ).toLocaleString()
              }
            />

            <MetricRow
              label="Verified"
              value={
                songsLoading
                  ? "..."
                  : (
                      songs?.results?.filter(
                        (song) =>
                          song.verified
                      ).length ?? 0
                    ).toLocaleString()
              }
            />

            <MetricRow
              label="Total plays"
              value={
                songsLoading
                  ? "..."
                  : (
                      songs?.results?.reduce(
                        (
                          total,
                          song
                        ) =>
                          total +
                          Number(
                            song.play_count ?? 0
                          ),
                        0
                      ) ?? 0
                    ).toLocaleString()
              }
            />

          </div>

        </div>

      </DashboardCard>


      {/* =====================================================
          REVENUE
      ===================================================== */}

      <DashboardCard
        title="Revenue"
        description="Platform financial overview"
        icon={Wallet}
        href="/admin/revenue"
      >

        <div className="mt-6">


          <div className="text-3xl font-semibold tracking-tight">

            {revenueLoading
              ? "..."
              : totalRevenue.toLocaleString()}

          </div>


          <div className="mt-1 text-xs text-zinc-600">
            Total revenue
          </div>


          <div className="mt-7 space-y-3">

            <MetricRow
              label="Today"
              value={
                revenueLoading
                  ? "..."
                  : Number(
                      revenue?.today_revenue ?? 0
                    ).toLocaleString()
              }
            />

            <MetricRow
              label="This month"
              value={
                revenueLoading
                  ? "..."
                  : monthlyRevenue.toLocaleString()
              }
            />

            <MetricRow
              label="Platform"
              value={
                revenueLoading
                  ? "..."
                  : Number(
                      revenue?.platform_revenue ?? 0
                    ).toLocaleString()
              }
            />

          </div>

        </div>

      </DashboardCard>


      {/* =====================================================
          SUBSCRIPTIONS
      ===================================================== */}

      <DashboardCard
        title="Subscriptions"
        description="Premium membership"
        icon={CreditCard}
        href="/admin/subscriptions"
      >

        <div className="mt-6">


          <div className="text-3xl font-semibold tracking-tight">

            {revenueLoading
              ? "..."
              : activeSubscriptions.toLocaleString()}

          </div>


          <div className="mt-1 text-xs text-zinc-600">
            Active subscriptions
          </div>


          <div className="mt-7 space-y-3">

            <MetricRow
              label="Active members"
              value={
                revenueLoading
                  ? "..."
                  : activeSubscriptions.toLocaleString()
              }
            />

            <MetricRow
              label="Successful payments"
              value={
                revenueLoading
                  ? "..."
                  : Number(
                      revenue?.successful_payments ?? 0
                    ).toLocaleString()
              }
            />

            <MetricRow
              label="Pending payments"
              value={
                revenueLoading
                  ? "..."
                  : Number(
                      revenue?.pending_payments ?? 0
                    ).toLocaleString()
              }
            />

          </div>

        </div>

      </DashboardCard>


      {/* =====================================================
          ADVERTISEMENTS
      ===================================================== */}

      <DashboardCard
        title="Advertisements"
        description="Campaign performance"
        icon={Megaphone}
        href="/admin/advertisements"
      >

        <div className="mt-6">


          <div className="text-3xl font-semibold tracking-tight">

            {adsLoading
              ? "..."
              : activeAdvertisementCount.toLocaleString()}

          </div>


          <div className="mt-1 text-xs text-zinc-600">
            Active advertisements
          </div>


          <div className="mt-7 space-y-3">

            <MetricRow
              label="Total advertisements"
              value={
                adsLoading
                  ? "..."
                  : advertisementCount.toLocaleString()
              }
            />

            <MetricRow
              label="Active"
              value={
                adsLoading
                  ? "..."
                  : activeAdvertisementCount.toLocaleString()
              }
            />

            <MetricRow
              label="Inactive"
              value={
                adsLoading
                  ? "..."
                  : (
                      advertisementCount -
                      activeAdvertisementCount
                    ).toLocaleString()
              }
            />

          </div>

        </div>

      </DashboardCard>


    </div>
  );
}
