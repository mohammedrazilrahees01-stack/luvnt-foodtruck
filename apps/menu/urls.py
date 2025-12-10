# apps/menu/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import MenuItemViewSet, ComboViewSet, ShopMenuViewSet

router = DefaultRouter()
router.register(r'items', MenuItemViewSet, basename='menuitem')
router.register(r'combos', ComboViewSet, basename='combo')
router.register(r'shop', ShopMenuViewSet, basename='shopmenu')  # /api/menu/shop/{pk}/menu/

urlpatterns = [
    path('', include(router.urls)),
]
