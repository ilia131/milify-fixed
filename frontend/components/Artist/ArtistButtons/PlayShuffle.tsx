"use client";

import {
  setQueue,
  togglePlay,
  Song,
} from "@/redux/features/playerSlice";
import { useAppDispatch, useAppSelector } from "@/redux/hook";

import ShuffleButton from "./ShuffleButton";
import PlayGreenButton from "./PlayGreenButton";

interface PlayShuffleProps {
  songs: Song[];
}

const PlayShuffle = ({ songs }: PlayShuffleProps) => {
  const dispatch = useAppDispatch();

  const { queue, isPlaying } = useAppSelector(
    (state) => state.player
  );

  const isSameQueue =
    queue.length === songs?.length &&
    songs.every((song) =>
      queue.some((q) => q.id === song.id)
    );

  const handlePlay = () => {
    if (!songs.length) return;

    if (isSameQueue) {
      dispatch(togglePlay());
      return;
    }

    dispatch(
      setQueue({
        songs,
        startIndex: 0,
      })
    );
  };

  const handleShuffle = () => {
    if (!songs.length) return;

    const shuffled = [...songs].sort(
      () => Math.random() - 0.5
    );

    dispatch(
      setQueue({
        songs: shuffled,
        startIndex: 0,
      })
    );
  };

  return (
    <div className="flex h-13 w-23 items-center justify-between">
      <ShuffleButton onShuffle={handleShuffle} />

      <PlayGreenButton
        onPlay={handlePlay}
        isPlaying={isSameQueue && isPlaying}
      />
    </div>
  );
};

export default PlayShuffle;