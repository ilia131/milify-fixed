import type { MetadataRoute } from "next";

const BASE_URL = "https://milify.ir";
const API_URL = "https://api.milify.ir";

interface SitemapArtist {
  uuid: string;
  artistname: string;
  updated_at?: string;
}

interface SitemapSong {
  unique_id: string;
  updated_at?: string;
}

interface SitemapData {
  artists: SitemapArtist[];
  songs: SitemapSong[];
}

/* =========================================================
   FETCH SEO SITEMAP DATA
========================================================= */

async function getSitemapData(): Promise<SitemapData> {
  try {
    const response = await fetch(
      `${API_URL}/api/seo/sitemap/`,
      {
        next: {
          revalidate: 3600,
        },
      }
    );

    if (!response.ok) {
      console.error(
        "Sitemap API error:",
        response.status
      );

      return {
        artists: [],
        songs: [],
      };
    }

    const data =
      (await response.json()) as SitemapData;

    return {
      artists: Array.isArray(data.artists)
        ? data.artists
        : [],

      songs: Array.isArray(data.songs)
        ? data.songs
        : [],
    };
  } catch (error) {
    console.error(
      "Sitemap fetch error:",
      error
    );

    return {
      artists: [],
      songs: [],
    };
  }
}

/* =========================================================
   SITEMAP
========================================================= */

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const data = await getSitemapData();

  /* =======================================================
     STATIC PAGES
  ======================================================= */

  const staticPages: MetadataRoute.Sitemap = [
    {
      url: BASE_URL,
      changeFrequency: "daily",
      priority: 1,
    },

    {
      url: `${BASE_URL}/search`,
      changeFrequency: "daily",
      priority: 0.8,
    },

    {
      url: `${BASE_URL}/explore`,
      changeFrequency: "daily",
      priority: 0.8,
    },
  ];

  /* =======================================================
     ARTIST PAGES
  ======================================================= */

  const artistPages: MetadataRoute.Sitemap =
    data.artists
      .filter((artist) => artist.uuid)
      .map((artist) => ({
        url: `${BASE_URL}/artist/${encodeURIComponent(
          artist.uuid
        )}`,

        lastModified: artist.updated_at
          ? new Date(artist.updated_at)
          : undefined,

        changeFrequency: "weekly" as const,

        priority: 0.8,
      }));

  /* =======================================================
     SONG PAGES
  ======================================================= */

  const songPages: MetadataRoute.Sitemap =
    data.songs
      .filter((song) => song.unique_id)
      .map((song) => ({
        url: `${BASE_URL}/track/${encodeURIComponent(
          song.unique_id
        )}`,

        lastModified: song.updated_at
          ? new Date(song.updated_at)
          : undefined,

        changeFrequency: "weekly" as const,

        priority: 0.7,
      }));

  /* =======================================================
     RETURN
  ======================================================= */

  return [
    ...staticPages,
    ...artistPages,
    ...songPages,
  ];
}