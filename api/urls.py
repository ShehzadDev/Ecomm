from django.urls import path
from .views import RegisterAPIView, UserProfileView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("api/register/", RegisterAPIView.as_view(), name="register"),
    path("api/profile/", UserProfileView.as_view(), name="profile"),
    path("api/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
]
