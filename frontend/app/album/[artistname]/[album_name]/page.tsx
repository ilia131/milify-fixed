"use client";

import AlbumHero from "@/entities/albums/ui/album-hero";
import AlbumsRows from "@/entities/albums/ui/album-rows";

import { useGetAlbumDetailQuery } from "@/redux/services/artistApislice";
import { useParams, useRouter } from "next/navigation";
import { useEffect } from "react";

const Albums = () => {
  const params = useParams();
  const router = useRouter();

  const artist = params.artistname as string;
  const albums = params.album_name as string;

  const {
    data: detailPA,
    isLoading,
    isError,
    error,
  } = useGetAlbumDetailQuery(
    {
      artist,
      albums,
    },
    {
      skip: !artist || !albums,
    }
  );

  useEffect(() => {
    if (isError) {
      router.back();
    }
  }, [isError, router]);

  if (isLoading) {
    return null;
  }

  if (isError || !detailPA) {
    return null;
  }

  return (
    <div className="grid pb-50 overflow-hidden">
      <AlbumHero image={detailPA.cover ?? "p.svg"} />

      <AlbumsRows songs={detailPA.tracks ?? []} />
    </div>
  );
};

export default Albums;