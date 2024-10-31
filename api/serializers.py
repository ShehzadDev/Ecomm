from rest_framework import serializers
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


class RegisterSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=False, max_length=15)
    profile_picture = serializers.ImageField(required=False)
    address = serializers.CharField(required=False)
    date_of_birth = serializers.DateField(required=False)

    password = serializers.CharField(write_only=True)
    date_joined = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "date_joined",
            "password",
            "phone_number",
            "profile_picture",
            "address",
            "date_of_birth",
        ]

    def create(self, validated_data):
        phone_number = validated_data.pop("phone_number", None)
        profile_picture = validated_data.pop("profile_picture", None)
        address = validated_data.pop("address", None)
        date_of_birth = validated_data.pop("date_of_birth", None)

        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )

        UserProfile.objects.create(
            user=user,
            phone_number=phone_number,
            date_of_birth=date_of_birth,
            profile_picture=profile_picture,
            address=address,
        )

        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["phone_number", "address", "date_of_birth", "profile_picture"]


class UserProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "date_joined",
            "profile",
        ]
        read_only_fields = ["email", "username", "date_joined"]

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)

        profile = instance.profile

        profile_data = validated_data.get("profile")

        for field in profile_data:
            value = profile_data.get(field)
            if value is not None:
                setattr(profile, field, value)

        profile.save()
        return instance


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "parent", "subcategories"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )
    tags = TagSerializer(many=True, read_only=True)
    tags_id = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, source="tags", write_only=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "price",
            "discount_price",
            "category",
            "category_id",
            "tags",
            "tags_id",
            "inventory_count",
            "is_active",
            "created_at",
            "updated_at",
        ]


class ProductVariantSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "product",
            "product_id",
            "variant_name",
            "variant_value",
            "price",
            "stock_count",
        ]


class CartItemSerializer(serializers.ModelSerializer):
    product_variant = ProductVariantSerializer(read_only=True)
    product_variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all(), source="product_variant", write_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product_variant",
            "product_variant_id",
            "quantity",
            "price_at_time",
        ]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "created_at", "updated_at", "items"]


class OrderItemSerializer(serializers.ModelSerializer):
    product_variant = ProductVariantSerializer(read_only=True)
    product_variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all(), source="product_variant", write_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "order",
            "product_variant",
            "product_variant_id",
            "quantity",
            "price_at_time",
        ]


class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.ReadOnlyField()
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "order_status",
            "payment_status",
            "total_amount",
            "discounted_amount",
            "created_at",
            "updated_at",
            "items",
            "order_items",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "payment_method",
            "amount",
            "payment_status",
            "payment_date",
        ]


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = [
            "id",
            "user",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "postal_code",
            "country",
            "phone_number",
        ]


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "user",
            "rating",
            "comment",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class WishlistSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = ["id", "user", "products"]


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ["id", "code", "discount_amount", "is_active", "expiration_date"]
