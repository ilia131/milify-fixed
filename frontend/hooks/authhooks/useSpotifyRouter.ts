"use client";

import { useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import { useNavigationLoading } from "@/components/NavigationLoadingProvider/NavigationLoadingProvider";

type NavigateOptions = {
  replace?: boolean;
  delay?: number;
};

export default function useSpotifyRouter() {
  const router = useRouter();

  const navigatingRef = useRef(false);

  const { startLoading } = useNavigationLoading();

  const navigate = useCallback(
    (
      href: string,
      options: NavigateOptions = {}
    ) => {
      if (navigatingRef.current) return;

      navigatingRef.current = true;

      const {
        replace = true,
        delay = 50,
      } = options;

      // نمایش Loading
      startLoading();

      const navigateNow = () => {
        if (replace) {
          router.replace(href);
        } else {
          router.push(href);
        }

        // اجازه navigation بعدی
        setTimeout(() => {
          navigatingRef.current = false;
        }, 100);

        // fallback
        setTimeout(() => {
          if (
            typeof window !== "undefined" &&
            window.location.pathname !== href
          ) {
            window.location.replace(href);
          }
        }, 1500);
      };

      if (delay > 0) {
        setTimeout(navigateNow, delay);
      } else {
        navigateNow();
      }
    },
    [router, startLoading]
  );

  const refresh = useCallback(() => {
    router.refresh();
  }, [router]);

  return {
    navigate,

    push: (href: string) =>
      navigate(href, {
        replace: false,
        delay: 50,
      }),

    replace: (href: string) =>
      navigate(href, {
        replace: true,
        delay: 50,
      }),

    refresh,
  };
}