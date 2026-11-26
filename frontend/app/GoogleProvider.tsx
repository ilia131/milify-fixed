"use client";

import { ReactNode } from "react";
import { GoogleOAuthProvider } from "@react-oauth/google";

interface GoogleProviderProps {
  children: ReactNode;
}

export default function GoogleProvider({
  children,
}: GoogleProviderProps) {
  const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "";

  return (
    <GoogleOAuthProvider clientId={clientId}
    
    >
      {children}
    </GoogleOAuthProvider>
  );
}
