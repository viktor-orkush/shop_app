from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('add/<int:product_id>/', views.add_cart, name='add_cart'),
    path('delete/<int:product_id>/', views.delete_cart, name='delete_cart'),
    path('trash/<int:product_id>', views.trash_cart, name='trash_cart'),
    path('', views.cart_detail, name='cart_detail'),
]
