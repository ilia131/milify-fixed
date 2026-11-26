import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import { useAppDispatch } from "@/redux/hook";
import { useLoginMutation, useRegisterMutation } from "@/redux/services/authApiSlice";
import useSpotifyRouter from "@/hooks/authhooks/useSpotifyRouter";
import { useToast } from "@/components/ToastProvider/ToastProvider";
import RegisterPage from "./page";

jest.mock("@/redux/hook");
jest.mock("@/redux/services/authApiSlice");
jest.mock("@/redux/services/artistApislice", () => ({
  useGetArtistsListQuery: () => ({ data: [], isLoading: false }),
}));
jest.mock("@/hooks/authhooks/useSpotifyRouter");
jest.mock("@/components/ToastProvider/ToastProvider");

const register = jest.fn();
const login = jest.fn();
const dispatch = jest.fn();
const replace = jest.fn();
const error = jest.fn();

beforeEach(() => {
  jest.clearAllMocks();
  jest.mocked(useLoginMutation).mockReturnValue([login, { isLoading: false }] as
    unknown as ReturnType<typeof useLoginMutation>);
  jest.mocked(useRegisterMutation).mockReturnValue([register, { isLoading: false }] as
    unknown as ReturnType<typeof useRegisterMutation>);
  jest.mocked(useAppDispatch).mockReturnValue(dispatch);
  jest.mocked(useSpotifyRouter).mockReturnValue({
    replace, navigate: jest.fn(), push: jest.fn(), refresh: jest.fn(),
  });
  jest.mocked(useToast).mockReturnValue({
    success: jest.fn(), error, info: jest.fn(), warning: jest.fn(), showToast: jest.fn(),
  });
});

afterEach(() => {
  localStorage.clear();
  document.cookie = "access=; Max-Age=0; path=/";
  document.cookie = "refresh=; Max-Age=0; path=/";
});

function submitRegistration() {
  render(<RegisterPage />);
  const fields = {
    "First name": "Ava",
    "Last name": "Example",
    Username: "ava",
    "Email address": "Ava@example.com",
    Password: "long-password-example",
    "Confirm password": "long-password-example",
  };
  for (const [label, value] of Object.entries(fields)) {
    fireEvent.change(screen.getByLabelText(label, { exact: true }), { target: { value } });
  }
  fireEvent.click(screen.getByRole("button", { name: "Continue" }));
  fireEvent.click(screen.getByRole("button", { name: "Complete" }));
}

test("signs the listener in immediately after registration", async () => {
  register.mockReturnValue({ unwrap: async () => ({ id: 1 }) });
  login.mockReturnValue({ unwrap: async () => ({ access: "access-test", refresh: "refresh-test" }) });
  submitRegistration();

  await waitFor(() => expect(replace).toHaveBeenCalledWith("/browse"));
  expect(login).toHaveBeenCalledWith({ email: "ava@example.com", password: "long-password-example" });
  expect(localStorage.getItem("access")).toBe("access-test");
  expect(error).not.toHaveBeenCalled();
});

test("stays on the form when registration fails", async () => {
  register.mockReturnValue({ unwrap: async () => { throw { data: { email: ["Email already registered"] } }; } });
  submitRegistration();

  await waitFor(() => expect(error).toHaveBeenCalledWith("Email already registered"));
  expect(login).not.toHaveBeenCalled();
  expect(replace).not.toHaveBeenCalled();
});
