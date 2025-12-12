from django.urls import path
from . import views

urlpatterns = [
    path('auth/firebase-login/', views.firebase_login, name='firebase-login'),
]
