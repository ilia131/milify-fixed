// redux/services/adminUsersApi.ts

import { apiSlice } from "../apiSlice";

export interface AdminUser {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_artist: boolean;
  is_active: boolean;
  created_at: string;
  favorite_genres: string[];
  favorite_artists: string[];
  subscriptions: string[];
  is_staff:boolean
  profile_pic:string
  is_superuser :boolean
  has_active_subscription:boolean
}

interface UsersResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: AdminUser[];
}

interface ToggleUserActiveResponse {
  id: number;
  is_active: boolean;
}

// ─────────────────────────────────────
// Update Admin User
// ─────────────────────────────────────
export interface CreateAdminUserRequest {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  is_artist: boolean;
  is_active: boolean;
}
export interface UpdateAdminUserRequest {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_artist: boolean;
  is_active: boolean;
}

export const adminUsersApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    // ─────────────────────────────────────
    // Get Admin Users
    // ─────────────────────────────────────

    getAdminUsers: builder.query<
      UsersResponse,
      {
        page?: number;
        search?: string;
        is_artist?: string;
        is_active?: string;
      }
    >({
      query: ({
        page = 1,
        search = "",
        is_artist = "",
        is_active = "",
      }) => {
        const params = new URLSearchParams();

        params.set("page", String(page));

        if (search) {
          params.set("search", search);
        }

        if (is_artist) {
          params.set("is_artist", is_artist);
        }

        if (is_active) {
          params.set("is_active", is_active);
        }

        const token =
          typeof window !== "undefined"
            ? localStorage.getItem("admin_access")
            : null;

        return {
          url: `/permissions/admin/users/?${params.toString()}`,
          method: "GET",

          headers: token
            ? {
                Authorization: `Bearer ${token}`,
              }
            : undefined,
        };
      },

      providesTags: ["AdminUsers"],
    }),
    createAdminUser: builder.mutation<
  AdminUser,
  CreateAdminUserRequest
>({
  query: (data) => {
    const token =
      typeof window !== "undefined"
        ? localStorage.getItem("admin_access")
        : null;

    return {
      url: `/permissions/admin/users/create/`,
      method: "POST",
      body: data,

      headers: token
        ? {
            Authorization: `Bearer ${token}`,
          }
        : undefined,
    };
  },

  invalidatesTags: ["AdminUsers"],
}),
    // ─────────────────────────────────────
    // Get Single Admin User
    // ─────────────────────────────────────

    getAdminUser: builder.query<AdminUser, number>({
      query: (id) => {
        const token =
          typeof window !== "undefined"
            ? localStorage.getItem("admin_access")
            : null;

        return {
          url: `/permissions/admin/users/${id}/`,
          method: "GET",

          headers: token
            ? {
                Authorization: `Bearer ${token}`,
              }
            : undefined,
        };
      },

      providesTags: (_result, _error, id) => [
        {
          type: "AdminUsers",
          id,
        },
      ],
    }),

    // ─────────────────────────────────────
    // Update Admin User
    // ─────────────────────────────────────

    updateAdminUser: builder.mutation<
      AdminUser,
      {
        id: number;
        data: UpdateAdminUserRequest;
      }
    >({
      query: ({ id, data }) => {
        const token =
          typeof window !== "undefined"
            ? localStorage.getItem("admin_access")
            : null;

        return {
          url: `/permissions/admin/users/${id}/update/`,
          method: "PUT",
          body: data,

          headers: token
            ? {
                Authorization: `Bearer ${token}`,
              }
            : undefined,
        };
      },

      invalidatesTags: (_result, _error, { id }) => [
        "AdminUsers",
        {
          type: "AdminUsers",
          id,
        },
      ],
    }),

    // ─────────────────────────────────────
    // Toggle User Active
    // ─────────────────────────────────────

    toggleUserActive: builder.mutation<
      ToggleUserActiveResponse,
      number
    >({
      query: (id) => {
        const token =
          typeof window !== "undefined"
            ? localStorage.getItem("admin_access")
            : null;

        return {
          url: `/permissions/admin/users/${id}/toggle-active/`,
          method: "PATCH",

          headers: token
            ? {
                Authorization: `Bearer ${token}`,
              }
            : undefined,
        };
      },

      invalidatesTags: ["AdminUsers"],
    }),
  }),

  overrideExisting: false,
});

export const {
  useGetAdminUsersQuery,
  useGetAdminUserQuery,
  useUpdateAdminUserMutation,
  useToggleUserActiveMutation,
  useCreateAdminUserMutation,

} = adminUsersApi;