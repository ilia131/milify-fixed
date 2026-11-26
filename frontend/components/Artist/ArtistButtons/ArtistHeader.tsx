
import { Artist } from "@/redux/services/artistApislice"
import ArtistTabs from "../ArtistTabs/ArtistTabs"
import ArtistHeaderButton from "./ArtistHeaderbutton"
import ViewsMonthly from "./ViewsMonthly"
import { useDominantColorFromImage } from "@/shared/hooks/useDominantColorFromImage"
import { Song } from "@/redux/features/playerSlice"

const ArtistHeader = ({data , songs}:{data:Artist , songs:Song[]}) => {
   useDominantColorFromImage(data?.profile_pic ?? "");
  return (
    <div className="absolute inset-0 
     flex flex-col pl-4 pt-3 gap-3"
     >
      
         <ViewsMonthly monthly_listeners={data?.monthly_listeners} />
         <ArtistHeaderButton artist_uuid={data?.uuid} songs={songs} />
         <ArtistTabs />
    </div>
  )
}

export default ArtistHeader