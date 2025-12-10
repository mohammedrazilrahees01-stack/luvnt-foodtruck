# apps/orders/serializers.py
from rest_framework import serializers
from .models import Order, OrderItem, Customer, Driver, Payment
from apps.menu.serializers import MenuItemSerializer, ItemVariantSerializer, AddonSerializer
from apps.menu.models import MenuItem, ItemVariant, Addon

class OrderItemInputSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    addon_ids = serializers.ListField(child=serializers.IntegerField(), required=False, allow_empty=True)
    qty = serializers.IntegerField(min_value=1, default=1)

class OrderCreateSerializer(serializers.Serializer):
    shop_id = serializers.IntegerField()
    phone = serializers.CharField(max_length=30)
    address = serializers.CharField(allow_blank=True, required=False)
    is_delivery = serializers.BooleanField(default=False)
    scheduled_for = serializers.DateTimeField(required=False, allow_null=True)
    customer_name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    customer_email = serializers.EmailField(required=False, allow_blank=True)
    items = OrderItemInputSerializer(many=True)

    def validate_shop_id(self, value):
        from apps.shops.models import Shop
        if not Shop.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Shop not found.")
        return value

    def validate(self, data):
        # basic validation: items exist
        for it in data.get('items', []):
            if not MenuItem.objects.filter(pk=it['item_id']).exists():
                raise serializers.ValidationError(f"MenuItem id={it['item_id']} not found.")
        return data

    def create(self, validated_data):
        from apps.shops.models import Shop
        shop = Shop.objects.get(pk=validated_data['shop_id'])
        customer = None
        if validated_data.get('customer_name'):
            customer = Customer.objects.create(
                name=validated_data.get('customer_name') or 'Guest',
                phone=validated_data.get('phone'),
                email=validated_data.get('customer_email') or None,
            )
        order = Order.objects.create(
            shop=shop,
            customer=customer,
            phone=validated_data.get('phone'),
            address=validated_data.get('address'),
            is_delivery=validated_data.get('is_delivery', False),
            scheduled_for=validated_data.get('scheduled_for', None),
            total=0
        )

        total = 0
        for it in validated_data['items']:
            item = MenuItem.objects.get(pk=it['item_id'])
            price = item.base_price
            if it.get('variant_id'):
                variant = ItemVariant.objects.get(pk=it['variant_id'])
                price = price + variant.price_delta
            else:
                variant = None
            addons = []
            if it.get('addon_ids'):
                for aid in it['addon_ids']:
                    a = Addon.objects.get(pk=aid)
                    price += a.price
                    addons.append(a)
            qty = it.get('qty', 1)
            line_price = price * qty
            OrderItem.objects.create(
                order=order,
                item=item,
                variant=variant,
                qty=qty,
                price=price
            )
            # attach addons after item creation
            if addons:
                oi = order.items.last()
                oi.addons.set(addons)
            total += line_price

        order.total = total
        order.save()
        return order

class OrderItemSerializer(serializers.ModelSerializer):
    item = MenuItemSerializer(read_only=True)
    variant = ItemVariantSerializer(read_only=True)
    addons = AddonSerializer(many=True, read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'item', 'variant', 'addons', 'qty', 'price')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ('id','shop','customer','phone','address','is_delivery','scheduled_for','status','total','driver','items','created_at')

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('id','order','method','provider_payment_id','amount','paid_at','success')
