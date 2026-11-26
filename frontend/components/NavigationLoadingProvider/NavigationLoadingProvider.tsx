"use client";

import {
  createContext,
  useContext,
  useState,
  useCallback,
} from "react";

type NavigationLoadingContextType = {
  isLoading: boolean;
  startLoading: () => void;
  stopLoading: () => void;
};

const NavigationLoadingContext =
  createContext<NavigationLoadingContextType | undefined>(
    undefined
  );

export default function NavigationLoadingProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isLoading, setIsLoading] = useState(false);

  const startLoading = useCallback(() => {
    setIsLoading(true);
  }, []);

  const stopLoading = useCallback(() => {
    setIsLoading(false);
  }, []);

  return (
    <NavigationLoadingContext.Provider
      value={{
        isLoading,
        startLoading,
        stopLoading,
      }}
    >
      {children}
    </NavigationLoadingContext.Provider>
  );
}

export function useNavigationLoading() {
  const context = useContext(
    NavigationLoadingContext
  );

  if (!context) {
    throw new Error(
      "useNavigationLoading must be used inside NavigationLoadingProvider"
    );
  }

  return context;
}