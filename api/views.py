from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status, generics, viewsets
from rest_framework.decorators import action
from .serializers import *
from .models import *
from rest_framework import filters
from .enums import OrderStatus, PaymentStatus, PaymentMethod
from .pagination import CustomPagination
from django.utils import timezone
from django.db.utils import IntegrityError


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "User registered successfully."}, status=status.HTTP_201_CREATED
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsAdminUser()]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = CustomPagination

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "is_active", "price"]
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_at"]

    def get_permissions(self):
        if self.action in ["create", "update", "destroy", "add_variant"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @action(
        detail=True,
        methods=["get"],
        url_path="variants",
    )
    def variants(self, request, pk=None):
        product = self.get_object()
        variants = ProductVariant.objects.filter(product=product)

        serializer = ProductVariantSerializer(variants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        url_path="add-variants",
    )
    def add_variant(self, request, pk=None):
        product = self.get_object()
        serializer = ProductVariantSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], url_path="reviews")
    def reviews(self, request, pk=None):
        product = self.get_object()
        reviews = Review.objects.filter(product=product)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="add-reviews")
    def add_review(self, request, pk=None):
        product = self.get_object()
        serializer = ReviewSerializer(data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save(product=product, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [IsAdminUser]


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def retrieve(self, request, pk=None):
        try:
            cart = self.queryset.get(id=pk, user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {"detail": "Cart not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="add-item")
    def add_item(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        message = (
            "New cart created and item added."
            if created
            else "Item added to existing cart."
        )

        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(cart=cart)

        return Response({"message": message}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["put"], url_path="update")
    def update_item(self, request):
        item_id = request.data.get("item_id")

        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)

            serializer = CartItemSerializer(item, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                {"message": "Item updated in cart."}, status=status.HTTP_200_OK
            )
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Item not found in your cart."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["delete"], url_path="remove")
    def remove_item(self, request):
        item_id = request.data.get("item_id")

        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
            item.delete()

            return Response(
                {"message": "Item removed from cart."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Item not found in your cart."},
                status=status.HTTP_404_NOT_FOUND,
            )


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    @action(detail=False, methods=["post"], url_path="create")
    def create_order(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)

        if not cart or not cart.items.exists():
            return Response(
                {"error": "No items in cart to create an order."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total_amount = sum(
            item.price_at_time * item.quantity for item in cart.items.all()
        )

        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            order_status=OrderStatus.PENDING.value,
            payment_status=PaymentStatus.PENDING.value,
        )

        order_items = []
        for cart_item in cart.items.all():
            order_items.append(
                OrderItem(
                    order=order,
                    product_variant=cart_item.product_variant,
                    quantity=cart_item.quantity,
                    price_at_time=cart_item.price_at_time,
                )
            )
            OrderItem.objects.bulk_create(order_items)
            cart.items.all().delete()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["put"], url_path="cancel")
    def cancel_order(self, request, pk=None):
        order = self.get_object()
        if order.order_status != OrderStatus.PENDING.value:
            return Response(
                {"error": "Only pending orders can be canceled."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.order_status = OrderStatus.CANCELED.value
        order.save()
        return Response(
            {"message": "Order cancelled successfully."}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["get"], url_path="items")
    def list_items(self, request, pk=None):
        order = self.get_object()
        items = OrderItem.objects.filter(order=order)
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="apply")
    def apply(self, request, pk=None):
        coupon_id = request.data.get("coupon")

        try:
            coupon = Coupon.objects.get(id=coupon_id)
            order = Order.objects.get(id=pk, user=request.user)

            order.apply_coupon(coupon)
            message = "Coupon applied successfully."

            order.save()

            return Response(
                {
                    "message": message,
                    "order": OrderSerializer(order).data,
                },
                status=status.HTTP_200_OK,
            )
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Coupon.DoesNotExist:
            return Response(
                {"error": "Coupon not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except IntegrityError:
            return Response(
                {"error": "This coupon is already applied to the order."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(order__user=self.request.user)

    def create(self, request, *args, **kwargs):
        order_id = request.data.get("order")
        payment_method = request.data.get("payment_method")
        amount = request.data.get("amount")

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {
                    "detail": "Order not found or you do not have permission to access it."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        payment = Payment.objects.create(
            order=order,
            payment_method=payment_method,
            amount=amount,
            payment_status="PENDING",
            payment_date=timezone.now(),
        )

        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        try:
            payment = self.get_object()
            if payment.order.user != request.user:
                return Response(
                    {"detail": "You do not have permission to access this payment."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            return Response(PaymentSerializer(payment).data)
        except Payment.DoesNotExist:
            return Response(
                {"detail": "Payment not found."}, status=status.HTTP_404_NOT_FOUND
            )


class ShippingAddressViewSet(viewsets.ModelViewSet):
    queryset = ShippingAddress.objects.all()
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        try:
            shipping_address = self.get_object()
            if shipping_address.user != request.user:
                return Response(
                    {"detail": "You do not have permission to edit this address."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = self.get_serializer(shipping_address, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except ShippingAddress.DoesNotExist:
            return Response(
                {"detail": "Shipping address not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def destroy(self, request, *args, **kwargs):
        try:
            shipping_address = self.get_object()
            if shipping_address.user != request.user:
                return Response(
                    {"detail": "You do not have permission to delete this address."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            self.perform_destroy(shipping_address)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ShippingAddress.DoesNotExist:
            return Response(
                {"detail": "Shipping address not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class ReviewsViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminUser]


class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["list", "add", "remove"]:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def add(self, request):
        product_id = request.data.get("product_id")

        try:
            product = Product.objects.get(id=product_id)
            wishlist, created = Wishlist.objects.get_or_create(user=request.user)

            wishlist.products.add(product)
            wishlist.save()

            return Response(
                {"message": "Product added to wishlist."},
                status=status.HTTP_201_CREATED,
            )
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Wishlist.DoesNotExist:
            wishlist = Wishlist.objects.create(user=request.user)
            wishlist.products.add(product)
            wishlist.save()

            return Response(
                {"message": "New wishlist created and product added."},
                status=status.HTTP_201_CREATED,
            )

    @action(detail=False, methods=["delete"])
    def remove(self, request):
        product_id = request.data.get("product_id")

        try:
            product = Product.objects.get(id=product_id)
            wishlist = Wishlist.objects.get(user=request.user)
            wishlist.products.remove(product)
            wishlist.save()
            return Response(
                {"message": "Product removed from wishlist."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Wishlist.DoesNotExist:
            return Response(
                {"error": "Wishlist not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

    def get_permissions(self):
        if self.action in ["list", "create", "update", "destroy"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminUser]
