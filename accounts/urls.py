from cart.views import delete_address
from accounts.utils import generate_ref_code
from os import name
from django.urls import path
from . import views

urlpatterns = [
    # path('delete_product/<int:id>/',views.delete_product,"delete_product"),
    path('register/',views.register,name="register"),
    path('login/',views.login,name="login"),
    path('otp_login/',views.otp_login,name="otp_login"),
    path('enter_otp',views.enter_otp,name="enter_otp"),
    path('logout/',views.logout,name="logout"),
    path('activate/<uidb64>/<token>',views.activate,name="activate"),
    path('forgotPassword',views.forgotPassword,name="forgotPassword"),
    path('resetpassword_validate/<uidb64>/<token>',views.resetpassword_validate,name="resetpassword_validate"),
    path('resetPassword',views.resetPassword,name="resetPassword"),
    path('dashboard/',views.dashboard,name="dashboard"),
    path('',views.dashboard,name="dashboard"),
    path('edit_profile/',views.edit_profile,name="edit_profile"),
    path('change_password/',views.change_password,name="change_password"),
    
    
    

    #------------------- ADMIN SIDE -------------------
    
    path('admin_login/',views.admin_login,name="admin_login"),
    path('admin_panel/',views.admin_panel,name="admin_panel"),
    path('admin_logout',views.admin_logout,name="admin_logout"),
    path('product_details',views.product,name="product_details"),
    path('update_product/<int:pk>',views.update_product,name="update_product"),
    path('add_product',views.add_product,name="add_product"),
    path('view_category',views.view_category,name="view_category"),
    path('add_category',views.category,name="add_category"),
    path('variation/',views.variation,name="variation"),
    path('delete_variation/<int:pk>',views.delete_variation,name="delete_variation"),
    path('add_variation/',views.add_variation,name="add_variation"),
    path('order_management/',views.order_management,name="order_management"),
    path('user_details',views.user_details,name="user_details"),
    path('block_user/<int:pk>',views.block_user,name="block_user"),
    path('unblock_user/<int:pk>',views.unblock_user,name="unblock_user"),
    path('delete_user/<int:pk>',views.delete_user,name="delete_user"),
    path('delete_pro/<int:pk>',views.delete_pro,name="delete_pro"),
    path('my_orders/',views.my_orders,name="my_orders"),
    path('cancel_order/<int:pk>',views.cancel_order,name="cancel_order"),
    path('user_product_cancel/<int:pk>',views.user_product_cancel,name="user_product_cancel"),
    path('sales_management/',views.sales_management,name="sales_management"),
    path('period_report/',views.period_report,name="period_report"),
    path('monthly_report/',views.monthly_report,name="monthly_report"),
    path('yearly_report/',views.yearly_report,name="yearly_report"),
    path('product_offer/',views.product_offer,name="product_offer"),
    path('category_offer/',views.category_offer,name="category_offer"),
    path('export_pdf/',views.export_pdf,name="export_pdf"),
    path('coupon_discount/',views.coupon_discount,name="coupon_discount"),
    path('delete_coupon/<int:pk>/',views.delete_coupon,name="delete_coupon"),
    path('delete_category_offer/<int:pk>/',views.delete_category_offer,name="delete_category_offer"),
    path('delete_product_offer/<int:pk>/',views.delete_product_offer,name="delete_product_offer"),
    path('refferels/',views.refferels,name="refferels"),
    path('admin_base/',views.admin_base,name="admin_base"),
]
