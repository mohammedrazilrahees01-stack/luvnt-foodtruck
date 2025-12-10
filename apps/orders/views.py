# apps/orders/views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from decimal import Decimal
import json

from .models import Order, OrderItem, Customer, Payment
from apps.menu.models import MenuItem
from apps.shops.models import Shop


@csrf_exempt
def create_order(request):
    """
    Very simple order creation endpoint.

    Expected JSON:
    {
      "shop_id": 1,
      "phone": "9999999999",
      "address": "Near the mall",
      "is_delivery": true,
      "customer_name": "Razil",
      "referral_code": "ABC",        # optional
      "items": [
        {"item_id": 1, "qty": 2},
        {"item_id": 2, "qty": 1}
      ]
    }
    """
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON"}, status=400)

    # 1) Get shop
    shop = get_object_or_404(Shop, pk=data.get("shop_id"))

    # 2) Create / get customer (by phone)
    phone = (data.get("phone") or "").strip()
    customer_name = data.get("customer_name") or ""
    customer = None
    if phone:
        customer, _ = Customer.objects.get_or_create(
            phone=phone,
            defaults={"name": customer_name},
        )

    # 3) Create order object (total will be calculated)
    order = Order.objects.create(
        shop=shop,
        customer=customer,
        phone=phone,
        address=data.get("address", ""),
        is_delivery=bool(data.get("is_delivery", False)),
        total=Decimal("0.00"),
    )

    items_payload = data.get("items") or []
    if not items_payload:
        order.delete()
        return JsonResponse({"detail": "No items in order"}, status=400)

    total = Decimal("0.00")

    for line in items_payload:
        item_id = line.get("item_id")
        qty = int(line.get("qty") or 1)

        menu_item = MenuItem.objects.filter(pk=item_id, shop=shop, is_visible=True).first()
        if not menu_item:
            order.delete()
            return JsonResponse(
                {"detail": f"Invalid item_id {item_id} for this shop"},
                status=400,
            )

        price = menu_item.base_price
        OrderItem.objects.create(
            order=order,
            item=menu_item,
            variant=None,
            qty=qty,
            price=price,
        )
        total += price * qty

    # 4) Apply simple referral discount (optional)
    ref_code = (data.get("referral_code") or "").strip()
    discount = Decimal("0.00")
    if ref_code:
        # just as an example – real logic can use a Referral model
        if ref_code.upper() == "A":
            discount = Decimal("5.00")

    order.total = max(Decimal("0.00"), total - discount)
    order.save()

    # 5) Create a payment record (not processed yet, just a placeholder)
    payment = Payment.objects.create(
        order=order,
        method=data.get("payment_method", "online"),
        provider_payment_id="",
        amount=order.total,
        success=False,
    )

    return JsonResponse(
        {
            "order_id": order.id,
            "total": str(order.total),
            "payment_id": payment.id,
            "message": "Order created successfully",
        },
        status=201,
    )
