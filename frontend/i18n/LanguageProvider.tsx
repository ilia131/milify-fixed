"use client";

import {
  createContext,
  useContext,
  useEffect,
  useSyncExternalStore,
} from "react";

import fa from "./messages/fa.json";
import en from "./messages/en.json";

type Locale = "fa" | "en";

const messages = {
  fa,
  en,
};

type LanguageContextType = {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  toggleLocale: () => void;
  t: (key: string) => string;
};

const LanguageContext =
  createContext<LanguageContextType | null>(null);

const LOCALE_KEY = "milify-locale";
const localeChanged = "milify-locale-changed";

function subscribeLocale(listener: () => void) {
  window.addEventListener("storage", listener);
  window.addEventListener(localeChanged, listener);
  return () => {
    window.removeEventListener("storage", listener);
    window.removeEventListener(localeChanged, listener);
  };
}

function getLocale(): Locale {
  return localStorage.getItem(LOCALE_KEY) === "en" ? "en" : "fa";
}

export function LanguageProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const locale = useSyncExternalStore(subscribeLocale, getLocale, (): Locale => "fa");

  useEffect(() => {
    document.documentElement.lang = locale;
    // document.documentElement.dir =

    document.body.style.fontFamily =
      locale === "fa"
        ? "var(--font-vazirmatn)"
        : "var(--font-inter)";
  }, [locale]);

  const setLocale = (newLocale: Locale) => {
    localStorage.setItem(LOCALE_KEY, newLocale);
    window.dispatchEvent(new Event(localeChanged));
  };

  const toggleLocale = () => {
    setLocale(locale === "fa" ? "en" : "fa");
  };

  const t = (key: string) => {
    const keys = key.split(".");

    let value: unknown = messages[locale];

    for (const k of keys) {
      if (!value || typeof value !== "object" || !Object.hasOwn(value, k)) return key;
      value = (value as Record<string, unknown>)[k];
    }

    return typeof value === "string" ? value : key;
  };

  return (
    <LanguageContext.Provider
      value={{
        locale,
        setLocale,
        toggleLocale,
        t,
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);

  if (!context) {
    throw new Error(
      "useLanguage must be used inside LanguageProvider"
    );
  }

  return context;
}