import { apiSlice } from "./apiSlice";

// =========================
// Types
// =========================

export interface ShortVideoLikeResponse {
  liked: boolean;
  likes_count: number;
}

export interface ShortVideoComment {
  id: number;
  user_id: number;
  username: string;
  text: string;
  created_at: string;
  updated_at: string;
  parent: number | null;
  likes_count: number;
  is_liked: boolean;
  replies_count: number;
}

export interface ShortVideoCommentsResponse {
  count: number;
  results: ShortVideoComment[];
}

export interface CreateShortVideoCommentRequest {
  uuid: string;
  text: string;
  parent?: number | null;
}

export interface ShortVideoCommentLikeResponse {
  liked: boolean;
  likes_count: number;
}

export interface ShortVideoShareResponse {
  shares_count: number;
}

// =========================
// API
// =========================

export const shortApiSlice = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    // =========================
    // Like / Unlike Short Video
    // =========================

    shortVideoLike: builder.mutation<
      ShortVideoLikeResponse,
      string
    >({
      query: (uuid) => ({
        url: `/short-videos/${uuid}/like/`,
        method: "POST",
      }),

      invalidatesTags: (_result, _error, uuid) => [
        {
          type: "ShortVideo",
          id: uuid,
        },
      ],
    }),

    // =========================
    // Get Comments
    // =========================

    getShortVideoComments: builder.query<
      ShortVideoCommentsResponse,
      string
    >({
      query: (uuid) => ({
        url: `/short-videos/${uuid}/comments/`,
        method: "GET",
      }),

      providesTags: (result, _error, uuid) => [
        {
          type: "ShortVideoComments",
          id: uuid,
        },

        ...(result?.results ?? []).map((comment) => ({
          type: "ShortVideoComment" as const,
          id: comment.id,
        })),
      ],
    }),

    // =========================
    // Create Comment
    // =========================

    createShortVideoComment: builder.mutation<
      ShortVideoComment,
      CreateShortVideoCommentRequest
    >({
      query: ({ uuid, text, parent = null }) => ({
        url: `/short-videos/${uuid}/comments/`,
        method: "POST",
        body: {
          text,
          parent,
        },
      }),

      invalidatesTags: (_result, _error, { uuid }) => [
        {
          type: "ShortVideoComments",
          id: uuid,
        },
        {
          type: "ShortVideo",
          id: uuid,
        },
      ],
    }),

    // =========================
    // Delete Comment
    // =========================

    deleteShortVideoComment: builder.mutation<
      void,
      {
        commentId: number;
        uuid: string;
      }
    >({
      query: ({ commentId }) => ({
        url: `/short-video-comments/${commentId}/`,
        method: "DELETE",
      }),

      invalidatesTags: (_result, _error, { commentId, uuid }) => [
        {
          type: "ShortVideoComments",
          id: uuid,
        },
        {
          type: "ShortVideoComment",
          id: commentId,
        },
        {
          type: "ShortVideo",
          id: uuid,
        },
      ],
    }),

    // =========================
    // Like / Unlike Comment
    // =========================

    shortVideoCommentLike: builder.mutation<
      ShortVideoCommentLikeResponse,
      number
    >({
      query: (commentId) => ({
        url: `/short-video-comments/${commentId}/like/`,
        method: "POST",
      }),

      invalidatesTags: (_result, _error, commentId) => [
        {
          type: "ShortVideoComment",
          id: commentId,
        },
      ],
    }),

    // =========================
    // Share Short Video
    // =========================

    shortVideoShare: builder.mutation<
      ShortVideoShareResponse,
      string
    >({
      query: (uuid) => ({
        url: `/short-videos/${uuid}/share/`,
        method: "POST",
      }),

      invalidatesTags: (_result, _error, uuid) => [
        {
          type: "ShortVideo",
          id: uuid,
        },
      ],
    }),
  }),

  overrideExisting: false,
});

// =========================
// Hooks
// =========================

export const {
  useShortVideoLikeMutation,
  useGetShortVideoCommentsQuery,
  useCreateShortVideoCommentMutation,
  useDeleteShortVideoCommentMutation,
  useShortVideoCommentLikeMutation,
  useShortVideoShareMutation,
} = shortApiSlice;