from django.shortcuts import render
from store.models import Product
from orders.models import ProductOffer,CategoryOffer

def home(request):
    categoy_off = CategoryOffer.objects.all()
    products = Product.objects.all().filter(is_available=True)
    context = {'products':products,}
    return render(request,'home.html',context)