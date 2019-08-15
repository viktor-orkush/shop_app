from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('add/<int:product_id>/', views.add_cart, name='add_cart'),
    path('remove/<int:product_id>/', views.remove_cart, name='remove_cart'),
    path('trash/<int:product_id>', views.full_remove, name='full_remove'),
    path('', views.cart_detail, name='cart_detail'),
]
