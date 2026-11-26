import {
  ListMusic,
} from "lucide-react";

import ShareIcon from "@/public/Icons/ShareIcon";

const ShareCastMp = ({
  setIsOpenLyric,
  setIsOpenQueue,
}: {
  setIsOpenLyric: (isOpenLyric: boolean) => void;
  setIsOpenQueue: (isOpenQueue: boolean) => void;
}) => {
  return (
    <div
      className="
        mt-14.25
        flex
        items-center
        justify-between
        px-1
        [@media(max-height:800px)]:mt-10
      "
    >
      {/* Share */}

      {/* <button
        type="button"
        className="
          flex
          h-10
          w-10
          items-center
          justify-center
          rounded-full
          transition
          hover:bg-white/10
          active:scale-90
        "
      >
        <ShareIcon />
      </button> */}

      {/* Lyrics */}

      <button
        type="button"
        onClick={() => setIsOpenLyric(true)}
        className="
          group
          flex
          items-center
          gap-2
          rounded-full
          px-4
          py-2
          text-sm
          font-semibold
          text-white
          transition
          hover:bg-white/10
          active:scale-95
        "
      >
        <span>
          Lyrics
        </span>

        <span
          className="
            h-1.5
            w-1.5
            rounded-full
            bg-[#1ed760]
            opacity-0
            transition
            group-hover:opacity-100
          "
        />
      </button>

      {/* Queue */}

      <button
        type="button"
        onClick={() => setIsOpenQueue(true)}
        aria-label="Open queue"
        className="
          flex
          h-10
          w-10
          items-center
          justify-center
          rounded-full
          text-white
          transition
          hover:bg-white/10
          active:scale-90
        "
      >
        <ListMusic size={22} />
      </button>
    </div>
  );
};

export default ShareCastMp;