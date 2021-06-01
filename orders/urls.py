from django.urls import path
from . import views


urlpatterns = [
    path('place_order/',views.place_order,name="place_order"),
    path('payments',views.payments,name="payments"),
    path('paypal_payment/',views.paypal_payment,name="paypal_payment"),
    path('razorpay_payment/',views.razorpay_payment,name="razorpay_payment"),
    path('order_complete/',views.order_complete,name="order_complete"),
]
 