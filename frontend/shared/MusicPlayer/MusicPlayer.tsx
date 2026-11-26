"use client";

import { useState } from "react";

import { useAppSelector } from "@/redux/hook";

import CoverMusicPlayer from "./CoverMusicPlayer/CoverMusicPlayer";
import MiniPlayer from "./MiniPlayer";
import QueueSheet from "./QueueSheet";

import {
  usePlayerUI,
} from "./context/playerUIContext";

import { useAudioPlayer } from "@/entities/artist/hooks/useAudioPlayer";

import AudioAd from "@/components/player/AudioAd";

const MusicPlayer = () => {
  const {
    isCoverOpen,
    openCover,
    closeCover,
  } = usePlayerUI();

  const [
    isOpenQueue,
    setIsOpenQueue,
  ] = useState(false);

  const {
    seekFromEvent,
    formatTime,

    handleNext,
    handlePrevious,

    showAd,
    currentAd,
    handleAdFinished,
  } = useAudioPlayer();

  const {
    progress,
    currentTime,
    duration,
    buffered,
    queue,
    currentIndex,
  } = useAppSelector(
    (state) => state.player
  );

  const currentSong =
    queue[currentIndex];

  return (
    <>
      {/* Mini Player */}

      <MiniPlayer
        currentSong={currentSong}
        progress={progress}
        onOpenCover={openCover}
      />

      {/* Full Player */}

      {isCoverOpen && (
        <div className="h-screen">
          <CoverMusicPlayer
            buffered={buffered}
            onClose={closeCover}
            currentSong={currentSong}
            progress={progress}
            lowerTime={formatTime(currentTime)}
            higherTime={formatTime(duration)}
            handleSeek={seekFromEvent}
            onNext={handleNext}
            onPrevious={handlePrevious}
            setIsOpenQueue={setIsOpenQueue}
          />
        </div>
      )}

      {/* Queue */}

      {isOpenQueue && (
        <QueueSheet
          onClose={() =>
            setIsOpenQueue(false)
          }
        />
      )}

      {/* Audio Ad */}

      {showAd && currentAd && (
        <AudioAd
          ad={currentAd}
          onFinished={handleAdFinished}
        />
      )}
    </>
  );
};

export default MusicPlayer;