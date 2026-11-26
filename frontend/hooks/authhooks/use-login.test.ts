import { setAuth } from "@/redux/features/authSlice";
import { saveSession } from "./use-login";

jest.mock("@/redux/hook");
jest.mock("@/redux/services/authApiSlice");
jest.mock("./useSpotifyRouter");
jest.mock("@/components/ToastProvider/ToastProvider");

afterEach(() => {
  localStorage.clear();
  document.cookie = "access=; Max-Age=0; path=/";
  document.cookie = "refresh=; Max-Age=0; path=/";
});

test("persists the JWT session shared by sign-in and registration", async () => {
  const dispatch = jest.fn();
  const tokens = { access: "test-access", refresh: "test-refresh" };

  await saveSession(tokens, dispatch);

  expect(localStorage.getItem("access")).toBe(tokens.access);
  expect(localStorage.getItem("refresh")).toBe(tokens.refresh);
  expect(fetch).toHaveBeenCalledWith("/api/auth/set-token", expect.objectContaining({
    method: "POST", body: JSON.stringify(tokens),
  }));
  expect(dispatch).toHaveBeenCalledWith(setAuth(tokens));
});

test("does not authenticate when the response omits a token", async () => {
  const dispatch = jest.fn();

  await expect(saveSession({ access: "test-access", refresh: "" }, dispatch)).rejects.toThrow();

  expect(localStorage.getItem("access")).toBeNull();
  expect(dispatch).not.toHaveBeenCalled();
});
