import { apiSlice } from "./apiSlice";

/* =========================================================
   USER
========================================================= */

interface User {
  id?: number;
  first_name: string;
  last_name: string;
  email: string;
  username?: string;
  profile_pic?: string | null;
  is_artist?: boolean;
}

/* =========================================================
   REGISTER
========================================================= */

type RegisterRequest = {
  first_name: string;
  last_name: string;
  username: string;
  email: string;
  password: string;
  re_password: string;
  favorite_artists: string[];
};

type RegisterResponse = {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  favorite_artists?: string[];
};

/* =========================================================
   LOGIN
========================================================= */

interface LoginResponse {
  access: string;
  refresh: string;
}

/* =========================================================
   GOOGLE LOGIN
========================================================= */

/**
 * Google ID Token
 *
 * Google
 *   ↓
 * Google ID Token
 *   ↓
 * Django /google/login/
 *   ↓
 * Milify JWT
 */

interface GoogleTokenLoginRequest {
  id_token: string;
}

interface GoogleTokenLoginResponse {
  access: string;
  refresh: string;

  created?: boolean;

  user?: {
    id: number;
    email: string;
    username: string;
    first_name: string;
    last_name: string;
  };
}

/* =========================================================
   GOOGLE PROFILE COMPLETION
========================================================= */

interface CompleteGoogleProfileRequest {
  favorite_artists: string[];
}

interface CompleteGoogleProfileResponse {
  detail: string;
  favorite_artists: string[];
}

/* =========================================================
   API
========================================================= */

const authApiSlice = apiSlice.injectEndpoints({
  endpoints: (builder) => ({

    // =====================================================
    // GET CURRENT USER
    // =====================================================

    retrieveUser: builder.query<User, void>({
      query: () => "/users/me/",
      providesTags: ["UserProfile"],
    }),

    // =====================================================
    // NORMAL LOGIN
    // =====================================================

    login: builder.mutation<
      LoginResponse,
      {
        email: string;
        password: string;
      }
    >({
      query: ({ email, password }) => ({
        url: "/jwt/create/",
        method: "POST",
        body: {
          email,
          password,
        },
      }),

      invalidatesTags: ["UserProfile"],
    }),

    // =====================================================
    // GOOGLE LOGIN
    // =====================================================

    /**
     * Google ID Token
     *       ↓
     * Django verifies Google
     *       ↓
     * Find / Create UserListener
     *       ↓
     * Milify Access + Refresh JWT
     */

    googleTokenLogin: builder.mutation<
      GoogleTokenLoginResponse,
      GoogleTokenLoginRequest
    >({
      query: ({ id_token }) => ({
        url: "/google/login/",
        method: "POST",
        body: {
          id_token,
        },
      }),

      invalidatesTags: ["UserProfile"],
    }),

    // =====================================================
    // GOOGLE PROFILE COMPLETION
    // =====================================================

    /**
     * After Google Login:
     *
     * Artist Selection
     *       ↓
     * favorite_artists
     *       ↓
     * Django
     *       ↓
     * user.favorite_artists.set(...)
     */

    completeGoogleProfile: builder.mutation<
      CompleteGoogleProfileResponse,
      CompleteGoogleProfileRequest
    >({
      query: (body) => ({
        url: "/google/complete-profile/",
        method: "POST",
        body,
      }),

      invalidatesTags: ["UserProfile"],
    }),

    // =====================================================
    // REGISTER
    // =====================================================

    register: builder.mutation<
      RegisterResponse,
      RegisterRequest
    >({
      query: (body) => ({
        url: "/users/",
        method: "POST",
        body,
      }),

      invalidatesTags: ["UserProfile"],
    }),

    // =====================================================
    // VERIFY JWT
    // =====================================================

    verify: builder.mutation<
      unknown,
      {
        token: string;
      }
    >({
      query: (body) => ({
        url: "/jwt/verify/",
        method: "POST",
        body,
      }),
    }),

    // =====================================================
    // LOGOUT
    // =====================================================

    logout: builder.mutation<
      unknown,
      void
    >({
      query: () => ({
        body: {
          refresh: typeof window !== "undefined" ? localStorage.getItem("refresh") : null,
        },
        url: "/logout/",
        method: "POST",
      }),

      invalidatesTags: ["UserProfile"],
    }),

    // =====================================================
    // RESET PASSWORD
    // =====================================================

    resetPassword: builder.mutation<
      unknown,
      string
    >({
      query: (email) => ({
        url: "/users/reset_password/",
        method: "POST",
        body: {
          email,
        },
      }),
    }),

    // =====================================================
    // RESET PASSWORD CONFIRM
    // =====================================================

    resetPasswordConfirm: builder.mutation<
      unknown,
      {
        uid: string;
        token: string;
        new_password: string;
        re_new_password: string;
      }
    >({
      query: ({
        uid,
        token,
        new_password,
        re_new_password,
      }) => ({
        url: "/users/reset_password_confirm/",
        method: "POST",
        body: {
          uid,
          token,
          new_password,
          re_new_password,
        },
      }),
    }),
  }),
});

/* =========================================================
   EXPORT HOOKS
========================================================= */

export const {
  // Current User
  useRetrieveUserQuery,

  // Normal Login
  useLoginMutation,

  // Google
  useGoogleTokenLoginMutation,
  useCompleteGoogleProfileMutation,

  // Register
  useRegisterMutation,

  // JWT
  useVerifyMutation,

  // Logout
  useLogoutMutation,

  // Activation

  // Password Reset
  useResetPasswordMutation,
  useResetPasswordConfirmMutation,

} = authApiSlice;