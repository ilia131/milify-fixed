import { apiSlice } from "./apiSlice"

export interface CategorySong {
  id: number
  unique_id: string
  title: string | null
  description?: string | null
  duration?: number
  popularity?: number
  tempo?: number
  energy?: number
  danceability?: number
  valence?: number | null
  acousticness?: number | null
  image?: string | null
  track?: string | null
  play_count?: number
  unique_listeners?: number
  plays_last_24h?: number
  release_date?: string
}

export interface CategoryRecommendation {
  category: string
  count: number
  songs: CategorySong[]
}

export type CategoryRecommendationsResponse = Record<
  string,
  CategoryRecommendation
>


export const songApiSlice = apiSlice.injectEndpoints({
  endpoints: builder => ({

    playSong: builder.mutation({
      query: (songId: number) => ({
        url: `/songs/${songId}/play/`,
        method: "POST",
      }),
    }),

    getRecentlyPlayed: builder.query({
      query: () => "/recently-played/",
    }),

    getForYou: builder.query({
      query: () => "/recommendations/for-you/",
    }),

    getCategoryRecommendations:
      builder.query<CategoryRecommendationsResponse, void>({
        query: () => "/tt/recommendations/categories/",
      }),

    getSongDetail: builder.query({
      query: (uniqueId) => `tracks/${uniqueId}/`,
    }),
  }),
})


export const {
  usePlaySongMutation,
  useGetRecentlyPlayedQuery,
  useGetForYouQuery,
  useGetCategoryRecommendationsQuery,
  useGetSongDetailQuery,
} = songApiSlice