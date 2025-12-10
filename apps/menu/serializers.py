# apps/menu/serializers.py
from rest_framework import serializers
from .models import Category, MenuItem, ItemVariant, Addon, Combo, ComboItem

class ItemVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemVariant
        fields = ('id', 'name', 'price_delta', 'sku')

class AddonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Addon
        fields = ('id', 'name', 'price')

class MenuItemSerializer(serializers.ModelSerializer):
    variants = ItemVariantSerializer(many=True, read_only=True)
    addons = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = ('id', 'name', 'description', 'base_price', 'image', 'is_visible', 'is_combo', 'variants', 'addons')

    def get_addons(self, obj):
        # return addons available at the shop level
        qs = obj.shop.addons.all()
        return AddonSerializer(qs, many=True).data

class CategorySerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'order', 'items')

class ComboItemSerializer(serializers.ModelSerializer):
    item = MenuItemSerializer(read_only=True)
    class Meta:
        model = ComboItem
        fields = ('id', 'item', 'required')

class ComboSerializer(serializers.ModelSerializer):
    combo_items = ComboItemSerializer(many=True, read_only=True)
    class Meta:
        model = Combo
        fields = ('id', 'name', 'base_price', 'combo_items')
