from typing import TextIO
from django.db import models
from django.db.models.fields import IntegerField
from category.models import Category
from django.urls import reverse
from accounts.models import Account
# from accounts.forms import NewOrderProductForm

# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200,unique=True)
    description = models.TextField(max_length=500,blank=True)
    price = models.IntegerField()
    off_price = models.IntegerField(null=True)
    off_percentage = IntegerField(null=True)
    images_1 = models.ImageField(upload_to='photos/products')
    images_2 = models.ImageField(upload_to='photos/products')
    images_3 = models.ImageField(upload_to='photos/products')
    images_4 = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    created_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now = True)

    # def clean_photo(self):
    #     image_file = self.cleaned_data.get('images_1','images_2','images_3','images_4')
    #     if not image_file.name.endswith(".jpg"):
    #         raise NewOrderProductForm.ValidationError("Only .jpg image accepted")
    #     return image_file

    def get_url(self):
        return reverse('product_detail', args = [self.category.slug, self.slug])

    def __str__(self):
        return self.product_name

class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category = 'color',is_active = True)
    
    def sizes(self):
        return super(VariationManager, self).filter(variation_category = 'size',is_active = True)

variation_category_choice = (
    ('color','color'),
    ('size' ,' size'),
)

class Variation(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=200,choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value


class ReviewRating(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500,blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.subject
    
    