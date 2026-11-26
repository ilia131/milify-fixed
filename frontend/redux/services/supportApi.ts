import { apiSlice } from "./apiSlice";

export interface SupportRequest {
  id: string;
  email: string;
  subject: string;
  message: string;
  status: "OPEN" | "IN_PROGRESS" | "ANSWERED" | "CLOSED";
  created_at: string;
  updated_at: string;
}

interface CreateSupportRequest {
  email?: string;
  subject: string;
  message: string;
}

interface CreateSupportResponse {
  message: string;
  request: SupportRequest;
}

export const supportApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    createSupportRequest: builder.mutation<
      CreateSupportResponse,
      CreateSupportRequest
    >({
      query: (body) => ({
        url: "/permissions/support/",
        method: "POST",
        body,
      }),
    }),
  }),
});

export const {
  useCreateSupportRequestMutation,
} = supportApi;