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

test("persists the JWT session shared by sign-in and registration", () => {
  const dispatch = jest.fn();
  const tokens = { access: "test-access", refresh: "test-refresh" };

  saveSession(tokens, dispatch);

  expect(localStorage.getItem("access")).toBe(tokens.access);
  expect(localStorage.getItem("refresh")).toBe(tokens.refresh);
  expect(document.cookie).toContain("access=test-access");
  expect(document.cookie).toContain("refresh=test-refresh");
  expect(dispatch).toHaveBeenCalledWith(setAuth(tokens));
});

test("does not authenticate when the response omits a token", () => {
  const dispatch = jest.fn();

  expect(() => saveSession({ access: "test-access", refresh: "" }, dispatch)).toThrow();

  expect(localStorage.getItem("access")).toBeNull();
  expect(dispatch).not.toHaveBeenCalled();
});
