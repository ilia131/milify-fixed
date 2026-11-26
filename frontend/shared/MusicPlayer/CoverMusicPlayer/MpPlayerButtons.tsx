import Shuffle from "@/public/Icons/Shuffle";
import BackButtonIcon from "@/public/Icons/BackButtonIcon";
import PauseCircle from "@/public/Icons/PauseCircle";
import NextButtonIcon from "@/public/Icons/NextButtonIcon";
import { Repeat1 } from "lucide-react";
import PlayCircle from "@/public/Icons/PlayCircle";

import {
  useAppDispatch,
  useAppSelector,
} from "@/redux/hook";

import {
  togglePlay,
  setVolume,
  toggleRepeatOne,
  toggleShuffle,
} from "@/redux/features/playerSlice";

const MpPlayerButtons = ({
  onNext,
  onPrevious
}: {
  onNext: () => void;
  onPrevious :  ()=>void

}) => {
  const dispatch = useAppDispatch();

  const {
    isPlaying,
    queue,
    shuffle,
    repeatOne,
    volume,
  } = useAppSelector(
    (state) => state.player
  );

  const disabled =
    queue.length === 0;

  return (
    <div>
    <div className="flex justify-between mt-2 mx-1 items-center">

      {/* Shuffle */}
      <button
        className="text-white"
        title="shuffle"
        aria-label="Shuffle"
        aria-pressed={shuffle}
        onClick={() => dispatch(toggleShuffle())}
        type="button"
        disabled={disabled}
      >
        <Shuffle />
      </button>

      {/* Previous */}
      <button
        type="button"
        disabled={disabled}
        onClick={onPrevious}
      >
        <BackButtonIcon />
      </button>

      {/* Play / Pause */}
      <button
        type="button"
        disabled={disabled}
        onClick={() => dispatch(togglePlay())}
      >
        {isPlaying ? (
          <PauseCircle />
        ) : (
          <PlayCircle />
        )}
      </button>

      {/* Next */}
      <button
        type="button"
        disabled={disabled}
        onClick={onNext}
      >
        <NextButtonIcon />
      </button>

      <button
        type="button"
        aria-label="Repeat current track"
        aria-pressed={repeatOne}
        onClick={() => dispatch(toggleRepeatOne())}
      >
        <Repeat1 size={20} />
      </button>
    </div>
    <label className="mt-2 flex items-center gap-2 text-xs">
      صدا
      <input
        aria-label="Volume"
        type="range"
        min="0"
        max="1"
        step="0.01"
        value={volume}
        onChange={(event) => dispatch(setVolume(event.currentTarget.valueAsNumber))}
      />
    </label>
    </div>
  );
};

export default MpPlayerButtons;