"use client";

import { Loader2 } from "lucide-react";
import FacebookIcon from "@/public/Icons/FacebookIcon";
import GoogleIcon from "@/public/Icons/GoogleIcon";
import AppleIcon2 from "@/public/Icons/AppleIcon2";
import { cn } from "@/utils/cn";
import {
  JSX,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import { useGoogleTokenLoginMutation } from "@/redux/services/authApiSlice";
import { useAppDispatch } from "@/redux/hook";
import { setAuth } from "@/redux/features/authSlice";
import useSpotifyRouter from "@/hooks/authhooks/useSpotifyRouter";

type Provider = "Google" | "Facebook" | "Apple";

interface OAuthButtonProps {
  readonly provider: Provider;
  readonly onClick?: () => void;
}

interface GoogleCredentialResponse {
  credential?: string;
}

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: {
            client_id: string;
            callback: (response: GoogleCredentialResponse) => void;
            auto_select?: boolean;
            cancel_on_tap_outside?: boolean;
            use_fedcm_for_prompt?: boolean;
            itp_support?: boolean;
          }) => void;
          renderButton: (
            parent: HTMLElement,
            options: Record<string, unknown>
          ) => void;
          cancel: () => void;
        };
      };
    };
  }
}

/* ---------------------------------------------
   لود کردن اسکریپت گوگل (Singleton)
--------------------------------------------- */
let googleScriptPromise: Promise<void> | null = null;

const loadGoogleScript = (): Promise<void> => {
  if (window.google?.accounts?.id) {
    return Promise.resolve();
  }

  if (googleScriptPromise) {
    return googleScriptPromise;
  }

  googleScriptPromise = new Promise((resolve, reject) => {
    const existing = document.querySelector(
      'script[src="https://accounts.google.com/gsi/client"]'
    ) as HTMLScriptElement | null;

    if (existing) {
      if (window.google?.accounts?.id) {
        resolve();
        return;
      }
      existing.addEventListener("load", () => resolve(), { once: true });
      existing.addEventListener(
        "error",
        () => reject(new Error("Google script failed to load")),
        { once: true }
      );
      return;
    }

    const script = document.createElement("script");
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.defer = true;
    script.onload = () => resolve();
    script.onerror = () =>
      reject(new Error("Google script failed to load"));
    document.head.appendChild(script);
  });

  return googleScriptPromise;
};

/* ---------------------------------------------
   تنظیمات آیکون‌ها
--------------------------------------------- */
const PROVIDER_CONFIG: Record<
  Provider,
  { icon: JSX.Element; className?: string }
> = {
  Google: { icon: <GoogleIcon />, className: "" },
  Facebook: { icon: <FacebookIcon />, className: "" },
  Apple: { icon: <AppleIcon2 />, className: "" },
};

/* ---------------------------------------------
   کامپوننت اصلی
--------------------------------------------- */
export const OAuthButton: React.FC<OAuthButtonProps> = ({
  provider,
  onClick,
}) => {
  const { icon, className = "" } = PROVIDER_CONFIG[provider];

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const dispatch = useAppDispatch();
  const { replace } = useSpotifyRouter();
  const [googleTokenLogin] = useGoogleTokenLoginMutation();

  const googleBtnRef = useRef<HTMLDivElement>(null);
  const googleInitialized = useRef(false);

  /* ---------------------------------------------
     هندل کردن توکن گوگل
  --------------------------------------------- */
  const handleGoogleCredential = useCallback(
    async (response: GoogleCredentialResponse) => {
      try {
        setLoading(true);
        setError(null);

        const googleIdToken = response.credential;
        if (!googleIdToken) {
          throw new Error("Google ID token دریافت نشد");
        }

        const result = await googleTokenLogin({
          id_token: googleIdToken,
        }).unwrap();

        const { access, refresh } = result;

        if (!access || !refresh) {
          throw new Error("توکن Milify دریافت نشد");
        }

        // ذخیره کوکی HttpOnly
        const cookieResponse = await fetch("/api/auth/set-token", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ access, refresh }),
        });

        if (!cookieResponse.ok) {
          throw new Error("ذخیره JWT در Cookie انجام نشد");
        }

        // LocalStorage
        localStorage.setItem("access", access);
        localStorage.setItem("refresh", refresh);

        // Redux
        dispatch(setAuth({ access, refresh }));

        // ریدایرکت
        replace("/browse");
      } catch (err) {
        console.error("Google → Milify login failed:", err);
        setError("ورود با گوگل ناموفق بود. لطفاً دوباره تلاش کنید.");
        setLoading(false);
      }
    },
    [dispatch, googleTokenLogin, replace]
  );

  /* ---------------------------------------------
     رندر کردن دکمه رسمی گوگل
  --------------------------------------------- */
  useEffect(() => {
    if (provider !== "Google") return;

    let cancelled = false;

    const initGoogleButton = async () => {
      try {
        await loadGoogleScript();

        if (cancelled || !window.google?.accounts?.id || !googleBtnRef.current) {
          return;
        }

        const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
        if (!clientId) {
          setError("NEXT_PUBLIC_GOOGLE_CLIENT_ID تعریف نشده");
          return;
        }

        // فقط یک بار initialize کن
        if (!googleInitialized.current) {
          window.google.accounts.id.initialize({
            client_id: clientId,
            callback: handleGoogleCredential,
            auto_select: false,
            cancel_on_tap_outside: true,
            use_fedcm_for_prompt: false, // مهم: FedCM رو خاموش می‌کنیم
            itp_support: true,
          });
          googleInitialized.current = true;
        }

        // رندر دکمه رسمی گوگل
        window.google.accounts.id.renderButton(googleBtnRef.current, {
          type: "standard",
          theme: "outline",
          size: "large",
          text: "continue_with",
          shape: "pill",
          logo_alignment: "left",
          width: "100%", // عرض کامل
        });
      } catch (err) {
        console.error("خطا در بارگذاری دکمه گوگل:", err);
        setError("خطا در بارگذاری سرویس گوگل");
      }
    };

    initGoogleButton();

    return () => {
      cancelled = true;
    };
  }, [provider, handleGoogleCredential]);

  /* ---------------------------------------------
     کلیک برای فیسبوک و اپل
  --------------------------------------------- */
  const handleClick = () => {
    if (provider !== "Google" && onClick) {
      onClick();
    }
  };

  /* ---------------------------------------------
     استایل پایه
  --------------------------------------------- */
  const baseClasses =
    "relative text-[rgba(255,255,255,0.9)] justify-center flex py-[12.5px] mt-2 rounded-[34px] focus:outline-none border border-[rgba(255,255,255,0.44)] text-[14px] w-full font-bold transform transition-transform duration-200 ease-in-out hover:scale-105 max-[360px]:text-[12px] items-center disabled:opacity-60 disabled:cursor-not-allowed";

  /* ---------------------------------------------
     رندر
  --------------------------------------------- */
  if (provider === "Google") {
    return (
      <div className="w-full">
        {/* کانتینر دکمه رسمی گوگل */}
        <div
          ref={googleBtnRef}
          className="w-full flex justify-center min-h-[48px]"
        />

        {/* لودینگ */}
        {loading && (
          <div className="mt-3 flex items-center justify-center gap-2 text-sm text-white/60">
            <Loader2 className="h-4 w-4 animate-spin text-green-500" />
            در حال ورود به میلِفای...
          </div>
        )}

        {/* ارور */}
        {error && (
          <p className="mt-2 text-center text-xs text-red-400">{error}</p>
        )}
      </div>
    );
  }

  // فیسبوک و اپل (دکمه سفارشی خودت)
  return (
    <>
      <button
        className={cn(baseClasses, className)}
        onClick={handleClick}
        type="button"
        disabled={loading}
      >
        <div className="absolute left-[32.5px] flex items-center">
          {icon}
        </div>
        <span>Continue with {provider}</span>
      </button>

      {error && (
        <p className="mt-2 text-center text-xs text-red-400">{error}</p>
      )}
    </>
  );
};