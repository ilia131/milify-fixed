"use client";

import ThreeDots from "../ArtistButtons/ThreeDots";
import TitleMusicCard from "./TitleMusicCard";
import ViewMusicCard from "./ViewMusicCard";
import { Song } from "@/redux/features/playerSlice";
import { useAppDispatch, useAppSelector } from "@/redux/hook";
import { openBottomSheet } from "@/redux/features/bottomSheet";
import { useRemoveTrackFromPlaylistMutation } from "@/redux/services/playlistApiSlice";
import { useState } from "react";
import LoginRequiredAlert from "@/components/LoginRequiredAlert/LoginRequiredAlert";

interface ItemProps {
  item: Song;
  isPlaylistView?: boolean;
  playlistId?: string;
}

const OptionCardMusic = ({
  item,
  isPlaylistView,
  playlistId,
}: ItemProps) => {
  const dispatch = useAppDispatch();

  const [showLoginAlert, setShowLoginAlert] = useState(false);

  const isAuthenticated = useAppSelector(
    (state) => state.auth.isAuthenticated
  );

  const [removeTrackFromPlaylist, { isLoading: isRemoving }] =
    useRemoveTrackFromPlaylistMutation();

  const handleRemove = async (
    e: React.MouseEvent<HTMLButtonElement>
  ) => {
    e.stopPropagation();

    if (!playlistId) return;

    try {
      await removeTrackFromPlaylist({
        playlistId,
        song_uuid: item.unique_id,
      }).unwrap();
    } catch (err) {
      console.error("Failed to remove track:", err);
    }
  };

  const handleThreeDotsClick = (
    e: React.MouseEvent<HTMLDivElement>
  ) => {
    e.stopPropagation();

    dispatch(openBottomSheet(item));
  };

  return (
    <>
      <div className="flex h-9.75 flex-1 justify-between">
        <div className="grid h-9.75 items-center justify-start text-left">
          <TitleMusicCard title={item.title} />
          <ViewMusicCard countview={item.play_count} />
        </div>

        <div className="flex items-center gap-2">
          {isPlaylistView ? (
            <button
              onClick={handleRemove}
              disabled={isRemoving}
              aria-label="Remove from playlist"
              title="Remove from playlist"
              className="
                flex min-h-6 min-w-6
                h-6 w-6
                items-center justify-center
                rounded-full
                border border-white/55
                text-white/80
                transition
                duration-150
                hover:border-white
                hover:text-white
                disabled:opacity-40
              "
            >
              <div className="h-[1.5px] w-2.5 rounded-full bg-current" />
            </button>
          ) : (
            <ThreeDots
              isAuthenticated={isAuthenticated}
              onRequireLogin={() => {
                setShowLoginAlert(true);
              }}
              onClick={handleThreeDotsClick}
            />
          )}
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

export default OptionCardMusic;