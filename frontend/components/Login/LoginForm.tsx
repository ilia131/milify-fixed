"use client";

import { Formik, Form } from "formik";
import * as Yup from "yup";

import OAuthSection from "./OAuthSection";
import { SubmitButton } from "./SubmitButton";
import { FormField } from "../../shared/FormField/FormField";
import useLogin from "@/hooks/authhooks/use-login";
import { useLanguage } from "@/i18n/LanguageProvider";

interface LoginFormValues {
  email: string;
  password: string;
}

const LoginForm = () => {
  const { onSubmit, isLoading } = useLogin();
  const { t, locale } = useLanguage();

  const initialValues: LoginFormValues = {
    email: "",
    password: "",
  };

  const validationSchema = Yup.object({
    email: Yup.string()
      .email(t("login.validation.invalidEmail"))
      .required(t("login.validation.emailRequired")),

    password: Yup.string().required(
      t("login.validation.passwordRequired")
    ),
  });

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={onSubmit}
    >
      {({ handleSubmit }) => (
        <Form
          className="pt-6"
          noValidate
          onSubmit={handleSubmit}
          dir={locale === "fa" ? "rtl" : "ltr"}
        >
          <FormField
            name="email"
            label={t("login.emailOrUsername")}
            placeholder={t("login.emailOrUsername")}
            type="email"
          />

          <FormField
            name="password"
            label={t("login.password")}
            placeholder={t("login.passwordPlaceholder")}
            type="password"
          />

          <SubmitButton isLoading={isLoading}>
            {t("login.continue")}
          </SubmitButton>

          <OAuthSection />
        </Form>
      )}
    </Formik>
  );
};

export default LoginForm;