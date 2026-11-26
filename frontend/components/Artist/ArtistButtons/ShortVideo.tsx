import Image from "next/image";
import { Shorts } from "@/redux/services/artistApislice";
import { useEffect, useState } from "react";
import { useShortVideos } from "@/features/explore/hooks/useShortVideo";

interface ShortVideoProps {
  item: Shorts;
  i: number;
  onOpen: (i: number) => void;
  videos: Shorts[];
}

const ShortVideo = ({ item, onOpen, i }: ShortVideoProps) => {
  const { thumbnails, generateThumbnails } = useShortVideos();
  const uuid = item.uuid;
  const thumb = thumbnails[uuid] ;
  const [completedFor, setCompletedFor] = useState<string>();
  const isLoading = !thumb && completedFor !== uuid;

  useEffect(() => {
    if (thumb || completedFor === uuid) return;
    let current = true;
    const complete = () => { if (current) setCompletedFor(uuid); };
    void generateThumbnails([item]).then(complete, complete);
    return () => { current = false; };
  }, [uuid, thumb, item, generateThumbnails, completedFor]);

  return (
    <div
      className="h-45.75 relative flex justify-center cursor-pointer"
      onClick={() => onOpen(i)}
    >
      {isLoading ? (
        <div
          className="h-45.75 flex items-center justify-center rounded-[9px] bg-gray-300" 
          style={{ width: '107px' }} 
        >
          <p>Loading...</p> 
        </div>
      ) : (
        <Image
          width={107}
          height={183}
          src={thumb || "/images/placeholder-thumb.png"}
          className="h-45.75 overflow-hidden rounded-[9px] object-cover"
          alt={item.caption || "short video"}
          loading="lazy"
        />
      )}
      <p className="absolute bottom-2 font-bold text-[12px] text-white">
        {item.caption}
      </p>
    </div>
  );
};

export default ShortVideo;
