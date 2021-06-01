from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart,name="cart"),
    path('add_cart/<int:product_id>/',views.add_cart,name="add_cart"),
    path('remove_cart/<int:product_id>/<int:cart_item_id>/',views.remove_cart,name="remove_cart"),
    path('remove_cart_item/<int:product_id>/<int:cart_item_id>/',views.remove_cart_item,name="remove_cart_item"),
    path('checkout/',views.checkout,name="checkout"),
    path('add_address/',views.add_address,name="add_address"),
    path('update_address/<int:pk>/',views.update_address,name="update_address"),
    path('delete_address/<int:pk>/',views.delete_address,name="delete_address"),
    path('redeem_coupon/',views.coupon_redeem,name="coupon_redeem"),
]
