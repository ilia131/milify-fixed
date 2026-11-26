"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";

import BottomNav from "@/shared/BottomNav/BottomNav";
import MenuBar from "@/shared/MenuBar/MenuBar";

import MusicPlayerProvider from "@/shared/MusicPlayer/MusicPlayerProvider";
import MusicOptionsSheet from "@/shared/ui/BottomSheet/MusicOptionsSheet";
import PlaylistSelectorSheet from "@/components/Library/PlaylistSelectorSheet";
import { PlayerUIProvider } from "@/shared/MusicPlayer/context/playerUIContext";
import {
  useAppDispatch,
  useAppSelector,
} from "@/redux/hook";

import {
  closeMenu,
} from "@/redux/features/uiSlice";

import LanguageSwitcher from "@/shared/LanguageSwitcher/LanguageSwitcher";

import { useNavigationLoading } from "@/components/NavigationLoadingProvider/NavigationLoadingProvider";

export default function RootClientLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const isAuthenticated = useAppSelector(
    (state) => state.auth.isAuthenticated
  );
  const dispatch = useAppDispatch();

  const {
    isLoading,
    stopLoading,
  } = useNavigationLoading();

  useEffect(() => {
    stopLoading();
  }, [pathname, stopLoading]);

  const isMenuOpen = useAppSelector(
    (state) => state.ui.isMenuOpen
  );

  const hasSong = useAppSelector(
    (state) => state.player.queue.length > 0
  );

  const locale = pathname.startsWith("/en")
    ? "en"
    : "fa";

  const isEnglish = locale === "en";
  const isLandingPage = pathname === "/";
  const isArtistPage =
  pathname === "/home" || pathname.startsWith("/home/");  // Routes
  const isAuthPage =
    pathname === "/auth/login" ||
    pathname === "/auth/register";

  const isAddLikedSongsPage =
    pathname === "/library/LikedSongs/AddLikeSongs";

  const isHomePage =
    pathname === "/home";

  const isAdminRoute =
    pathname.startsWith("/admin");

  const handleCloseMenu = () => {
    dispatch(closeMenu());
  };
  if (isLandingPage || isArtistPage) {
    return (
      <div
        className="w-full min-h-screen"
        dir={isEnglish ? "ltr" : "rtl"}
      >
        {children}
      </div>
    );
  }
  /*
  =========================================================
  ADMIN
  =========================================================
  */

  if (isAdminRoute) {
    return (
      <div
        className="min-h-screen w-full"
        dir={isEnglish ? "ltr" : "rtl"}
      >
        {children}

        <LanguageSwitcher />

        {isLoading && (
          <div className="fixed inset-0 z-[99999] flex items-center justify-center bg-[#121212]">
            <div className="flex flex-col items-center gap-4">
              <div className="h-10 w-10 animate-spin rounded-full border-4 border-white/20 border-t-[#1DB954]" />

              <span className="text-sm text-white">
                Loading...
              </span>
            </div>
          </div>
        )}
      </div>
    );
  }

  /*
  =========================================================
  MAIN
  =========================================================
  */

  return (
    <PlayerUIProvider>
      <div className="flex justify-center w-full">
        <div
          className={`
            relative
            min-h-screen
            ${
              isHomePage
                ? "w-full"
                : "w-[440px] max-w-full"
            }
          `}
        >
          {/* Page */}
          {children}
  
          {/* Music Options */}
          <MusicOptionsSheet />
  
          {/* Music Player */}
          {hasSong && !isAuthPage && (
            <MusicPlayerProvider />
          )}
  
          {/* Menu */}
          <MenuBar
            isOpen={isMenuOpen}
            onClose={handleCloseMenu}
          />
  
          {/* Playlist Selector */}
          <PlaylistSelectorSheet />
  
          {/* Bottom Navigation */}
          {!isAuthPage &&
            !isAddLikedSongsPage &&
            !isHomePage && (
              <BottomNav />
            )}
  
          <LanguageSwitcher />
  
          {/* Navigation Loading */}
          {isLoading && (
            <div className="fixed inset-0 z-[99999] flex items-center justify-center bg-[#121212]">
              <div className="flex flex-col items-center gap-4">
                <div className="h-10 w-10 animate-spin rounded-full border-4 border-white/20 border-t-[#1DB954]" />
  
                <span className="text-sm text-white">
                  Loading...
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </PlayerUIProvider>
  );
}