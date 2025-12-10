# apps/orders/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import OrderViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('order/create/', OrderViewSet.as_view({'post': 'create_order'}), name='create-order'),
    path('order/<int:pk>/status/', OrderViewSet.as_view({'get': 'status'}), name='order-status'),
]
