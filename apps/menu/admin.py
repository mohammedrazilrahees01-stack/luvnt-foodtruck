from django.contrib import admin
from .models import Category, MenuItem, ItemVariant, Addon, Combo, ComboItem

admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(ItemVariant)
admin.site.register(Addon)
admin.site.register(Combo)
admin.site.register(ComboItem)
