import type { MetadataRoute } from "next";

const BASE_URL = "https://milify.ir";
const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "https://api.milify.ir";

interface Song {
  unique_id: string;
  release_date?: string;
}

interface Artist {
  uuid: string;
  updated_at?: string;
}

async function getSongs(): Promise<Song[]> {
  try {
    const response = await fetch(
      `${API_URL}/api/music/songs/?is_published=true`,
      {
        next: {
          revalidate: 3600,
        },
      }
    );

    if (!response.ok) {
      return [];
    }

    const data = await response.json();

    return Array.isArray(data)
      ? data
      : data.results || [];
  } catch {
    return [];
  }
}

async function getArtists(): Promise<Artist[]> {
  try {
    const response = await fetch(
      `${API_URL}/api/artists/`,
      {
        next: {
          revalidate: 3600,
        },
      }
    );

    if (!response.ok) {
      return [];
    }

    const data = await response.json();

    return Array.isArray(data)
      ? data
      : data.results || [];
  } catch {
    return [];
  }
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [songs, artists] = await Promise.all([
    getSongs(),
    getArtists(),
  ]);

  const staticPages: MetadataRoute.Sitemap = [
    {
      url: BASE_URL,
      lastModified: new Date(),
      changeFrequency: "daily",
      priority: 1,
    },
    {
      url: `${BASE_URL}/search`,
      lastModified: new Date(),
      changeFrequency: "daily",
      priority: 0.8,
    },
    {
      url: `${BASE_URL}/explore`,
      lastModified: new Date(),
      changeFrequency: "daily",
      priority: 0.9,
    },
  ];

  const songPages: MetadataRoute.Sitemap = songs
    .filter((song) => song.unique_id)
    .map((song) => ({
      url: `${BASE_URL}/track/${song.unique_id}`,
      lastModified: song.release_date
        ? new Date(song.release_date)
        : new Date(),
      changeFrequency: "weekly" as const,
      priority: 0.7,
    }));

  const artistPages: MetadataRoute.Sitemap = artists
    .filter((artist) => artist.uuid)
    .map((artist) => ({
      url: `${BASE_URL}/artist/${artist.uuid}`,
      lastModified: artist.updated_at
        ? new Date(artist.updated_at)
        : new Date(),
      changeFrequency: "weekly" as const,
      priority: 0.8,
    }));

  return [
    ...staticPages,
    ...songPages,
    ...artistPages,
  ];
}
