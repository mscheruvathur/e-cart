from typing import Text
from django.db import models
from django.db.models.base import Model
from django.db.models.fields import CharField
from accounts.models import Account
from store.models import Product,Variation,Category

# Create your models here.

class Payment(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.payment_id




class Order(models.Model):
    STATUS =(
        ('New' , 'New'),
        ('Accepted' , 'Accepted'),
        ('Completed' , 'Completed'),
        ('Cancelled' , 'Cancelled'),
    )

    user = models.ForeignKey(Account,on_delete=models.SET_NULL, null=True)
    Payment = models.ForeignKey(Payment, on_delete=models.SET_NULL,blank=True,null=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email =  models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def __str__(self):
        return self.first_name


class OrderProduct(models.Model):

    # STATUS =(
    #     ('Ordered' , 'Ordered'),
    #     ('Packed' , 'Packed'),
    #     ('Shipped' , 'Shipped'),
    #     ('Cancelled' , 'Cancelled'),
    # )

    
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    status = models.CharField(max_length=10, default='Ordered',)
    user_cancel = models.CharField(max_length=15,default=False,null=True)

    def __str__(self):
        return self.product.product_name
        



class UserAddress(models.Model):

    user = models.ForeignKey(Account,on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email =  models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    order_note = models.CharField(max_length=100, blank=True)
    created_at = models.DateField(auto_now_add=True)


    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def __str__(self):
        return self.first_name


class ProductOffer(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    offer_price = models.FloatField()
    valid_from = models.CharField(max_length=10)
    valid_to = models.CharField(max_length=10)

    def __Str__(self):
        return self.product


class CategoryOffer(models.Model):
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    offer_price = models.FloatField()
    valid_from = models.CharField(max_length=10)
    valid_to = models.CharField(max_length=10)

    def __Str__(self):
        return self.category


class CouponDiscount(models.Model):
    coupon_code = CharField(max_length=12)
    coupon_price = models.FloatField(null=True,blank=True)
    valid_from = models.CharField(max_length=10,null=True,blank=True)
    valid_to = models.CharField(max_length=10,null=True,blank=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.coupon_code


class RefCoupon(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    coupon_code = CharField(max_length=12)
    coupon_price = models.FloatField(default=10)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.coupon_code

        