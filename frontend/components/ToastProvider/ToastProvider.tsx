"use client";

import {
  createContext,
  useCallback,
  useContext,
  useState,
  ReactNode,
} from "react";

type ToastType = "success" | "error" | "info" | "warning";

interface ToastItem {
  id: number;
  type: ToastType;
  message: string;
  duration: number;
}

interface ToastContextType {
  showToast: (
    message: string,
    type?: ToastType,
    duration?: number
  ) => void;

  success: (message: string) => void;
  error: (message: string) => void;
  info: (message: string) => void;
  warning: (message: string) => void;
}

const ToastContext =
  createContext<ToastContextType | null>(null);

export function ToastProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [toasts, setToasts] = useState<ToastItem[]>(
    []
  );

  const removeToast = useCallback((id: number) => {
    setToasts((prev) =>
      prev.filter((toast) => toast.id !== id)
    );
  }, []);

  const showToast = useCallback(
    (
      message: string,
      type: ToastType = "info",
      duration = 3000
    ) => {
      const id = Date.now() + Math.random();

      setToasts((prev) => [
        ...prev,
        {
          id,
          type,
          message,
          duration,
        },
      ]);

      setTimeout(() => {
        removeToast(id);
      }, duration);
    },
    [removeToast]
  );

  const success = useCallback(
    (message: string) =>
      showToast(message, "success"),
    [showToast]
  );

  const error = useCallback(
    (message: string) =>
      showToast(message, "error"),
    [showToast]
  );

  const info = useCallback(
    (message: string) =>
      showToast(message, "info"),
    [showToast]
  );

  const warning = useCallback(
    (message: string) =>
      showToast(message, "warning"),
    [showToast]
  );

  return (
    <ToastContext.Provider
      value={{
        showToast,
        success,
        error,
        info,
        warning,
      }}
    >
      {children}

      <div
        className="
          fixed
          top-5
          right-5
          z-[99999]
          flex
          w-[min(380px,calc(100vw-32px))]
          flex-col
          gap-3
          pointer-events-none
        "
      >
        {toasts.map((toast) => (
          <Toast
            key={toast.id}
            toast={toast}
            onClose={() =>
              removeToast(toast.id)
            }
          />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

function Toast({
  toast,
  onClose,
}: {
  toast: ToastItem;
  onClose: () => void;
}) {
  const config = {
    success: {
      icon: "✓",
      title: "Success",
    },
    error: {
      icon: "!",
      title: "Error",
    },
    warning: {
      icon: "!",
      title: "Warning",
    },
    info: {
      icon: "i",
      title: "Info",
    },
  };

  const current = config[toast.type];

  return (
    <div
      role="alert"
      className="
        pointer-events-auto
        relative
        overflow-hidden
        rounded-2xl
        border
        border-white/10
        bg-[#181818]/95
        p-4
        text-white
        shadow-2xl
        backdrop-blur-xl
        animate-[toastIn_.3s_ease-out]
      "
    >
      <div className="flex items-start gap-3">
        <div
          className="
            flex
            h-9
            w-9
            shrink-0
            items-center
            justify-center
            rounded-full
            bg-white/10
            text-sm
            font-bold
          "
        >
          {current.icon}
        </div>

        <div className="min-w-0 flex-1">
          <p className="text-sm font-bold">
            {current.title}
          </p>

          <p className="mt-1 break-words text-sm text-zinc-400">
            {toast.message}
          </p>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="
            text-zinc-500
            transition
            hover:text-white
          "
          aria-label="Close notification"
        >
          ×
        </button>
      </div>

      <div
        className="
          absolute
          bottom-0
          left-0
          h-[2px]
          w-full
          origin-left
          bg-white/30
        "
        style={{
          animation: `toastProgress ${toast.duration}ms linear forwards`,
        }}
      />
    </div>
  );
}

export function useToast() {
  const context = useContext(ToastContext);

  if (!context) {
    throw new Error(
      "useToast must be used inside ToastProvider"
    );
  }

  return context;
}