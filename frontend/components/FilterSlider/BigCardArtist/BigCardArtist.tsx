import Image from "next/image";
import {
  Song,
  playSingleSong,
  togglePlay,
} from "@/redux/features/playerSlice";
import CardHeader from "./CardHeader";
import BottomBigArtist from "./BottomBigArtist";
import {
  useAppDispatch,
  useAppSelector,
} from "@/redux/hook";
import { useRouter } from "next/navigation";

export interface ItemArtistProps {
  item: ItemsBigProps;
}

export interface ItemsBigProps {
  name: string;
  pic: string;
  bg: string;
  firstTrack?: Song;
  album_name?: string;
}

const BigCardArtist = ({
  item,
}: ItemArtistProps) => {
  const router = useRouter();

  const dispatch = useAppDispatch();

  const {
    isPlaying,
    currentSong,
  } = useAppSelector(
    (state) => state.player
  );

  const isThisActive =
    isPlaying &&
    currentSong?.unique_id ===
      item.firstTrack?.unique_id;

  const handleToggle = (
    e: React.MouseEvent
  ) => {
    e.stopPropagation();

    if (isThisActive) {
      dispatch(togglePlay());
    } else if (item.firstTrack) {
      dispatch(
        playSingleSong(item.firstTrack)
      );
    }
  };

  const handleCardClick = () => {
    // اگر آلبوم دارد → صفحه آلبوم
    if (
      item.album_name &&
      item.album_name.trim()
    ) {
      router.push(
        `/album/${encodeURIComponent(
          item.name
        )}/${encodeURIComponent(
          item.album_name
        )}`
      );

      return;
    }

    // اگر آلبوم ندارد → صفحه آرتیست
    router.push(
      `/artist/${encodeURIComponent(
        item.name
      )}`
    );
  };

  return (
    <div
      className="flex justify-start pr-4"
      onClick={handleCardClick}
    >
      <div className="flex flex-col gap-y-2.25 pt-8.75">
        <div className="relative z-2 h-110.25 shrink-0 overflow-hidden">
          <CardHeader
            coverSrc={item.pic}
            title={item.name}
            subtitle={
              item.album_name
                ? "Album · Milify"
                : "Artist · Milify"
            }
          />

          <Image
            src={item.bg}
            alt="Big music cover"
            width={358}
            height={441}
            className="
              z-2
              h-110.25
              w-110
              rounded-3xl
              object-cover
            "
            unoptimized
          />

          <p
            className="
              absolute
              bottom-18.5
              left-4
              z-2
              h-4.5
              w-58.75
              text-[12px]
              text-[rgba(255_255_255/0.60)]
            "
          >
            Pass the sticks & Press Play.
          </p>

          <div className="absolute bottom-4.75 left-4 right-4">
            <BottomBigArtist
              isPlaying={isThisActive}
              onTogglePlay={handleToggle}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default BigCardArtist;