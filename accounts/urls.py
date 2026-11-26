from django.urls import path

from accounts.admin_views import (
    AdminUserListView,
    AdminUserDetailView,
    AdminUserToggleActiveView,
    AdminUserUpdateView,
    AdminLoginView, 
    AdminUserPasswordView,
    AdminUserDeleteView,
    AdminUserCreateView
    
)

from accounts.notifications.views import (
    NotificationListView,
    NotificationMarkReadView,
    NotificationMarkAllReadView,
    NotificationDeleteView,
    PushSubscriptionCreateView,
    PushSubscriptionDeleteView,
    
)

from .views import (
    MyProfileView,
    ChangePasswordView,
    SupportRequestCreateView
)


urlpatterns = [
    #NOTIFICATION
        path(
        "notifications/",
        NotificationListView.as_view(),
        name="notification-list",
    ),

    path(
        "notifications/<int:id>/read/",
        NotificationMarkReadView.as_view(),
        name="notification-mark-read",
    ),

    path(
        "notifications/read-all/",
        NotificationMarkAllReadView.as_view(),
        name="notification-mark-all-read",
    ),

    path(
        "notifications/<int:id>/",
        NotificationDeleteView.as_view(),
        name="notification-delete",
    ),

    # Web Push
    path(
        "push-subscriptions/",
        PushSubscriptionCreateView.as_view(),
        name="push-subscription-create",
    ),

    path(
        "push-subscriptions/<int:id>/",
        PushSubscriptionDeleteView.as_view(),
        name="push-subscription-delete",
    ),
    # =========================
    # Admin Users
    # =========================
    
    path(
        "admin/login/",
        AdminLoginView.as_view(),
        name="admin-login",
    ),

    path(
        "admin/users/",
        AdminUserListView.as_view(),
        name="admin-users",
    ),

    path(
        "admin/users/create/",
        AdminUserCreateView.as_view(),
        name="admin-user-create",
    ),

    path(
        "admin/users/<int:id>/",
        AdminUserDetailView.as_view(),
        name="admin-user-detail",
    ),

    path(
        "admin/users/<int:id>/update/",
        AdminUserUpdateView.as_view(),
        name="admin-user-update",
    ),

    path(
        "admin/users/<int:id>/toggle-active/",
        AdminUserToggleActiveView.as_view(),
        name="admin-user-toggle-active",
    ),

    path(
        "admin/users/<int:id>/password/",
        AdminUserPasswordView.as_view(),
        name="admin-user-password",
    ),

    path(
        "admin/users/<int:id>/delete/",
        AdminUserDeleteView.as_view(),
        name="admin-user-delete",
    ),
    # =========================
    # User
    # =========================
    path(
        "support/",
        SupportRequestCreateView.as_view(),
        name="support-create",
    ),
    path(
        "profile/",
        MyProfileView.as_view(),
        name="my-profile",
    ),

    path(
        "change-password/",
        ChangePasswordView.as_view(),
        name="change-password",
    ),
]