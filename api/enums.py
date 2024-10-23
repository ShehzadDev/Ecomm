from enum import Enum


class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    @classmethod
    def choices(cls):
        return [(tag.value, tag.name.capitalize()) for tag in cls]


class OrderStatus(Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELED = "canceled"

    @classmethod
    def choices(cls):
        return [(tag.value, tag.name.capitalize()) for tag in cls]


class PaymentMethod(Enum):
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"

    @classmethod
    def choices(cls):
        return [(tag.value, tag.name.capitalize()) for tag in cls]
