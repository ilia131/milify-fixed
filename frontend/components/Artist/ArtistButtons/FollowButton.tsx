"use client";

import { useState } from "react";

import {
  useFollowArtistMutation,
  useIsFollowingQuery,
} from "@/redux/services/followApiSlice";

import { useLanguage } from "@/i18n/LanguageProvider";
import { useAppSelector } from "@/redux/hook";

import LoginRequiredAlert from "@/components/LoginRequiredAlert/LoginRequiredAlert";

interface FollowButtonProps {
  artistUuid: string;
}

const FollowButton = ({
  artistUuid,
}: FollowButtonProps) => {
  const { t } = useLanguage();

  const [pending, setPending] = useState(false);
  const [showLoginAlert, setShowLoginAlert] = useState(false);

  // ==========================================
  // AUTH
  // ==========================================

  const isAuthenticated = useAppSelector(
    (state) => state.auth.isAuthenticated
  );

  const initialLoadFinished = useAppSelector(
    (state) => state.auth.initialLoadFinished
  );

  // ==========================================
  // FOLLOW STATUS
  // ==========================================

  const {
    data,
    refetch,
  } = useIsFollowingQuery(artistUuid, {
    skip:
      !artistUuid ||
      !initialLoadFinished ||
      !isAuthenticated,
  });

  // ==========================================
  // FOLLOW MUTATION
  // ==========================================

  const [
    followArtist,
    { isLoading },
  ] = useFollowArtistMutation();

  // ==========================================
  // FOLLOW CLICK
  // ==========================================

  const handleFollowClick = async () => {
    // ----------------------------------------
    // AUTH IS STILL INITIALIZING
    // ----------------------------------------

    if (!initialLoadFinished) {
      return;
    }

    // ----------------------------------------
    // GUEST
    // ----------------------------------------

    if (!isAuthenticated) {
      setShowLoginAlert(true);
      return;
    }

    // ----------------------------------------
    // PREVENT DOUBLE CLICK
    // ----------------------------------------

    if (pending || isLoading) {
      return;
    }

    setPending(true);

    try {
      await followArtist(artistUuid).unwrap();

      await refetch();
    } catch (error) {
      console.error(
        "❌ Follow artist error:",
        error
      );
    } finally {
      setPending(false);
    }
  };

  // ==========================================
  // STATUS
  // ==========================================

  const isFollowing =
    data?.is_following ?? false;

  const loading =
    pending || isLoading;

  // ==========================================
  // UI
  // ==========================================

  return (
    <>
      <button
        type="button"
        onClick={handleFollowClick}
        disabled={loading}
        className="
          w-20.5
          h-9
          border
          border-solid
          rounded-[17px]
          border-[rgba(255,255,255,0.42)]
          text-[rgba(255,255,255,0.79)]
          hover:border-white
          hover:text-white
          text-[12.8px]
          font-bold
          flex
          justify-center
          items-center
          transition-all
          duration-200
          disabled:opacity-50
          disabled:cursor-not-allowed
        "
      >
        {loading ? (
          <div
            className="
              w-4
              h-4
              border-2
              border-white/30
              border-t-white
              rounded-full
              animate-spin
            "
          />
        ) : isFollowing ? (
          t("artist.following")
        ) : (
          t("artist.follow")
        )}
      </button>

      <LoginRequiredAlert
        open={showLoginAlert}
        onClose={() => setShowLoginAlert(false)}
        title="Login to follow"
        message="Sign in to follow artists and save them to your library."
      />
    </>
  );
};

export default FollowButton;