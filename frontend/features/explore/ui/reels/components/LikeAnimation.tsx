"use client";

import { Heart } from "lucide-react";

interface LikeAnimationProps {
  visible: boolean;
}

const LikeAnimation = ({
  visible,
}: LikeAnimationProps) => {
  if (!visible) return null;

  return (
    <div
      className="
        pointer-events-none
        absolute
        inset-0
        z-40
        flex
        items-center
        justify-center
      "
    >
      <Heart
        size={110}
        fill="white"
        strokeWidth={0}
        className="
          animate-[ping_0.7s_ease-out]
          drop-shadow-[0_4px_20px_rgba(0,0,0,0.4)]
        "
      />
    </div>
  );
};

export default LikeAnimation;