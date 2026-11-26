

import { Artist } from "@/redux/services/artistApislice"
import ArtistHeader from "./ArtistHeader"
import BackgroundLayers from "./BackgroundLayers"
import { useDominantColorFromImage } from "@/shared/hooks/useDominantColorFromImage";
import { Song } from "@/redux/features/playerSlice";



const ArtistButtons = ({data , songs}:{data : Artist , songs:Song[]}) => {
  const dominantColor = useDominantColorFromImage(data?.profile_pic ?? "");

  return (
    <div className="absolute bottom-0 w-full h-37">
      <BackgroundLayers image={data?.profile_pic} />
      <ArtistHeader data={data} songs={songs}/>
    </div>
  )
}

export default ArtistButtons