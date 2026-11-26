import { apiSlice } from "./apiSlice";

/* =========================================================
   TYPES
========================================================= */

export type BeatGenre =
  | "TRAP"
  | "HIPHOP"
  | "DRILL"
  | "RNB"
  | "POP"
  | "LOFI"
  | "OTHER";

export type BeatLicenseType =
  | "BASIC"
  | "PREMIUM"
  | "EXCLUSIVE";

export type BeatPurchaseStatus =
  | "PENDING"
  | "COMPLETED"
  | "REFUNDED";

/* =========================================================
   PRODUCER USER
========================================================= */

export interface ProducerUser {
  id: number | string;
  username: string;
  first_name: string;
  last_name: string;
}

/* =========================================================
   PRODUCER PROFILE
========================================================= */

export interface ProducerProfile {
  id: number;
  uuid: string;

  producer_name: string;
  bio: string;

  profile_pic: string | null;
  cover_image: string | null;

  instagram: string;
  youtube: string;

  is_verified: boolean;
  is_active: boolean;

  total_sales: number;
  total_revenue: number | string;

  user: ProducerUser;

  created_at: string;
}

/* =========================================================
   LICENSE
========================================================= */

export interface BeatLicense {
  id: number;

  license_type: BeatLicenseType;

  name: string;

  price: number | string;

  commercial_use: boolean;

  stems_included: boolean;

  exclusive: boolean;

  is_active: boolean;
}

/* =========================================================
   BEAT
========================================================= */

export interface Beat {
  id: number;

  title: string;

  slug: string;

  genre: BeatGenre;

  bpm: number | null;

  key: string;

  cover: string | null;

  preview_audio: string;

  description: string;

  price: number | string;

  is_active: boolean;

  is_featured: boolean;

  plays: number;

  sales: number;

  producer: ProducerProfile;

  licenses?: BeatLicense[];

  created_at: string;

  updated_at: string;
}

/* =========================================================
   PURCHASE
========================================================= */

export interface BeatPurchase {
  id: string;

  beat: Beat;

  price: number | string;

  status: BeatPurchaseStatus;

  created_at: string;
}

/* =========================================================
   BUY RESPONSE
========================================================= */

export interface BuyBeatResponse {
  message: string;

  purchase: {
    id: string;

    beat_id: number;

    beat_title: string;

    license_id: number;

    license_name: string;

    license_type: BeatLicenseType;

    price: number | string;

    platform_fee: number | string;

    producer_revenue: number | string;

    status: BeatPurchaseStatus;
  };

  buyer_wallet: {
    old_balance: number | string;

    remaining_balance: number | string;
  };

  producer: {
    uuid: string;

    producer_name: string;
  };

  producer_wallet: {
    old_balance: number | string;

    new_balance: number | string;
  };

  platform: {
    fee_percent: number | string;

    revenue: number | string;
  };
}

/* =========================================================
   DOWNLOAD
========================================================= */

export interface DownloadBeatResponse {
  beat: string;

  license: string;

  audio_file: string;
}

export const getPurchasedBeatStreamPath = (
  purchase_id: string
) => `/purchases/${purchase_id}/stream/`;

/* =========================================================
   API
========================================================= */

export const ProducerApiSlice =
  apiSlice.injectEndpoints({
    endpoints: (builder) => ({

      /* =====================================================
         BEATS
      ===================================================== */

      /**
       * GET /beats/
       *
       * لیست بیت‌ها
       *
       * Examples:
       *
       * /beats/
       * /beats/?search=trap
       * /beats/?genre=TRAP
       * /beats/?featured=true
       * /beats/?ordering=-sales
       */

      getBeats: builder.query<
        Beat[],
        {
          search?: string;

          genre?: BeatGenre;

          featured?: boolean;

          ordering?: string;
        } | void
      >({

        query: (params) => ({
          url: "/beats/",

          params: params
            ? {
                ...(params.search
                  ? {
                      search: params.search,
                    }
                  : {}),

                ...(params.genre
                  ? {
                      genre: params.genre,
                    }
                  : {}),

                ...(params.featured !== undefined
                  ? {
                      featured: params.featured
                        ? "true"
                        : "false",
                    }
                  : {}),

                ...(params.ordering
                  ? {
                      ordering: params.ordering,
                    }
                  : {}),
              }
            : undefined,
        }),

        providesTags: ["Beats"],
      }),

      /* =====================================================
         BEAT DETAIL
      ===================================================== */

      /**
       * GET /beats/{id}/
       */

      getBeatDetail: builder.query<
        Beat,
        number
      >({

        query: (id) =>
          `/beats/${id}/`,

        providesTags: (
          _result,
          _error,
          id
        ) => [
          {
            type: "Beat",
            id,
          },
        ],
      }),

      /* =====================================================
         BUY BEAT
      ===================================================== */

      /**
       * POST /beats/{beat_id}/buy/
       *
       * Body:
       *
       * {
       *   license_id: 2
       * }
       */

      buyBeat: builder.mutation<
        BuyBeatResponse,
        {
          beat_id: number;

          license_id: number;
        }
      >({

        query: ({
          beat_id,
          license_id,
        }) => ({
          url: `/beats/${beat_id}/buy/`,

          method: "POST",

          body: {
            license_id,
          },
        }),

        invalidatesTags: (
          _result,
          _error,
          { beat_id }
        ) => [
          "Beats",

          {
            type: "Beat",
            id: beat_id,
          },

          "MyBeatPurchases",
        ],
      }),

      /* =====================================================
         PRODUCER LIST
      ===================================================== */

      /**
       * GET /producers/
       */

      getProducers: builder.query<
      ProducerProfile[],
      { search?: string; ordering?: string } | void
    >({
      query: (params) => ({
        url: "/producers/",
        params: params
          ? {
              ...(params.search ? { search: params.search } : {}),
              ...(params.ordering
                ? { ordering: params.ordering }
                : {}),
            }
          : undefined,
      }),
    
      transformResponse: (response: any) => {
    
        if (Array.isArray(response)) {
          return response;
        }
    
        if (Array.isArray(response?.results)) {
          return response.results;
        }
    
        return [];
      },
    
      providesTags: ["Producers"],
    }),

      /* =====================================================
         PRODUCER PROFILE
      ===================================================== */

      /**
       * GET /producers/{uuid}/
       */

      getProducerProfile: builder.query<
        ProducerProfile,
        string
      >({

        query: (uuid) =>
          `/producers/${uuid}/`,

        providesTags: (
          _result,
          _error,
          uuid
        ) => [
          {
            type: "Producer",
            id: uuid,
          },
        ],
      }),

      /* =====================================================
         PRODUCER BEATS
      ===================================================== */

      /**
       * GET /producers/{uuid}/beats/
       */

      getProducerBeats: builder.query<
        Beat[],
        {
          uuid: string;

          search?: string;

          ordering?: string;
        }
      >({

        query: ({
          uuid,
          search,
          ordering,
        }) => ({
          url: `/producers/${uuid}/beats/`,

          params: {
            ...(search
              ? {
                  search,
                }
              : {}),

            ...(ordering
              ? {
                  ordering,
                }
              : {}),
          },
        }),

        providesTags: (
          _result,
          _error,
          { uuid }
        ) => [
          {
            type: "ProducerBeats",
            id: uuid,
          },
        ],
      }),

      /* =====================================================
         MY PURCHASES
      ===================================================== */

      /**
       * GET /my/purchases/
       */

      getMyBeatPurchases: builder.query<
        BeatPurchase[],
        void
      >({

        query: () =>
          "/my/purchases/",

        providesTags: [
          "MyBeatPurchases",
        ],
      }),

      /* =====================================================
         DOWNLOAD PURCHASED BEAT
      ===================================================== */

      /**
       * GET
       * /purchases/{purchase_id}/download/
       */

      downloadBeat: builder.query<
  DownloadBeatResponse,
  string
>({
  query: (purchase_id) =>
    `/purchases/${purchase_id}/download/`,
}),
      getPurchasedBeatStreamUrl: builder.query<
  string,
  string
>({
  queryFn: (purchase_id) => {
    const url =
      `/purchases/${purchase_id}/stream/`;

    return {
      data: url,
    };
  },
})

    }),
    
  });

/* =========================================================
   HOOKS
========================================================= */

export const {
  useGetBeatsQuery,
  useGetBeatDetailQuery,
  useBuyBeatMutation,

  useGetProducersQuery,
  useGetProducerProfileQuery,
  useGetProducerBeatsQuery,
  useGetPurchasedBeatStreamUrlQuery,
  useGetMyBeatPurchasesQuery,
  useLazyDownloadBeatQuery,
} = ProducerApiSlice;