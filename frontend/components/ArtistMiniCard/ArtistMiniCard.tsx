"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";

import {
  Artist,
  useGetFavArtistsQuery,
} from "@/redux/services/artistApislice";

import { useAppSelector } from "@/redux/hook";

const ArtistMiniCard = () => {
  const router = useRouter();

  const {
    isAuthenticated,
    initialLoadFinished,
  } = useAppSelector((state) => state.auth);

  const {
    data: artists,
    isLoading,
    error,
  } = useGetFavArtistsQuery(0, {
    skip:
      !initialLoadFinished ||
      !isAuthenticated,
  });

  // هنوز auth مشخص نشده
  if (!initialLoadFinished) {
    return null;
  }

  // کاربر لاگین نیست
  if (!isAuthenticated) {
    return null;
  }

  // API خطا داده
  if (error) {
    return null;
  }

  // دیتا نداریم
  if (!Array.isArray(artists) || artists.length === 0) {
    return null;
  }

  return (
    <section className="grid grid-cols-2 gap-3 pr-3">
      {artists.map((artist: Artist) => {
        if (
          !artist ||
          !artist.id ||
          !artist.artistname ||
          !artist.profile_pic
        ) {
          return null;
        }

        return (
          <div
            key={artist.id}
            className="flex cursor-pointer"
            onClick={() =>
              router.push(`/artist/${artist.artistname}`)
            }
          >
            <div
              className="
                h-15 w-17
                overflow-hidden
                rounded-tl-[5px]
                rounded-tr-[1px]
                rounded-br-[1px]
                rounded-bl-[5px]
              "
            >
              <Image
                src={artist.profile_pic}
                width={60}
                height={60}
                alt={artist.artistname}
                className="
                  h-full object-cover
                  rounded-tl-[5px]
                  rounded-tr-[1px]
                  rounded-br-[1px]
                  rounded-bl-[5px]
                "
              />
            </div>

            <div
              className="
                flex h-15 w-full
                items-center
                rounded-tl-[1px]
                rounded-tr-[5px]
                rounded-br-[5px]
                rounded-bl-[1px]
                bg-[rgb(39_39_39/0.91)]
                pl-4
              "
            >
              <p className="text-[12.5px] font-semibold text-[rgb(255_255_255/0.86)]">
                {artist.artistname}
              </p>
            </div>
          </div>
        );
      })}
    </section>
  );
};

export default ArtistMiniCard;