# apps/orders/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # create order (used by your frontend / Place order button)
    path('order/create/', views.create_order, name='order-create'),

    # list recent orders by phone (optional tracking endpoint)
    path('by-phone/', views.orders_by_phone, name='orders-by-phone'),
]
