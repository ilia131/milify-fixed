"use client";

import { useLanguage } from "@/i18n/LanguageProvider";

const LoginHeader = () => {
  const { t } = useLanguage();

  return (
    <p className="text-[rgba(255,255,255,0.9)] font-extrabold text-[43px] text-center max-[360px]:text-[37px]">
      {t("login.welcomeBack")}
    </p>
  );
};

export default LoginHeader;