from django.contrib import admin
from django.urls import path, include
from apps.core import views as core_views

urlpatterns = [
    path('', core_views.frontend, name='frontend'),   # your frontend
    path('api/menu/', include('apps.menu.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('admin/', admin.site.urls),
]
