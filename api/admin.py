from django.contrib import admin
from .models import (
    User,
    UserProfile,
    Category,
    Product,
    ProductVariant,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Payment,
    ShippingAddress,
    Review,
    Wishlist,
    Coupon,
    Tag,
)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "date_joined",
    )
    list_filter = ("is_active", "is_staff")
    search_fields = ("email", "username")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_active", "is_staff")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If adding a new user
            obj.set_password(form.cleaned_data["password1"])
        super().save_model(request, obj, form, change)


admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(ShippingAddress)
admin.site.register(Review)
admin.site.register(Wishlist)
admin.site.register(Coupon)
admin.site.register(Tag)
