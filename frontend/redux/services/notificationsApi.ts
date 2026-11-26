import { apiSlice } from "./apiSlice";

export interface Notification {
    id: number;
    title: string;
    message: string;
    notification_type: string;
    url: string;
    is_read: boolean;
    created_at: string;
  }
export interface PushSubscriptionPayload {
  endpoint: string;
  p256dh: string;
  auth: string;
}

export const notificationsApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    getNotifications: builder.query<Notification[], void>({
      query: () => "/permissions/notifications/",
      providesTags: ["Notifications"],
    }),

    markNotificationRead: builder.mutation<
      void,
      number
    >({
      query: (id) => ({
        url: `/permissions/notifications/${id}/read/`,
        method: "PATCH",
      }),
      invalidatesTags: ["Notifications"],
    }),

    markAllNotificationsRead: builder.mutation<void, void>({
      query: () => ({
        url: "/permissions/notifications/read-all/",
        method: "PATCH",
      }),
      invalidatesTags: ["Notifications"],
    }),

    deleteNotification: builder.mutation<void, number>({
      query: (id) => ({
        url: `/permissions/notifications/${id}/`,
        method: "DELETE",
      }),
      invalidatesTags: ["Notifications"],
    }),

    subscribeToPush: builder.mutation<
      unknown,
      PushSubscriptionPayload
    >({
      query: (body) => ({
        url: "/permissions/push-subscriptions/",
        method: "POST",
        body,
      }),
    }),

    deletePushSubscription: builder.mutation<void, number>({
      query: (id) => ({
        url: `/permissions/push-subscriptions/${id}/`,
        method: "DELETE",
      }),
    }),
  }),

  overrideExisting: false,
});

export const {
  useGetNotificationsQuery,
  useMarkNotificationReadMutation,
  useMarkAllNotificationsReadMutation,
  useDeleteNotificationMutation,
  useSubscribeToPushMutation,
  useDeletePushSubscriptionMutation,
} = notificationsApi;