"use client";

interface ReelInfoProps {
  username?: string;
  caption?: string;
}

const ReelInfo = ({
  username,
  caption,
}: ReelInfoProps) => {
  if (!username && !caption) {
    return null;
  }

  return (
    <div
      className="
        absolute
        left-4
        right-20
        z-20
        text-white
      "
      style={{
        bottom:
          "calc(env(safe-area-inset-bottom, 0px) + 5rem)",
      }}
    >
      {username && (
        <div className="flex items-center gap-2">
          <p className="text-[14px] font-bold">
            @{username}
          </p>
        </div>
      )}

      {caption && (
        <p
          className="
            mt-2
            max-w-[90%]
            text-[13px]
            leading-5
            text-white/95
          "
        >
          {caption}
        </p>
      )}
    </div>
  );
};

export default ReelInfo;