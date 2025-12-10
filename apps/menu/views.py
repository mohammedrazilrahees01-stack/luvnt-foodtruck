# apps/menu/views.py
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category, MenuItem, Combo
from .serializers import CategorySerializer, MenuItemSerializer, ComboSerializer
from apps.shops.models import Shop
from django.shortcuts import get_object_or_404

class ShopMenuViewSet(viewsets.GenericViewSet):
    """
    Use: GET /api/shops/{shop_slug}/menu/  -> returns categories + items
    """
    serializer_class = CategorySerializer

    @action(detail=True, methods=['get'], url_path='menu')
    def menu(self, request, pk=None):
        shop = get_object_or_404(Shop, pk=pk)
        categories = Category.objects.filter(shop=shop).order_by('order', 'name')
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)

class MenuItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MenuItem.objects.filter(is_visible=True).select_related('shop')
    serializer_class = MenuItemSerializer

class ComboViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Combo.objects.all().select_related('shop')
    serializer_class = ComboSerializer
