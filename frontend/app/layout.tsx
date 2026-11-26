import type { Metadata, Viewport } from "next";
import { Vazirmatn } from "next/font/google";
import localFont from "next/font/local";

import RootClientLayout from "./RootClientLayout";
import Provider from "@/redux/Provider";
import PWARegister from "./pwa-register";
import "./globals.css";
import Setup from "@/utils/authsetup/Setup";
import { LanguageProvider } from "@/i18n/LanguageProvider";
import { ToastProvider } from "@/components/ToastProvider/ToastProvider";
import NavigationLoadingProvider from "@/components/NavigationLoadingProvider/NavigationLoadingProvider";
/* =========================================================
   VIEWPORT
========================================================= */

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: "cover",
  themeColor: "#121212",
};

/* =========================================================
   SEO / METADATA
========================================================= */

export const metadata: Metadata = {
  metadataBase: new URL("https://milify.ir"),

  title: {
    default: "میلیفای | Milify",
    template: "%s | میلیفای",
  },

  description:
    "میلیفای | Milify؛ پلتفرم موسیقی برای شنیدن، کشف و دنبال کردن آهنگ‌ها و هنرمندان ایرانی.",

  keywords: [
    "میلیفای",
    "Milify",
    "موسیقی",
    "موسیقی ایرانی",
    "آهنگ ایرانی",
    "موزیک ایرانی",
    "دانلود آهنگ",
    "پخش آنلاین موسیقی",
    "خواننده ایرانی",
    "هنرمندان ایرانی",
    "Persian Music",
    "Iranian Music",
    "Iranian Songs",
    "Persian Songs",
    "Music Streaming",
    "Milify Music",
  ],

  authors: [
    {
      name: "Milify",
      url: "https://milify.ir",
    },
  ],

  creator: "Milify",
  publisher: "Milify",

  applicationName: "Milify",

  category: "music",

  alternates: {
    canonical: "https://milify.ir",
  },

  robots: {
    index: true,
    follow: true,

    googleBot: {
      index: true,
      follow: true,
      "max-image-preview": "large",
      "max-snippet": -1,
      "max-video-preview": -1,
    },
  },

  /* =======================================================
     OPEN GRAPH
  ======================================================= */

  openGraph: {
    title: "میلیفای | Milify",

    description:
      "کشف و گوش دادن به موسیقی ایرانی، آهنگ‌ها و هنرمندان مورد علاقه‌تان در میلیفای.",

    url: "https://milify.ir",

    siteName: "میلیفای | Milify",

    locale: "fa_IR",

    type: "website",

    images: [
      {
        url: "/Icons/milify-192.png",
        width: 192,
        height: 192,
        alt: "لوگوی میلیفای | Milify",
      },
    ],
  },

  /* =======================================================
     TWITTER / X
  ======================================================= */

  twitter: {
    card: "summary_large_image",

    title: "میلیفای | Milify",

    description:
      "کشف و گوش دادن به موسیقی ایرانی و دنبال کردن هنرمندان در میلیفای.",

    images: ["/Icons/milify-192.png"],
  },

  /* =======================================================
     ICONS
  ======================================================= */

  icons: {
    icon: [
      {
        url: "/Icons/milify-192.png",
        sizes: "192x192",
        type: "image/png",
      },
    ],

    apple: [
      {
        url: "/Icons/milify-180.png",
        sizes: "180x180",
        type: "image/png",
      },
    ],
  },

  /* =======================================================
     PWA
  ======================================================= */

  manifest: "/manifest.webmanifest",
};

/* =========================================================
   ENGLISH FONT
========================================================= */

const inter = localFont({
  src: "../public/fonts/Inter23.ttf",
  variable: "--font-inter",
  display: "swap",
});

/* =========================================================
   PERSIAN FONT
========================================================= */

const vazirmatn = Vazirmatn({
  subsets: ["arabic"],
  variable: "--font-vazirmatn",
  display: "swap",
});

/* =========================================================
   ROOT LAYOUT
========================================================= */

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="fa"
      className={`${inter.variable} ${vazirmatn.variable}`}
    >
      <body className="font-[var(--font-vazirmatn)]">
      <NavigationLoadingProvider>
  <ToastProvider>
    <LanguageProvider>
      <Provider>
        <PWARegister />
        <Setup />

        <RootClientLayout>
          {children}
        </RootClientLayout>
        
      </Provider>
    </LanguageProvider>
  </ToastProvider>
</NavigationLoadingProvider>
      </body>
    </html>
  );
}