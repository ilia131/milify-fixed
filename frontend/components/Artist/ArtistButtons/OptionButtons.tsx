
import FollowButton from "./FollowButton"
import IconShortClip from "./IconShortClip"
import ThreeDots from "./ThreeDots"

const OptionButtons = ({artist_uuid}:{artist_uuid:string}) => {
  return (
    <div className="w-43.25 flex justify-between  items-center">
     <IconShortClip />
     <FollowButton artistUuid={artist_uuid} />
     <div className="w-4.75 flex justify-center items-center">
   
    </div>  </div>
  )
}

export default OptionButtons