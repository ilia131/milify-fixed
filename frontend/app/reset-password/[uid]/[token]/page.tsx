"use client";

import { useState, type FormEvent } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useResetPasswordConfirmMutation } from "@/redux/services/authApiSlice";

export default function ResetPasswordConfirmPage() {
  const { uid, token } = useParams<{ uid: string; token: string }>();
  const [confirm, { isLoading }] = useResetPasswordConfirmMutation();
  const [error, setError] = useState("");
  const [finished, setFinished] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const values = new FormData(event.currentTarget);
    const new_password = String(values.get("password"));
    const re_new_password = String(values.get("confirmation"));
    if (new_password !== re_new_password) {
      setError("رمز عبور و تکرار آن یکسان نیستند.");
      return;
    }
    try {
      await confirm({ uid, token, new_password, re_new_password }).unwrap();
      setError("");
      setFinished(true);
    } catch {
      setError("رمز پذیرفته نشد یا پیوند بازیابی اعتبار ندارد.");
    }
  }

  return (
    <main dir="rtl" className="mx-auto max-w-md space-y-4 px-6 py-16">
      <h1 className="text-xl font-bold">انتخاب رمز عبور جدید</h1>
      {finished ? (
        <p role="status">رمز عبور تغییر کرد. <Link href="/auth/login">ورود به حساب</Link></p>
      ) : (
        <form className="space-y-3" onSubmit={submit}>
          <label htmlFor="new-password">رمز عبور جدید</label>
          <input id="new-password" name="password" type="password" autoComplete="new-password"
            required minLength={8} className="block w-full rounded border p-2" />
          <label htmlFor="confirm-password">تکرار رمز عبور</label>
          <input id="confirm-password" name="confirmation" type="password"
            autoComplete="new-password" required minLength={8} className="block w-full rounded border p-2" />
          <button disabled={isLoading} className="rounded bg-green-500 px-4 py-2 text-black">
            ذخیرهٔ رمز عبور
          </button>
        </form>
      )}
      {error && <p role="alert">{error}</p>}
    </main>
  );
}
