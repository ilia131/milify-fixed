"use client";

import { useState, type FormEvent } from "react";
import { useResetPasswordMutation } from "@/redux/services/authApiSlice";

export default function ResetPasswordPage() {
  const [send, { isLoading }] = useResetPasswordMutation();
  const [status, setStatus] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const email = String(new FormData(event.currentTarget).get("email")).trim().toLowerCase();
    try {
      await send(email).unwrap();
      setStatus("اگر حساب فعالی با این ایمیل وجود داشته باشد، پیوند بازیابی ارسال می‌شود.");
    } catch {
      setStatus("درخواست انجام نشد. لطفاً بعداً دوباره تلاش کنید.");
    }
  }

  return (
    <main dir="rtl" className="mx-auto max-w-md space-y-4 px-6 py-16">
      <h1 className="text-xl font-bold">بازیابی رمز عبور</h1>
      <form className="space-y-3" onSubmit={submit}>
        <label htmlFor="reset-email">نشانی ایمیل</label>
        <input id="reset-email" name="email" type="email" autoComplete="email" dir="ltr"
          required className="block w-full rounded border p-2" />
        <button disabled={isLoading} className="rounded bg-green-500 px-4 py-2 text-black">
          ارسال پیوند بازیابی
        </button>
      </form>
      <p role="status">{status}</p>
    </main>
  );
}
