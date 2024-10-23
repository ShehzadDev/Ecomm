from django.test import TestCase
from django.utils import timezone
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


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpassword"
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.check_password("testpassword"))

    def test_user_str(self):
        self.assertEqual(str(self.user), "test@example.com")


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpassword"
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            phone_number="1234567890",
            date_of_birth="1990-01-01",
            address="123 Test Address",
        )

    def test_user_profile_creation(self):
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.phone_number, "1234567890")
        self.assertEqual(self.profile.date_of_birth, "1990-01-01")
        self.assertEqual(self.profile.address, "123 Test Address")

    def test_user_profile_str(self):
        self.assertEqual(str(self.profile), "testuser's profile")


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Electronics", slug="electronics")

    def test_category_creation(self):
        self.assertEqual(self.category.name, "Electronics")
        self.assertEqual(self.category.slug, "electronics")

    def test_category_str(self):
        self.assertEqual(str(self.category), "Electronics")


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Electronics", slug="electronics")
        self.product = Product.objects.create(
            name="Laptop",
            slug="laptop",
            description="A powerful laptop.",
            price=999.99,
            category=self.category,
            inventory_count=10,
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Laptop")
        self.assertEqual(self.product.category, self.category)

    def test_product_str(self):
        self.assertEqual(str(self.product), "Laptop")


class ProductVariantModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Electronics", slug="electronics")
        self.product = Product.objects.create(
            name="Laptop",
            slug="laptop",
            description="A powerful laptop.",
            price=999.99,
            category=self.category,
            inventory_count=10,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            variant_name="Color",
            variant_value="Silver",
            price=999.99,
            stock_count=5,
        )

    def test_product_variant_creation(self):
        self.assertEqual(self.variant.product, self.product)
        self.assertEqual(self.variant.variant_name, "Color")
        self.assertEqual(self.variant.variant_value, "Silver")

    def test_product_variant_str(self):
        self.assertEqual(str(self.variant), "Color: Silver (Laptop)")


class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpassword"
        )
        self.cart = Cart.objects.create(user=self.user)

    def test_cart_creation(self):
        self.assertEqual(self.cart.user, self.user)

    def test_cart_str(self):
        self.assertEqual(str(self.cart), "Cart of testuser")


class CartItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpassword"
        )
        self.cart = Cart.objects.create(user=self.user)
        self.category = Category.objects.create(name="Electronics", slug="electronics")
        self.product = Product.objects.create(
            name="Laptop",
            slug="laptop",
            description="A powerful laptop.",
            price=999.99,
            category=self.category,
            inventory_count=10,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            variant_name="Color",
            variant_value="Silver",
            price=999.99,
            stock_count=5,
        )
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product_variant=self.variant,
            quantity=1,
            price_at_time=999.99,
        )

    def test_cart_item_creation(self):
        self.assertEqual(self.cart_item.cart, self.cart)
        self.assertEqual(self.cart_item.product_variant, self.variant)
        self.assertEqual(self.cart_item.quantity, 1)

    def test_cart_item_str(self):
        self.assertEqual(str(self.cart_item), "Color: Silver x 1 in cart")


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpassword"
        )
        self.order = Order.objects.create(
            user=self.user,
            total_amount=99.99,
        )

    def test_order_creation(self):
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.total_amount, 99.99)

    def test_order_str(self):
        self.assertEqual(str(self.order), "Order {} by testuser".format(self.order.id))


class OrderItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpassword"
        )
        self.order = Order.objects.create(
            user=self.user,
            total_amount=99.99,
        )
        self.category = Category.objects.create(name="Electronics", slug="electronics")
        self.product = Product.objects.create(
            name="Laptop",
            slug="laptop",
            description="A powerful laptop.",
            price=999.99,
            category=self.category,
            inventory_count=10,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            variant_name="Color",
            variant_value="Silver",
            price=999.99,
            stock_count=5,
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product_variant=self.variant,
            quantity=1,
            price_at_time=999.99,
        )

    def test_order_item_creation(self):
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.product_variant, self.variant)

    def test_order_item_str(self):
        self.assertEqual(str(self.order_item), "Color: Silver x 1 in order")


class PaymentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpassword"
        )
        self.order = Order.objects.create(
            user=self.user,
            total_amount=99.99,
        )
        self.payment = Payment.objects.create(
            order=self.order,
            amount=99.99,
            payment_method="Credit Card",
            payment_date=timezone.now(),
        )

    def test_payment_creation(self):
        self.assertEqual(self.payment.order, self.order)
        self.assertEqual(self.payment.amount, 99.99)

    def test_payment_str(self):
        self.assertEqual(
            str(self.payment),
            "Payment {} for Order {}".format(self.payment.id, self.order.id),
        )


class ShippingAddressModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpassword"
        )
        self.address = ShippingAddress.objects.create(
            user=self.user,
            address_line1="123 Main St",
            city="Anytown",
            state="Anystate",
            postal_code="12345",
            country="USA",
            phone_number="1234567890",
        )

    def test_shipping_address_creation(self):
        self.assertEqual(self.address.user, self.user)
        self.assertEqual(self.address.city, "Anytown")

    def test_shipping_address_str(self):
        self.assertEqual(str(self.address), "Shipping Address for testuser")


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpassword"
        )
        self.category = Category.objects.create(name="Electronics", slug="electronics")
        self.product = Product.objects.create(
            name="Laptop",
            slug="laptop",
            description="A powerful laptop.",
            price=999.99,
            category=self.category,
            inventory_count=10,
        )
        self.review = Review.objects.create(
            product=self.product, user=self.user, rating=5, comment="Great product!"
        )

    def test_review_creation(self):
        self.assertEqual(self.review.product, self.product)
        self.assertEqual(self.review.user, self.user)

    def test_review_str(self):
        self.assertEqual(str(self.review), "Review for Laptop by testuser")


class WishlistModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpassword"
        )
        self.wishlist = Wishlist.objects.create(user=self.user)

    def test_wishlist_creation(self):
        self.assertEqual(self.wishlist.user, self.user)

    def test_wishlist_str(self):
        self.assertEqual(str(self.wishlist), "Wishlist of testuser")


class CouponModelTest(TestCase):
    def setUp(self):
        self.coupon = Coupon.objects.create(
            code="SAVE10",
            discount_amount=10.00,
            expiration_date=timezone.now() + timezone.timedelta(days=30),
        )

    def test_coupon_creation(self):
        self.assertEqual(self.coupon.code, "SAVE10")
        self.assertEqual(self.coupon.discount_amount, 10.00)

    def test_coupon_str(self):
        self.assertEqual(str(self.coupon), "Coupon SAVE10")


class TagModelTest(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(name="New")

    def test_tag_creation(self):
        self.assertEqual(self.tag.name, "New")

    def test_tag_str(self):
        self.assertEqual(str(self.tag), "New")
