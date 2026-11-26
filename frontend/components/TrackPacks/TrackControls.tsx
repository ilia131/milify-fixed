"use client";

import { useState } from "react";

import ThreeDots from "@/components/Artist/ArtistButtons/ThreeDots";
import LoginRequiredAlert from "@/components/LoginRequiredAlert/LoginRequiredAlert";

import BarMusicPlayer from "@/shared/MusicPlayer/CoverMusicPlayer/BarMusicPlayer";
import CirclePlay from "@/public/Icons/CirclePlay";
import TimeNumber from "@/shared/MusicPlayer/CoverMusicPlayer/TimeNumber";

import { Song } from "@/redux/features/playerSlice";
import { useAppDispatch, useAppSelector } from "@/redux/hook";
import { openBottomSheet } from "@/redux/features/bottomSheet";

interface TrackControlsProps {
  progress: number;
  duration: string;
  item: Song;
}

const TrackControls = ({
  progress,
  duration,
  item,
}: TrackControlsProps) => {
  const dispatch = useAppDispatch();

  const [showLoginAlert, setShowLoginAlert] = useState(false);

  const isAuthenticated = useAppSelector(
    (state) => state.auth.isAuthenticated
  );

  const handleThreeDotsClick = () => {
    dispatch(openBottomSheet(item));
  };

  return (
    <>
      <div className="mt-2.25 flex w-51.5 items-center justify-between">
        <div className="mt-3 grid gap-1">
          <div className="h-1 w-29.75 rounded-[1px] bg-[rgba(255,255,255,0.5)]">
            <BarMusicPlayer progress={progress} />
          </div>

          <div className="flex w-full justify-between text-[7px]">
            <TimeNumber timenumber="0:00" />
            <TimeNumber timenumber={duration} />
          </div>
        </div>

        <div className="flex w-18.25 items-center justify-between">
          <ThreeDots
            isAuthenticated={isAuthenticated}
            onRequireLogin={() => {
              setShowLoginAlert(true);
            }}
            onClick={handleThreeDotsClick}
          />

          <CirclePlay
            stroke="none"
            className="h-8 w-8"
          />
        </div>
      </div>

      {showLoginAlert && (
        <LoginRequiredAlert
          open={showLoginAlert}
          onClose={() => setShowLoginAlert(false)}
        />
      )}
    </>
  );
};

export default TrackControls;