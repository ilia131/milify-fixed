import { apiSlice } from "./apiSlice";
import type { Album } from "./artistApislice";
import type { Song } from "@/redux/features/playerSlice";

type Page<T> = { results: T[]; next: string | null };

function nextCursor<T>(page: Page<T>) {
  return page.next ? new URL(page.next, "http://localhost").searchParams.get("cursor") ?? undefined : undefined;
}

function artistPageUrl(artistname: string, resource: "songs" | "albums", cursor: string | null) {
  const path = `/artists/${encodeURIComponent(artistname)}/${resource}/`;
  return cursor ? `${path}?cursor=${encodeURIComponent(cursor)}` : path;
}

export const artistContentApiSlice = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    artistSongPages: builder.infiniteQuery<Page<Song>, string, string | null>({
      query: ({ queryArg, pageParam }) => artistPageUrl(queryArg, "songs", pageParam),
      infiniteQueryOptions: { initialPageParam: null, getNextPageParam: nextCursor },
    }),
    artistAlbumPages: builder.infiniteQuery<Page<Album>, string, string | null>({
      query: ({ queryArg, pageParam }) => artistPageUrl(queryArg, "albums", pageParam),
      infiniteQueryOptions: { initialPageParam: null, getNextPageParam: nextCursor },
    }),

    getArtistSongs: builder.query({
      query: ({ artistname, cursor }) => {
        let url = `/artists/${artistname}/songs/`;
        if (cursor) url += `?cursor=${cursor}`;
        return url;
      },
    }),

    getArtistAlbums: builder.query({
      query: ({ artistname, cursor }) => {
        let url = `/artists/${artistname}/albums/`;
        if (cursor) url += `?cursor=${cursor}`;
        return url;
      },

      // مهم برای infinite scroll
      serializeQueryArgs: ({ queryArgs }) => {
        return queryArgs.artistname;
      },

      merge: (currentCache, newItems) => {
        const map = new Map(
          currentCache.results?.map((a: Album) => [a.id, a])
        );

        newItems.results?.forEach((a: Album) => {
          map.set(a.id, a);
        });

        currentCache.results = Array.from(map.values());
        currentCache.next = newItems.next;
      },

      forceRefetch({ currentArg, previousArg }) {
        return currentArg?.cursor !== previousArg?.cursor;
      },
    }),

  }),
});

export const {
  useArtistSongPagesInfiniteQuery,
  useArtistAlbumPagesInfiniteQuery,
  useGetArtistSongsQuery,
  useGetArtistAlbumsQuery,
} = artistContentApiSlice;
