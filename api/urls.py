from django.urls import path, include
from .views import (
    RegisterAPIView,
    UserProfileView,
    CategoryViewSet,
    ProductViewSet,
    ProductVariantViewSet,
    CartViewSet,
    OrderViewSet,
    PaymentViewSet,
    ShippingAddressViewSet,
)
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


router = DefaultRouter()

router.register("categories", CategoryViewSet, basename="category")
router.register("products", ProductViewSet, basename="product")
router.register("variants", ProductVariantViewSet, basename="variant")
router.register("carts", CartViewSet, basename="cart")
router.register("orders", OrderViewSet, basename="order")
router.register("payments", PaymentViewSet, basename="payment")
router.register("addresses", ShippingAddressViewSet, basename="address")


urlpatterns = [
    path("api/users/register/", RegisterAPIView.as_view(), name="register"),
    path("api/users/login/", TokenObtainPairView.as_view(), name="login"),
    path("api/users/profile/", UserProfileView.as_view(), name="profile"),
    path("api/users/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include(router.urls)),
]
