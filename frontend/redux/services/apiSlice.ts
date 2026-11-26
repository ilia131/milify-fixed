import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { RootState } from "@/redux/store";
import { logout, setAuth } from "@/redux/features/authSlice";
import { Mutex } from "async-mutex";
import type {
  BaseQueryFn,
  FetchArgs,
  FetchBaseQueryError,
} from "@reduxjs/toolkit/query";

interface RefreshResponse {
  access: string;
  refresh: string;
}

const mutex = new Mutex();

const baseQuery = fetchBaseQuery({
  baseUrl: `${process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, "")}/api/`,
  credentials: "include",

  prepareHeaders: (headers, { getState }) => {
    const state = getState() as RootState;

    const token =
      state.auth.accessToken ||
      (typeof window !== "undefined"
        ? localStorage.getItem("access")
        : null);

    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }

    return headers;
  },
});

function clearStoredTokens() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
  }
}

async function refreshTokens(): Promise<RefreshResponse | null> {
  if (typeof window === "undefined") {
    return null;
  }

  const refresh = localStorage.getItem("refresh");

  if (!refresh) {
    return null;
  }

  const response = await fetch("/api/auth/refresh", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "same-origin",
    cache: "no-store",
    body: JSON.stringify({ refresh }),
  });

  if (!response.ok) {
    return null;
  }

  const data = (await response.json()) as Partial<RefreshResponse>;

  if (
    typeof data.access !== "string" ||
    typeof data.refresh !== "string"
  ) {
    return null;
  }

  return {
    access: data.access,
    refresh: data.refresh,
  };
}

const baseQueryWithReauth: BaseQueryFn<
  string | FetchArgs,
  unknown,
  FetchBaseQueryError
> = async (args, api, extraOptions) => {
  await mutex.waitForUnlock();

  let result = await baseQuery(args, api, extraOptions);

  if (result.error?.status !== 401) {
    return result;
  }

  if (!mutex.isLocked()) {
    const release = await mutex.acquire();

    try {
      const tokens = await refreshTokens();

      if (!tokens) {
        clearStoredTokens();
        api.dispatch(logout());
        return result;
      }

      localStorage.setItem("access", tokens.access);
      localStorage.setItem("refresh", tokens.refresh);

      api.dispatch(
        setAuth({
          access: tokens.access,
          refresh: tokens.refresh,
        })
      );

      result = await baseQuery(args, api, extraOptions);
    } catch (error) {
      console.error("Token refresh failed:", error);

      clearStoredTokens();
      api.dispatch(logout());
    } finally {
      release();
    }
  } else {
    await mutex.waitForUnlock();
    result = await baseQuery(args, api, extraOptions);
  }

  return result;
};

export const apiSlice = createApi({
  baseQuery: baseQueryWithReauth,
  endpoints: () => ({}),
  tagTypes: [
    "LikedSongs",
    "Playlists",
    "Playlist",
    "FavoriteArtists",
    "PlayerAds",
    "SubscriptionPlans",
    "MySubscription",
    "ArtistSubscription",
    "SongSubscriptionAccess",
    "UserProfile",
    "AdminUsers",
    "AdminArtists",
    "AdminSongs",
    "AdminPlaylists",
    "AdminRevenue",
    "AdminPayments",
    "AdminSubscriptions",
    "AdminAds",
    "Beats",
    "Beat",
    "Producers",
    "Producer",
    "ProducerBeats",
    "MyBeatPurchases",
    "Notifications",
    "ShortVideo",
    "ShortVideoComments",
    "ShortVideoComment",
  ],
});