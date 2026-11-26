import { Song } from "@/redux/features/playerSlice"
import OptionButtons from "./OptionButtons"
import PlayShuffle from "./PlayShuffle"

const ArtistHeaderButton = ({artist_uuid , songs}:{artist_uuid : string , songs:Song[]}) => {
  return (
    <div className="pr-4.5 h-10.5  flex justify-between">
     <OptionButtons artist_uuid={artist_uuid}/>
     <PlayShuffle songs={songs} />
    </div>
  )
}

export default ArtistHeaderButton