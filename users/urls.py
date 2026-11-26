from django.urls import path
from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    GoogleTokenLoginView,
    GoogleProfileCompletionView,
    LogoutView
)


urlpatterns = [
    path(
        "google/login/",
        GoogleTokenLoginView.as_view(),
        name="google-token-login",
    ),
    path(
        "google/complete-profile/",
        GoogleProfileCompletionView.as_view(),
        name="google-complete-profile",
    ),
    path('jwt/create/', CustomTokenObtainPairView.as_view()),
    path('jwt/refresh/', CustomTokenRefreshView.as_view()),
    path('jwt/verify/', CustomTokenVerifyView.as_view()),
    path('logout/', LogoutView.as_view()),
]
