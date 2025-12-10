# apps/orders/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # POST /api/orders/order/create/
    path('order/create/', views.create_order, name='order-create'),
]
