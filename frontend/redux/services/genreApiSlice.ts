import { apiSlice } from "./apiSlice";
import { Song } from "../features/playerSlice";

export interface Genre {
  id: number;
  name: string;
  songs_count: number;
  cover_image: string;
}

export interface GenreResponse {
  genre: {
    id: number;
    name: string;
    songs_count: number;
  };
  songs: {
    next: string | null;
    previous: string | null;
    results: Song[];
  };
}

export const GenreApiSlice = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    getSongbyGenre: builder.query<
      GenreResponse,
      { genre: string; nextUrl?: string | null }
    >({
      query: ({ genre, nextUrl }) => {
        const url = nextUrl || `/genres/browse/${genre}/`;

 
        return url;
      },

      serializeQueryArgs: ({ queryArgs }) => {
        return queryArgs.genre;
      },

      merge: (currentCache, newItems) => {
        

        if (newItems?.songs?.results?.length) {
          currentCache.songs.results.push(...newItems.songs.results);
          currentCache.songs.next = newItems.songs.next;
          currentCache.songs.previous = newItems.songs.previous;
        }
      },

      forceRefetch({ currentArg, previousArg }) {
      

        return currentArg?.nextUrl !== previousArg?.nextUrl;
      },
    }),

    getAllGenre: builder.query<Genre[], void>({
      query: () => {
        const url = `/genres/browse/?_t=${Date.now()}`;
    
    
        return url;
      },
    
     
    }),
  }),
});

export const {
  useGetSongbyGenreQuery,
  useGetAllGenreQuery,
} = GenreApiSlice;