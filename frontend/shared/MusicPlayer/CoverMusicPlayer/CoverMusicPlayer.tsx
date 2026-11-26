import CoverMpLayout from "./CoverMpLayout"
import { Song } from "@/redux/features/playerSlice";
interface Props {
  onClose: () => void;
  progress: number;
  currentSong:Song;
  lowerTime:string, 
  higherTime:string
  handleSeek:(e: React.MouseEvent<HTMLDivElement>) => void
  buffered:number
  onNext: ()=>void;
  onPrevious  : ()=>void;
  setIsOpenQueue:(isOpenQueue:boolean)=>void
  
}

const CoverMusicPlayer = ({ 
  onClose , 
  progress , 
  currentSong , 
  lowerTime , 
  higherTime,
  handleSeek,
  buffered,
  onNext,
  onPrevious ,
  setIsOpenQueue

}: Props) => { 
   return <CoverMpLayout
          buffered={buffered} 
          onClose={onClose} 
          progress={progress} 
          onPrevious={onPrevious}
          currentSong={currentSong} 
          higherTime={higherTime} 
          setIsOpenQueue={setIsOpenQueue}

          lowerTime={lowerTime} 
          handleSeek={handleSeek}
          onNext={onNext}
          />
}

export default CoverMusicPlayer
