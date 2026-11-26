"use client";

import CardSection from "@/shared/CardSection/CardSection";
import RecentMusics from "./RecentMusics";

import { useArtistsQuery } from "@/redux/services/artistApislice";
import {
  useGetForYouQuery,
  useGetCategoryRecommendationsQuery,
} from "@/redux/services/songApiSlice";

import SkeletonSection from "@/shared/ui/Skeleton/SkeletonSection";

const categoryTitles: Record<string, string> = {
  GAMING: "Gaming",
  DRIVING: "Driving",
  GYM: "Gym",
  STUDY: "Study",
  SLEEP: "Sleep",
  PARTY: "Party",
  CHILL: "Chill",
  NIGHT_DRIVE: "Night Drive",
};

const Music = () => {
  const {
    isLoading: artistsLoading,
    error: artistsError,
  } = useArtistsQuery();

  const {
    data: ForYou,
    isLoading: forYouLoading,
  } = useGetForYouQuery(0);

  const {
    data: categories,
    isLoading: categoriesLoading,
  } = useGetCategoryRecommendationsQuery();

  const isLoading =
    artistsLoading ||
    forYouLoading ||
    categoriesLoading;

  if (isLoading) {
    return (
      <div className="pl-4 pt-15 pb-50">

        {/* Made For You */}
        <SkeletonSection
          title="Made For You"
        />

        {/* Recently Played */}
        <SkeletonSection
          title="Recently Played"
        />

        {/* Categories */}
        <SkeletonSection
          title="Gaming"
        />

        <SkeletonSection
          title="Driving"
        />

        <SkeletonSection
          title="Gym"
        />

        <SkeletonSection
          title="Study"
        />

      </div>
    );
  }

  if (artistsError) {
    return (
      <div className="p-4 text-red-500">
        Error loading music
      </div>
    );
  }

  return (
    <div
      className="
        pl-4
        relative
        hide-scrollbar
        pt-15
        overflow-hidden
        pb-50
        animate-[fadeIn_.4s_ease]
      "
    >

      {/* Made For You */}
      {ForYou && ForYou.length > 0 && (
        <CardSection
          title="Made For You"
          variant="track"
          items={ForYou}
        />
      )}

      {/* Recently Played */}
      <RecentMusics />

      {/* Categories */}
      {Object.entries(categories ?? {}).map(
        ([categoryKey, category]) => {

          if (!category?.songs?.length) {
            return null;
          }

          return (
            <CardSection
              key={categoryKey}
              title={
                categoryTitles[categoryKey] ??
                categoryKey
              }
              variant="track"
              items={category.songs}
            />
          );
        }
      )}

    </div>
  );
};

export default Music;