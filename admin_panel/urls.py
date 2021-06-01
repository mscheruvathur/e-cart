from django.urls import path
from . import views
urlpatterns = [
    path('',views.admin_panel,name="admin_panel"),
    path('product_details/',views.admin_panel,name="product"),
    path('add_product',views.admin_panel,name="add_product"),
    path('add_category',views.admin_panel,name="add_category"),
    path('block/<int:pk>',views.block_user,name="block_user"),
    path('unblock/<int:pk>',views.unblock_user,name="unblock_user"),
    path('delete/<int:pk>',views.delete_user,name="delete_user"),
]
