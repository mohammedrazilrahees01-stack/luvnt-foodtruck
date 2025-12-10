from django.db import models
from decimal import Decimal

class Customer(models.Model):
    # Optional link to auth.User could be added later
    user = models.OneToOneField('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"


class Driver(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30)
    vehicle = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'New'
        PREPARING = 'preparing', 'Preparing'
        READY = 'ready', 'Ready'
        OUT_FOR_DELIVERY = 'out_delivery', 'Out for delivery'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'

    shop = models.ForeignKey('shops.Shop', on_delete=models.CASCADE, related_name='orders')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=30)
    address = models.TextField(blank=True, null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.NEW)
    is_delivery = models.BooleanField(default=False)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.shop.name} - {self.get_status_display()}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey('menu.MenuItem', on_delete=models.SET_NULL, null=True)
    variant = models.ForeignKey('menu.ItemVariant', on_delete=models.SET_NULL, null=True, blank=True)
    addons = models.ManyToManyField('menu.Addon', blank=True)
    qty = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # price snapshot per unit

    def line_total(self):
        return self.price * self.qty

    def __str__(self):
        return f"{self.qty} x {self.item.name if self.item else 'Item'} (Order #{self.order.id})"


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    method = models.CharField(max_length=50)  # 'card', 'upi', 'cash'
    provider_payment_id = models.CharField(max_length=200, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(null=True, blank=True)
    success = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment {self.id} - {self.method} - {self.amount}"


# append to apps/orders/models.py

from django.utils import timezone

class ReferralCode(models.Model):
    CODE_TYPE_CHOICES = [
        ('fixed', 'Fixed amount'),
        ('percent', 'Percentage'),
    ]
    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200, blank=True)
    type = models.CharField(max_length=10, choices=CODE_TYPE_CHOICES, default='fixed')
    value = models.DecimalField(max_digits=8, decimal_places=2, help_text="Amount or percent")
    max_uses = models.PositiveIntegerField(null=True, blank=True)  # null = unlimited
    uses = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} ({self.type} {self.value})"

    def is_valid(self):
        if not self.active:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        if self.max_uses is not None and self.uses >= self.max_uses:
            return False
        return True

    def apply_discount(self, amount: float):
        """
        Return (discount_amount: float, new_total: float)
        amount should be float (or decimal convertible)
        """
        amt = float(amount)
        if self.type == 'fixed':
            discount = min(amt, float(self.value))
        else:
            discount = (float(self.value) / 100.0) * amt
        new_total = max(0.0, amt - discount)
        return round(discount, 2), round(new_total, 2)

    def increment_usage(self):
        if self.max_uses is None or self.uses < self.max_uses:
            self.uses += 1
            self.save()
