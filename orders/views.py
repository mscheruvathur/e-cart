from django.http import response
from django.shortcuts import render,redirect
from cart.models import CartItem
import datetime
from .forms import OrderForm
from .models import Order,Payment,OrderProduct, UserAddress
from store.models import Product
import json
import razorpay
from orders.models import CouponDiscount



# razorpay payment

def razorpay_payment(request):
    order = Order.objects.get(user=request.user, is_ordered=False,)

    if request.method =='POST':

        amount = int(order.order_total)
        currency = 'INR'
        client = razorpay.Client(auth=('rzp_test_geR1AvIEZJzphk','U2WRkALwpHaofKKSQYMeBlzl'))
        payment = client.order.create({'amount' : amount, 'currency':currency,'payment_capture' : '1'})


        razorpay_payment = Payment(
            user = request.user,
            payment_id = order.order_number,
            payment_method = 'Razorpay',
            amount_paid = order.order_total,
            status = 'COMPLEATED',
        )
        razorpay_payment.save()


        order.payment = razorpay_payment
        order.is_ordered = True
        order.save()
        

        cart_items = CartItem.objects.filter(user=request.user)
        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.payment = razorpay_payment
            orderproduct.user_id  = request.user.id
            orderproduct.product_id  = item.product_id
            orderproduct.quantity  = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()


            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variations.all()
            orderproduct = OrderProduct.objects.get(id=orderproduct.id)
            orderproduct.variations.set(product_variation)
            orderproduct.save()

            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()
        
        CartItem.objects.filter(user=request.user).delete()
        coupon_code = CouponDiscount.objects.filter(is_active = True)
        coupon_code.delete()
        ref_code = RefCoupon.objects.filter(is_active = True)
        ref_code.delete()

    return redirect('order_complete')



# paypal payment
from django.http import JsonResponse
def paypal_payment(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id  = request.user.id
        orderproduct.product_id  = item.product_id
        orderproduct.quantity  = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()


        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()
    
    CartItem.objects.filter(user=request.user).delete()
    coupon_code = CouponDiscount.objects.filter(is_active = True)
    coupon_code.delete()

    ref_code = RefCoupon.objects.filter(is_active = True)
    ref_code.delete()
    data={
        'order_number':order.order_number,
        'transID':payment.payment_id
    }
    
    return JsonResponse(data)


# cash payment

def payments(request):
    
    order_count = Order.objects.filter(user = request.user, is_ordered=False,).count()
    print(order_count)

    if order_count >1:
        # order = Order.objects.get(user = request.user, is_ordered=False,)
        order = Order.objects.last()
        
        payment = Payment(
            user = request.user,
            payment_id = order.order_number,
            payment_method= 'Cash on Delivery',
            amount_paid= order.order_total,
            status='COD'        
        )
        
        payment.save()
        order.Payment = payment
        order.is_ordered = True
        order.save()
    else:

        order = Order.objects.get(user = request.user, is_ordered=False,)
        payment = Payment(
            user = request.user,
            payment_id = order.order_number,
            payment_method= 'Cash on Delivery',
            amount_paid= order.order_total,
            status='COD'        
        )
        payment.save()
        order.Payment = payment
        order.is_ordered = True
        order.save()
        


    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id  = request.user.id
        orderproduct.product_id  = item.product_id
        orderproduct.quantity  = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()


        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()
    
    CartItem.objects.filter(user=request.user).delete()
    coupon_code = CouponDiscount.objects.filter(is_active = True)
    coupon_code.delete()

    ref_code = RefCoupon.objects.filter(is_active = True)
    ref_code.delete()


    return redirect('order_complete')




# order palcing

from orders.models import RefCoupon
total2 = 0
def place_order(request, total = 0, quantity = 0, coupon_co = 0, coupon_disc = 0, offer_price = 0):
    current_user = request.user


    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()


    coupon_code = CouponDiscount.objects.filter(is_active = True)
    ref_code = RefCoupon.objects.filter(is_active = True)
        

    if cart_count <= 0 :
        return redirect('store')
    
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        if cart_item.product.off_price is not None:

            if coupon_code:
                print('coupon conde is 2 ',coupon_code)
                coupon_discount = 0
                coupon_co = ''
                for i in coupon_code:
                    coupon_discount = i.coupon_price
                    coupon_co = i.coupon_code
                total += ((cart_item.product.price - cart_item.product.off_price) * cart_item.quantity)
                quantity += cart_item.quantity
                global total2
                total2 = (total/100)*int(coupon_discount)
                offer_price = total-total2
                coupon_disc = total2
            elif ref_code:
                

                coupon_discount = 0
                coupon_co = ''
                for i in ref_code:
                    coupon_discount = i.coupon_price
                    coupon_co = i.coupon_code
                total += ((cart_item.product.price - cart_item.product.off_price) * cart_item.quantity)
                quantity += cart_item.quantity
                total2 = (total/100)*int(coupon_discount)
                offer_price = total-total2
                coupon_disc = total2
                

            else:
                total += ((cart_item.product.price - cart_item.product.off_price) * cart_item.quantity)
                quantity += cart_item.quantity
            


        else:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
    if coupon_code:        
        tax = (5 * total)/100
    elif ref_code:
        tax = (5 * total)/100
    else:
        tax = (5 * total)/100
    grand_total = total + tax
    grand_total_2 = int(grand_total)*100
    g_total = grand_total
    
    if coupon_code:
        grand_total = total-total2
        grand_total_2 = int(grand_total)*100
    elif ref_code:
        grand_total = total-total2
        grand_total_2 = int(grand_total)*100

    
    if request.method == 'POST':

        address_id = request.POST.get('address_id')
        if address_id is None:
            return redirect('checkout')
        else:
            print(address_id)
            user_address = UserAddress.objects.get(id=address_id)
            data = Order()
            data.user = current_user
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            
            order = Order.objects.get(user=current_user, is_ordered = False, order_number= order_number)

        context = {
            'ref_code': ref_code,
            'g_total':g_total,
            'coupon_code' : coupon_code,
            'coupon_co': coupon_co,
            'coupon_disc': coupon_disc,
            'offer_price' : offer_price,
            'user_address' : user_address,
            'order' : order,
            'cart_items' : cart_items,
            'total' : total,
            'tax' : tax,
            'grand_total' : grand_total,
            'grand_total_2' : grand_total_2,
        }

        return render(request,'orders/payments.html',context)
    else:
        return redirect('checkout')



# order compleate success page

def order_complete(request):
    return render(request,'orders/order_complete.html')

