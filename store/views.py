from typing import OrderedDict
from django import forms
from django.contrib import messages
from store.forms import ReviewForm
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from .models import Product, ReviewRating
from category.models import Category
from cart.models import CartItem
from cart.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from orders.models import OrderProduct, ProductOffer
import datetime




# store

def store(request, category_slug = None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category,slug = category_slug)
        products = Product.objects.filter(category=categories, is_available = True)
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count =products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = {'products':paged_products,'product_count':product_count}
    return render(request,'store/store.html',context)




# product details

def product_detail(request, category_slug, product_slug,offer_price=0):

    try:
        single_product =  Product.objects.get(category__slug = category_slug, slug = product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request),product = single_product).exists()

        if single_product.off_price is not None:
            offer_price = single_product.price - single_product.off_price
            expairy = str(datetime.datetime.now().date())
            print('today date',expairy)
            product_offers = ProductOffer.objects.all()

            for i in product_offers:
                if i.valid_to < expairy:
                    products = Product.objects.get(id=i.product.id)
                    products.off_price = None
                    products.off_percentage = None
                    products.save(update_fields = ['off_price','off_percentage'])
    except Exception as e:
        raise e

    try:
        orderproduct = OrderProduct.objects.filter(user =  request.user, product_id = single_product.id).exists()
    except OrderProduct.DoesNotExist:
        orderproduct = None

    reviews = ReviewRating.objects.filter(product_id = single_product.id, status = True)

    context = {
        'offer_price':offer_price,
        'single_product':single_product,
        'in_cart' : in_cart,
        'orderproduct' : orderproduct,
        'reviews' : reviews,
        }
    return render(request,'store/product_detail.html',context)




# search

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products =Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {
        'products' : products,
        'product_count' : product_count,
        }
    return render(request,'store/store.html',context)




# review submission

def submit_review(request,pk):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id = request.user.id,product__id = pk)
            form = ReviewForm(request.POST,instance=reviews)
            form.save()
            messages.success(request,'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = pk
                data.user_id = request.user.id
                data.save()
                messages.success(request,'Thank you! Your review has been submited.')
                return redirect(url)



# creating refferel links for user

from accounts.models import Refferel

def ref_home(request,*args, **kwargs):
    code = str(kwargs.get('ref_code'))
    original_code = 'http://127.0.0.1:8000/store/' + code
    try:
        refferel = Refferel.objects.get(code = original_code)
        request.session['ref_profile'] = refferel.id
    except:
        pass
    products = Product.objects.all().filter(is_available=True)
    context = {'products':products,}
    return render(request,'home.html',context)