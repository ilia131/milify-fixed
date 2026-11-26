import { Artist } from "@/redux/services/artistApislice"
import CircleAvatar from "../CircleAvatar/CircleAvatar"
import Link from "next/link"

interface CircleCardProps {
    item:Artist ,
}



const AvatarCircleCard = ({item} : CircleCardProps ) => {
  return (
    <Link href={`/artist/${item.artistname ?? ""}`} className="grid h-44.25 w-35 justify-center gap-4 text-center" >
        <CircleAvatar item={item}  />
        <p className="text-[14px] text-[rgba(255_255_255/0.66)] font-600">{item.artistname}</p>
    </Link>
  )
}

export default AvatarCircleCard