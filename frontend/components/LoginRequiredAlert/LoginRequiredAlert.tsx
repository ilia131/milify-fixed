"use client";

import { useRouter } from "next/navigation";
import { useAppDispatch, useAppSelector } from "@/redux/hook";
import { togglePlay } from "@/redux/features/playerSlice";

interface LoginRequiredAlertProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  message?: string;
}

const LoginRequiredAlert = ({
  open,
  onClose,
  title = "Login required",
  message = "Please log in to access this option.",
}: LoginRequiredAlertProps) => {
  const router = useRouter();
  const dispatch = useAppDispatch();

  const isPlaying = useAppSelector(
    (state) => state.player.isPlaying
  );

  if (!open) return null;

  const handleLogin = () => {
    // Stop music before navigating to login
    if (isPlaying) {
      dispatch(togglePlay());
    }

    onClose();

    router.push("/auth/login");
  };

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60 px-4">
      <div className="w-full max-w-sm rounded-2xl bg-[#181818] p-5 text-white shadow-2xl">
        <h2 className="text-lg font-semibold">
          {title}
        </h2>

        <p className="mt-2 text-sm text-white/60">
          {message}
        </p>

        <div className="mt-5 flex gap-2">
          <button
            type="button"
            onClick={onClose}
            className="
              flex-1
              rounded-xl
              bg-white/10
              py-2.5
              text-sm
              text-white
              transition
              hover:bg-white/15
            "
          >
            Maybe later
          </button>

          <button
            type="button"
            onClick={handleLogin}
            className="
              flex-1
              rounded-xl
              bg-white
              py-2.5
              text-sm
              font-medium
              text-black
              transition
              hover:bg-white/90
            "
          >
            Log in
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginRequiredAlert;