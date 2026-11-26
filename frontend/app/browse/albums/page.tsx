"use client";

import BeatCard from "@/entities/beats/ui/BeatsCard/BeatCard";
import BeatCardSkeleton from "@/entities/beats/ui/BeatCardSkeleton";
import { useGetBeatsQuery } from "@/redux/services/producerApiSlice";

const Beats = () => {
  const {
    data,
    isLoading,
    isError,
  } = useGetBeatsQuery();

  if (isLoading) {
    return (
      <div className="w-full px-3.75 pt-22 flex flex-col gap-4 pb-40">
        {Array.from({ length: 6 }).map((_, index) => (
          <BeatCardSkeleton key={index} />
        ))}
      </div>
    );
  }

  if (isError) {
    return (
      <div className="w-full px-4 pt-22 text-red-400">
        Error loading beats
      </div>
    );
  }

  return (
    <div className="w-full px-3.75 pt-22 flex flex-col gap-4 pb-40">
      {data?.map((beat) => (
        <BeatCard
          key={beat.id}
          beat={beat}
        />
      ))}
    </div>
  );
};

export default Beats;