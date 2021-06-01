from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from store.models import Product,Variation
from .models import Cart,CartItem
from orders.models import CouponDiscount, UserAddress
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required



# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart



# add cart

def add_cart(request,product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)

    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        is_cart_item_exists = CartItem.objects.filter(product=product, user = current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)

            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
                
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id  = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                # cart_item.quantity += 1
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation) 
            cart_item.save()
        return redirect('cart')


    #if the user is not authenticated
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        
        try:
            cart = Cart.objects.get(cart_id= _cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()


        is_cart_item_exists = CartItem.objects.filter(product=product,cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)

            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            print(ex_var_list)

            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id  = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                # cart_item.quantity += 1
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation) 
            cart_item.save()
        return redirect('cart')




# def remove cart

def remove_cart(request,product_id, cart_item_id):
    
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product,user=request.user,id=cart_item_id)    
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_item = CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
        if cart_item.quantity > 1 :
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')




# remove cart item

def remove_cart_item(request,product_id, cart_item_id):
    product = get_object_or_404(Product,id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)    
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')



# cart items

def cart(request, total = 0, quantity = 0, cart_items = None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user,is_active =True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active =True)
        for cart_item in cart_items:
            if cart_item.product.off_price is not None:
                
                total += ((cart_item.product.price - cart_item.product.off_price) * cart_item.quantity)
                quantity += cart_item.quantity 
            else:
                total += (cart_item.product.price * cart_item.quantity)
                quantity += cart_item.quantity 

        tax = (5 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total' : grand_total,
    }
    return render(request,'store/cart.html',context)



# checkout

@login_required(login_url='login')
def checkout(request, total = 0, quantity = 0, cart_items = None, user_address = None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user,is_active =True)
            user_address = UserAddress.objects.filter(user = request.user)
            

        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active =True)
            
        for cart_item in cart_items:

            if cart_item.product.off_price is not None:
                
                total += ((cart_item.product.price - cart_item.product.off_price) * cart_item.quantity)
                quantity += cart_item.quantity 

            else:
                total += (cart_item.product.price * cart_item.quantity)
                quantity += cart_item.quantity 

        tax = (5 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    context = {
        'user_address' : user_address,
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total' : grand_total,
    }
    return render(request,'store/checkout.html',context)




# redeem your coupon here
from orders.models import RefCoupon

def coupon_redeem(request):

    if request.method == 'POST':
        coupon_code = request.POST['coupon_code']
        coupons = CouponDiscount.objects.filter(coupon_code=coupon_code)
        ref_coup = RefCoupon.objects.filter(coupon_code=coupon_code)
        if ref_coup:
            for i in ref_coup:
                i.is_active = True
                print('coupon is not activated ')
                i.save(update_fields = ['is_active'])
                print('coupon is activated')
        
        if coupons:
            for i in coupons:
                i.is_active = True
                print('coupon is not activated ')
                i.save(update_fields = ['is_active'])
                print('coupon is activated')
        else:
            print('not actived')

    return redirect('place_order')



# add address

def add_address(request):

    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        address_line_1 = request.POST['address_line_1']
        address_line_2 = request.POST['address_line_2']
        city = request.POST['city']
        state = request.POST['state']
        country = request.POST['country']

        user_address = UserAddress(

            user = request.user,
            first_name = first_name,
            last_name = last_name,
            email = email,
            phone = phone,
            address_line_1 = address_line_1,
            address_line_2 = address_line_2,
            city = city,
            state = state,
            country = country
        )

        user_address.save()
        return redirect('place_order')

    return render(request,'store/add_address.html')


# update address

def update_address(request,pk):
    user_address = UserAddress.objects.get(id=pk)
    if request.method == 'POST':
        user_address.first_name = request.POST['first_name']
        user_address.last_name = request.POST['last_name']
        user_address.email = request.POST['email']
        user_address.phone = request.POST['phone']
        user_address.address_line_1 = request.POST['address_line_1']
        user_address.address_line_2 = request.POST['address_line_2']
        user_address.city = request.POST['city']
        user_address.state = request.POST['state']
        user_address.country = request.POST['country']
        user_address.save()
        return redirect('place_order')
    context = {'user_address':user_address}
    return render(request,'store/update_address.html',context)

def delete_address(request,pk):
    user_address = UserAddress.objects.filter(id=pk)
    user_address.delete()
    return redirect('place_order')