from django.urls import path
from ecommerseapp import views

urlpatterns = [
    path('', views.index, name='index'),
]
