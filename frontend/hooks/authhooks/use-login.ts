import { useAppDispatch } from "@/redux/hook";
import { useLoginMutation } from "@/redux/services/authApiSlice";
import { setAuth } from "@/redux/features/authSlice";
import useSpotifyRouter from "./useSpotifyRouter";
import { useToast } from "@/components/ToastProvider/ToastProvider";

interface LoginFormData {
  email: string;
  password: string;
}

export async function saveSession(
  { access, refresh }: { access: string; refresh: string },
  dispatch: ReturnType<typeof useAppDispatch>
) {
  if (!access || !refresh) throw new Error("توکن دریافت نشد");

  const response = await fetch("/api/auth/set-token", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ access, refresh }),
  });
  if (!response.ok) throw new Error("نشست ایجاد نشد");
  localStorage.setItem("access", access);
  localStorage.setItem("refresh", refresh);
  dispatch(setAuth({ access, refresh }));
}

export default function useLogin() {
  const { replace } = useSpotifyRouter();

  const { success, error } = useToast();

  const dispatch = useAppDispatch();

  const [login, { isLoading }] =
    useLoginMutation();

  const onSubmit = async (
    values: LoginFormData
  ) => {
    const { email, password } = values;

    try {
      const result = await login({
        email,
        password,
      }).unwrap();

      await saveSession(result, dispatch);

      // -------------------------
      // Success
      // -------------------------

      success(
        "Your login was successful"
      );

      // -------------------------
      // Spotify Router
      // -------------------------

      replace("/browse");

    } catch (err: unknown) {
      let errorMsg = "Login failed";

      if (err instanceof Error) {
        errorMsg = err.message;
      } else if (
        typeof err === "object" &&
        err !== null &&
        "data" in err
      ) {
        const e = err as {
          data?: {
            detail?: string;
          };
        };

        errorMsg =
          e.data?.detail ??
          errorMsg;
      }

      error(errorMsg);
    }
  };

  return {
    onSubmit,
    isLoading,
  };
}