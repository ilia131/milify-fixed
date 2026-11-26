"use client";

import { SendHorizontal } from "lucide-react";

interface CommentInputProps {
  value: string;
  disabled?: boolean;

  onChange: (value: string) => void;
  onSubmit: () => void;
}

const CommentInput = ({
  value,
  disabled = false,
  onChange,
  onSubmit,
}: CommentInputProps) => {
  return (
    <div
      className="
        border-t
        border-white/10
        px-3
        py-3
      "
    >
      <div
        className="
          flex
          items-center
          gap-2
          rounded-full
          bg-white/[0.07]
          px-3
          py-1.5
        "
      >
        <input
          type="text"
          value={value}
          onChange={(e) =>
            onChange(e.target.value)
          }
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              onSubmit();
            }
          }}
          disabled={disabled}
          placeholder="Add a comment..."
          className="
            min-w-0
            flex-1
            bg-transparent
            py-2
            text-[13px]
            text-white
            outline-none
            placeholder:text-white/35
            disabled:opacity-50
          "
        />

        <button
          type="button"
          disabled={
            !value.trim() || disabled
          }
          onClick={onSubmit}
          className="
            flex
            h-9
            w-9
            shrink-0
            items-center
            justify-center
            rounded-full
            text-purple-400
            transition
            active:scale-75
            disabled:opacity-30
          "
        >
          <SendHorizontal size={19} />
        </button>
      </div>
    </div>
  );
};

export default CommentInput;