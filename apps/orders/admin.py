from django.contrib import admin
from .models import Customer, Driver, Order, OrderItem, Payment

admin.site.register(Customer)
admin.site.register(Driver)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)


from django.contrib import admin
from .models import ReferralCode

@admin.register(ReferralCode)
class ReferralCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'type', 'value', 'active', 'uses', 'max_uses', 'expires_at', 'created_at')
    search_fields = ('code',)
