"use client";

import { ReactNode } from "react";
import { PlayerUIProvider } from "./context/playerUIContext";

export default function PlayerProvider({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <PlayerUIProvider>
      {children}
    </PlayerUIProvider>
  );
}