"use client";

import {
  Bell,
  Check,
  CheckCheck,
  Trash2,
  Music2,
  Disc3,
  UserRound,
  Loader2,
  ChevronLeft,
  ChevronRight,

} from "lucide-react";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import {
  useGetNotificationsQuery,
  useMarkNotificationReadMutation,
  useMarkAllNotificationsReadMutation,
  useDeleteNotificationMutation,
  Notification,
} from "@/redux/services/notificationsApi";

function getNotificationIcon(type: string) {
  switch (type) {
    case "new_song":
      return <Music2 size={19} strokeWidth={2} />;

    case "new_album":
      return <Disc3 size={19} strokeWidth={2} />;

    case "new_artist":
      return <UserRound size={19} strokeWidth={2} />;

    default:
      return <Bell size={19} strokeWidth={2} />;
  }
}

function formatDate(date: string) {
  return new Intl.DateTimeFormat("fa-IR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(date));
}

function getNotificationLabel(type: string) {
  switch (type) {
    case "new_song":
      return "آهنگ جدید";

    case "new_album":
      return "آلبوم جدید";

    case "new_artist":
      return "هنرمند جدید";

    default:
      return "اعلان";
  }
}

export default function NotificationsPage() {
  const router = useRouter();

  const {
    data: notifications = [],
    isLoading,
    isError,
    refetch,
  } = useGetNotificationsQuery();

  const [markRead, { isLoading: isMarkingRead }] =
    useMarkNotificationReadMutation();

  const [markAllRead, { isLoading: isMarkingAll }] =
    useMarkAllNotificationsReadMutation();

  const [deleteNotification] =
    useDeleteNotificationMutation();

  /**
   * وقتی Service Worker یک Push Notification دریافت کرد،
   * به صفحه پیام می‌فرستد.
   *
   * اینجا فقط notifications را دوباره می‌گیریم.
   *
   * هیچ polling وجود ندارد.
   */
  useEffect(() => {
    if (!("serviceWorker" in navigator)) {
      return;
    }

    const handleServiceWorkerMessage = (
      event: MessageEvent
    ) => {
      if (
        event.data?.type === "MILIFY_NOTIFICATION_RECEIVED"
      ) {
        refetch();
      }
    };

    navigator.serviceWorker.addEventListener(
      "message",
      handleServiceWorkerMessage
    );

    return () => {
      navigator.serviceWorker.removeEventListener(
        "message",
        handleServiceWorkerMessage
      );
    };
  }, [refetch]);

  /**
   * اگر کاربر از یک تب دیگر یا اپ دیگری برگردد،
   * اطلاعات اعلان‌ها تازه می‌شود.
   *
   * این درخواست فقط هنگام برگشت کاربر انجام می‌شود،
   * نه هر چند ثانیه.
   */
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        refetch();
      }
    };

    document.addEventListener(
      "visibilitychange",
      handleVisibilityChange
    );

    return () => {
      document.removeEventListener(
        "visibilitychange",
        handleVisibilityChange
      );
    };
  }, [refetch]);

  const unreadCount = notifications.filter(
    (notification) => !notification.is_read
  ).length;

  /**
   * کلیک روی اعلان
   *
   * 1. اگر خوانده نشده باشد → خوانده شده
   * 2. اگر URL داشته باشد → انتقال به صفحه مربوطه
   */
  const handleNotificationClick = (
    notification: Notification
  ) => {
    if (!notification.is_read) {
      markRead(notification.id);
    }

    if (notification.url) {
      router.push(notification.url);
    }
  };

  const handleDelete = async (id: number) => {
    await deleteNotification(id);
  };

  if (isLoading) {
    return (
      <main
        dir="rtl"
        className="min-h-screen bg-black text-white"
      >
        <div className="flex min-h-[70vh] items-center justify-center">
          <Loader2
            size={25}
            className="animate-spin text-zinc-400"
          />
        </div>
      </main>
    );
  }

  if (isError) {
    return (
      <main
        dir="rtl"
        className="min-h-screen bg-black px-4 text-white"
      >
        <div className="flex min-h-[70vh] items-center justify-center">
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] px-8 py-7 text-center">
            <Bell
              size={30}
              className="mx-auto mb-3 text-zinc-500"
            />

            <p className="text-sm text-zinc-400">
              دریافت اعلان‌ها با خطا مواجه شد.
            </p>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main
      dir="rtl"
      className="min-h-screen bg-black font-[Vazirmatn] text-white"
    >
      <div className="mx-auto w-full max-w-3xl px-4 pb-28 pt-6 sm:px-6 md:pt-10">
       
        {/* Header */}
        <header className="mb-8">
  <div className="flex items-start justify-between gap-4">

    {/* Back */}
    <button
      type="button"
      onClick={() => router.back()}
      aria-label="بازگشت"
      className="
        mt-1
        flex h-10 w-10 shrink-0
        items-center justify-center
        rounded-full
        border border-white/10
        bg-white/[0.04]
        text-zinc-400
        transition-all
        hover:border-white/20
        hover:bg-white/[0.08]
        hover:text-white
        active:scale-95
      "
    >
      <ChevronRight size={20} strokeWidth={1.8} />
    </button>

    <div className="flex-1">
      <div className="mb-3 flex items-center gap-3">

        <div className="flex h-11 w-11 items-center justify-center rounded-full bg-white text-black">
          <Bell size={21} />
        </div>

        <div>
          <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
            اعلان‌ها
          </h1>

          <p className="mt-1 text-xs text-zinc-500 sm:text-sm">
            آخرین اتفاقات Milify
          </p>
        </div>

      </div>
    </div>

    {unreadCount > 0 && (
      <button
        type="button"
        disabled={isMarkingAll}
        onClick={() => markAllRead()}
        className="
          group
          flex shrink-0
          items-center gap-2
          rounded-full
          border border-white/10
          bg-white/[0.04]
          px-3.5 py-2
          text-xs font-medium
          text-zinc-300
          transition-all
          hover:border-white/20
          hover:bg-white/[0.08]
          hover:text-white
          disabled:cursor-not-allowed
          disabled:opacity-50
          sm:text-sm
        "
      >
        {isMarkingAll ? (
          <Loader2
            size={15}
            className="animate-spin"
          />
        ) : (
          <CheckCheck
            size={15}
            className="transition-transform group-hover:scale-110"
          />
        )}

        خواندن همه
      </button>
    )}

  </div>
</header>
        {/* Empty */}
        {notifications.length === 0 && (
          <div className="relative overflow-hidden rounded-3xl border border-white/[0.08] bg-gradient-to-b from-white/[0.05] to-white/[0.015] px-6 py-20 text-center">

            <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent" />

            <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-white/[0.06]">
              <Bell
                size={27}
                className="text-zinc-500"
              />
            </div>

            <h2 className="text-base font-semibold">
              هنوز اعلانی نداری
            </h2>

            <p className="mx-auto mt-2 max-w-sm text-sm leading-6 text-zinc-500">
              وقتی آهنگ، آلبوم یا هنرمند جدیدی به
              Milify اضافه شود، اینجا بهت خبر می‌دهیم.
            </p>

          </div>
        )}

        {/* Notification List */}
        {notifications.length > 0 && (
          <div className="overflow-hidden rounded-3xl border border-white/[0.08] bg-white/[0.02]">

            {notifications.map((notification, index) => {
              const unread = !notification.is_read;

              return (
                <div
                  key={notification.id}
                  onClick={() =>
                    handleNotificationClick(notification)
                  }
                  className={[
                    "group relative flex cursor-pointer gap-3.5 px-4 py-4 transition-all sm:gap-4 sm:px-5",

                    index !== 0
                      ? "border-t border-white/[0.06]"
                      : "",

                    unread
                      ? "bg-white/[0.045] hover:bg-white/[0.07]"
                      : "hover:bg-white/[0.035]",
                  ].join(" ")}
                >

                  {/* Unread indicator */}
                  {unread && (
                    <span className="absolute right-0 top-0 h-full w-[2px] bg-white" />
                  )}

                  {/* Icon */}
                  <div
                    className={[
                      "flex h-11 w-11 shrink-0 items-center justify-center rounded-full transition-all sm:h-12 sm:w-12",

                      unread
                        ? "bg-white text-black"
                        : "bg-white/[0.07] text-zinc-400 group-hover:bg-white/[0.1] group-hover:text-white",
                    ].join(" ")}
                  >
                    {getNotificationIcon(
                      notification.notification_type
                    )}
                  </div>

                  {/* Content */}
                  <div className="min-w-0 flex-1">

                    <div className="flex items-start justify-between gap-3">

                      <div className="min-w-0">

                        <div className="mb-1 flex items-center gap-2">

                          <span className="text-[10px] font-medium text-zinc-600 sm:text-[11px]">
                            {getNotificationLabel(
                              notification.notification_type
                            )}
                          </span>

                          {unread && (
                            <span className="h-1.5 w-1.5 rounded-full bg-white" />
                          )}

                        </div>

                        <h3
                          className={[
                            "truncate text-sm sm:text-[15px]",

                            unread
                              ? "font-bold text-white"
                              : "font-medium text-zinc-300",
                          ].join(" ")}
                        >
                          {notification.title}
                        </h3>

                      </div>

                      {/* Desktop actions */}
                      <div className="hidden shrink-0 items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100 sm:flex">

                        {!notification.is_read && (
                          <button
                            type="button"
                            title="علامت‌گذاری به عنوان خوانده شده"
                            disabled={isMarkingRead}
                            onClick={(event) => {
                              event.stopPropagation();
                              markRead(notification.id);
                            }}
                            className="rounded-full p-2 text-zinc-500 transition hover:bg-white/10 hover:text-white disabled:opacity-50"
                          >
                            <Check size={15} />
                          </button>
                        )}

                        <button
                          type="button"
                          title="حذف اعلان"
                          onClick={(event) => {
                            event.stopPropagation();
                            handleDelete(notification.id);
                          }}
                          className="rounded-full p-2 text-zinc-500 transition hover:bg-red-500/10 hover:text-red-400"
                        >
                          <Trash2 size={15} />
                        </button>

                      </div>

                    </div>

                    {/* Message */}
                    <p className="mt-1 line-clamp-2 text-xs leading-6 text-zinc-500 sm:text-sm">
                      {notification.message}
                    </p>

                    {/* Date */}
                    <div className="mt-2 flex items-center gap-2">

                      <span className="text-[10px] text-zinc-600 sm:text-[11px]">
                        {formatDate(notification.created_at)}
                      </span>

                      {notification.url && (
                        <ChevronLeft
                          size={12}
                          className="text-zinc-700 transition-transform group-hover:-translate-x-0.5"
                        />
                      )}

                    </div>

                  </div>
                </div>
              );
            })}

          </div>
        )}

        {/* Bottom hint */}
        {notifications.length > 0 && (
          <p className="mt-6 text-center text-[11px] text-zinc-700">
            اعلان‌های جدید Milify اینجا نمایش داده می‌شوند
          </p>
        )}

      </div>
    </main>
  );
}