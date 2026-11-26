"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import Image from "next/image";

import {
  useGoogleTokenLoginMutation,
  useCompleteGoogleProfileMutation,
} from "@/redux/services/authApiSlice";

import { useGetArtistsListQuery } from "@/redux/services/artistApislice";

import { useAppDispatch } from "@/redux/hook";
import { setAuth } from "@/redux/features/authSlice";

import useSpotifyRouter from "@/hooks/authhooks/useSpotifyRouter";

// =====================================================
// TYPES
// =====================================================

interface GoogleCredentialResponse {
  credential?: string;
  select_by?: string;
}

interface Artist {
  id: number;
  artistname: string;
  profile_pic?: string | null;
}

// =====================================================
// COMPONENT
// =====================================================

export default function GoogleCallbackPage() {
  const dispatch = useAppDispatch();
  const { replace } = useSpotifyRouter();

  const [googleTokenLogin, { isLoading: isGoogleLoading }] =
    useGoogleTokenLoginMutation();

  const [completeGoogleProfile, { isLoading: isCompletingProfile }] =
    useCompleteGoogleProfileMutation();

  const {
    data: artistsData,
    isLoading: isArtistsLoading,
    isError: isArtistsError,
  } = useGetArtistsListQuery(0);

  const artists: Artist[] =
    artistsData?.results ?? artistsData ?? [];

  const [showArtistSelection, setShowArtistSelection] = useState(false);
  const [selectedArtists, setSelectedArtists] = useState<string[]>([]);
  const [artistQuery, setArtistQuery] = useState("");

  const processed = useRef(false);
  const initialized = useRef(false);

  // =====================================================
  // TOGGLE ARTIST
  // =====================================================
  const toggleArtist = useCallback((artistName: string) => {
    setSelectedArtists((current) => {
      if (current.includes(artistName)) {
        return current.filter((name) => name !== artistName);
      }
      return [...current, artistName];
    });
  }, []);

  // =====================================================
  // FILTER ARTISTS
  // =====================================================
  const filteredArtists = artists.filter((artist) =>
    artist.artistname.toLowerCase().includes(artistQuery.toLowerCase())
  );

  // =====================================================
  // COMPLETE PROFILE
  // =====================================================
  const handleCompleteProfile = useCallback(async () => {
    if (selectedArtists.length === 0) return;

    try {
      await completeGoogleProfile({
        favorite_artists: selectedArtists,
      }).unwrap();

      replace("/browse");
    } catch (err) {
      console.error("Google profile completion failed:", err);
    }
  }, [completeGoogleProfile, selectedArtists, replace]);

  // =====================================================
  // GOOGLE SUCCESS
  // =====================================================
  const handleGoogleSuccess = useCallback(
    async (credentialResponse: GoogleCredentialResponse) => {
      if (processed.current) return;
      processed.current = true;

      try {
        const googleIdToken = credentialResponse?.credential;

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

        // ذخیره کوکی
        const cookieResponse = await fetch("/api/auth/set-token", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
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

        // نمایش انتخاب هنرمند
        setShowArtistSelection(true);
      } catch (err) {
        console.error("Google → Milify login failed:", err);
        processed.current = false;
      }
    },
    [dispatch, googleTokenLogin]
  );

  // =====================================================
  // INITIALIZE GOOGLE
  // =====================================================
  const initializeGoogle = useCallback(() => {
    const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

    if (!clientId) {
      console.error("NEXT_PUBLIC_GOOGLE_CLIENT_ID is not defined");
      return;
    }

    if (!window.google?.accounts?.id) {
      console.error("Google Identity Services not loaded");
      return;
    }

    if (initialized.current) return;
    initialized.current = true;

    window.google.accounts.id.initialize({
      client_id: clientId,
      callback: handleGoogleSuccess,
      auto_select: true,
      cancel_on_tap_outside: false,
      use_fedcm_for_prompt: false,
      itp_support: true,
    });

    // استفاده از any برای دور زدن مشکل تایپ
    (window.google.accounts.id as any).prompt();
  }, [handleGoogleSuccess]);

  // =====================================================
  // LOAD GOOGLE SCRIPT
  // =====================================================
  useEffect(() => {
    const GOOGLE_SCRIPT = "https://accounts.google.com/gsi/client";

    const existingScript = document.querySelector(
      `script[src="${GOOGLE_SCRIPT}"]`
    ) as HTMLScriptElement | null;

    if (window.google?.accounts?.id) {
      initializeGoogle();
      return;
    }

    if (existingScript) {
      const handleLoad = () => {
        initializeGoogle();
      };

      existingScript.addEventListener("load", handleLoad);

      return () => {
        existingScript.removeEventListener("load", handleLoad);
        if (window.google?.accounts?.id) {
          (window.google.accounts.id as any).cancel?.();
        }
      };
    }

    const script = document.createElement("script");
    script.src = GOOGLE_SCRIPT;
    script.async = true;
    script.defer = true;

    script.onload = () => {
      initializeGoogle();
    };

    script.onerror = () => {
      console.error("Failed to load Google Identity Services");
    };

    document.head.appendChild(script);

    return () => {
      if (window.google?.accounts?.id) {
        (window.google.accounts.id as any).cancel?.();
      }
    };
  }, [initializeGoogle]);

  // =====================================================
  // ARTIST SELECTION UI
  // =====================================================
  if (showArtistSelection) {
    return (
      <main dir="rtl" className="min-h-screen bg-black text-white">
        <div className="mx-auto flex min-h-screen w-full max-w-md flex-col px-5 py-8">
          <div className="mb-6">
            <h1 className="text-2xl font-bold">هنرمندهای مورد علاقه‌ات</h1>
            <p className="mt-2 text-sm text-white/50">
              چند هنرمند انتخاب کن تا تجربه موسیقی Milify برایت شخصی‌تر شود.
            </p>
          </div>

          <div className="mb-5">
            <input
              type="text"
              value={artistQuery}
              onChange={(event) => setArtistQuery(event.target.value)}
              placeholder="جستجوی هنرمند..."
              className="h-12 w-full rounded-xl border border-white/10 bg-white/5 px-4 text-sm text-white outline-none placeholder:text-white/30 focus:border-green-500/50"
            />
          </div>

          <div className="mb-4 flex items-center justify-between">
            <span className="text-sm text-white/50">
              {selectedArtists.length} هنرمند انتخاب شده
            </span>

            {selectedArtists.length > 0 && (
              <button
                type="button"
                onClick={() => setSelectedArtists([])}
                className="text-xs text-white/40 transition hover:text-white"
              >
                پاک کردن
              </button>
            )}
          </div>

          {isArtistsLoading ? (
            <div className="flex flex-1 items-center justify-center">
              <p className="text-sm text-white/50">در حال دریافت هنرمندان...</p>
            </div>
          ) : isArtistsError ? (
            <div className="flex flex-1 items-center justify-center">
              <p className="text-sm text-red-400">
                دریافت هنرمندان با خطا مواجه شد.
              </p>
            </div>
          ) : filteredArtists.length === 0 ? (
            <div className="flex flex-1 items-center justify-center">
              <p className="text-sm text-white/40">هنرمندی پیدا نشد.</p>
            </div>
          ) : (
            <div className="grid grid-cols-3 gap-x-4 gap-y-7 overflow-y-auto pb-28">
              {filteredArtists.map((artist) => {
                const selected = selectedArtists.includes(artist.artistname);

                return (
                  <button
                    key={artist.id}
                    type="button"
                    onClick={() => toggleArtist(artist.artistname)}
                    className="group flex min-w-0 flex-col items-center"
                  >
                    <div className="relative aspect-square h-24 w-24">
                      <Image
                        src={artist.profile_pic || "/artist-placeholder.jpg"}
                        alt={artist.artistname}
                        width={96}
                        height={96}
                        className={`block h-24 w-24 rounded-full object-cover transition duration-200 group-hover:scale-105 ${
                          selected
                            ? "ring-4 ring-green-500"
                            : "ring-1 ring-white/10"
                        }`}
                      />

                      {selected && (
                        <div className="absolute inset-0 flex items-center justify-center rounded-full bg-green-500/30">
                          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-green-500 text-lg font-bold text-black">
                            ✓
                          </div>
                        </div>
                      )}
                    </div>

                    <span className="mt-2 w-full truncate text-center text-xs font-medium text-white/80">
                      {artist.artistname}
                    </span>
                  </button>
                );
              })}
            </div>
          )}

          <div className="fixed bottom-0 left-0 right-0 mx-auto w-full max-w-md border-t border-white/10 bg-black/95 p-4 backdrop-blur">
            <button
              type="button"
              onClick={handleCompleteProfile}
              disabled={selectedArtists.length === 0 || isCompletingProfile}
              className="h-12 w-full rounded-xl bg-green-500 font-semibold text-black transition hover:bg-green-400 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {isCompletingProfile ? "در حال ذخیره..." : "ادامه"}
            </button>
          </div>
        </div>
      </main>
    );
  }

  // =====================================================
  // GOOGLE LOGIN UI
  // =====================================================
  return (
    <main className="flex min-h-screen items-center justify-center bg-black text-white">
      <div className="w-full max-w-sm px-6 text-center">
        <div className="mb-6">
          <h1 className="text-xl font-bold">ورود به Milify</h1>
          <p className="mt-2 text-sm text-gray-500">
            در حال ورود با Google...
          </p>
        </div>

        {isGoogleLoading && (
          <p className="text-sm text-gray-500">
            در حال اتصال به حساب Milify...
          </p>
        )}
      </div>
    </main>
  );
}