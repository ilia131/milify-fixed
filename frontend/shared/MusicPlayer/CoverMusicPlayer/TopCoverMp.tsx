"use client";

import { useState } from "react";

import DownArrow from "@/public/Icons/DownArrow";
import ThreeCirlceFlex from "@/public/Icons/ThreeCircleFlex";

import { useAppDispatch, useAppSelector } from "@/redux/hook";
import { openBottomSheet } from "@/redux/features/bottomSheet";

import { Song } from "@/redux/features/playerSlice";

import LoginRequiredAlert from "@/components/LoginRequiredAlert/LoginRequiredAlert";

interface Props {
  onClose: () => void;
  currentSong: Song;
}

const TopCoverMp = ({ onClose, currentSong }: Props) => {
  const dispatch = useAppDispatch();

  const [showLoginAlert, setShowLoginAlert] = useState(false);

  const isAuthenticated = useAppSelector(
    (state) => state.auth.isAuthenticated
  );

  const handleOpenOptions = () => {
    if (!isAuthenticated) {
      setShowLoginAlert(true);
      return;
    }

    dispatch(openBottomSheet(currentSong));
  };

  return (
    <>
      <div
        className="
          relative
          top-[5%]
          flex
          items-center
          justify-between
          pt-[calc(env(safe-area-inset-top)+12px)]
        "
      >
        <DownArrow
          onClick={onClose}
          fill="white"
          fillOpacity="0.62"
        />

        <ThreeCirlceFlex
          onClick={handleOpenOptions}
        />
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

export default TopCoverMp;