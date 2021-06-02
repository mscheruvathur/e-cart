from datetime import date
from random import random
from django import forms, shortcuts
from django.core import paginator
from django.db.models import query
from django.shortcuts import get_object_or_404, render,redirect
from django.utils import encoding
from .forms import NewOrderProductForm, RegistrationForm,UserForm,UserProfileForm
from .models import Account, UserProfile, Refferel
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, response
from store.models import Product,Variation
from .forms import NewProductForm, NewCategorytForm,NewOrderProductForm,NewVariationForm
from django.contrib.sessions.models import Session
from django.views.decorators.cache import never_cache
from django.views.decorators.cache import cache_control
from cart.views import _cart_id
from cart.models import Cart , CartItem
from orders.models import CouponDiscount, OrderProduct,Order, Payment,ProductOffer,CategoryOffer,RefCoupon
from category.models import Category
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
import requests
from .sms_func import send_sms,gen_otp
from .decorator import admin_decorator
from datetime import date, timedelta
import datetime
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db.models import Sum
import uuid







# user registration

def register(request):
    if request.method == 'POST':
        profile_id = request.session.get('ref_profile')
        print('profile_id',profile_id)
        form = RegistrationForm(request.POST)
        if form.is_valid():
            if profile_id is not None:
                recommended_by_profile = Refferel.objects.get(id = profile_id)
                ref_code = str(uuid.uuid4()).replace("-", "")[:10]
                rec_code = str(uuid.uuid4()).replace("-", "")[:10]
                
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                phone_number = form.cleaned_data['phone_number']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                username = email.split('@')[0]
                user = Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username = username,password = password)
                user.phone_number = phone_number
                print(user.id)
                instance = user.save()
                registered_user = Account.objects.get(id=user.id)
                registered_profile = Refferel.objects.get(user = registered_user)
                registered_profile.recommended_by = recommended_by_profile.user
                registered_profile.save()
                coupon_1 =  RefCoupon(user=user,coupon_code = ref_code)
                coupon_1.save()
                coupon_2 =  RefCoupon(user=recommended_by_profile.user,coupon_code = rec_code)
                coupon_2.save()

                current_site = get_current_site(request)
                mail_subject = ' Please Activate Your Account'
                message = render_to_string('accounts/account_verification_email.html', {
                    'user' : user,
                    'domain' : current_site,
                    'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                    'token' : default_token_generator.make_token(user),
                })
                to_email = email
                send_email = EmailMessage(mail_subject, message, to=[to_email])
                send_email.send()
                return redirect('/accounts/login/?command=verification&email='+email)
            else:
                pass
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                phone_number = form.cleaned_data['phone_number']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                username = email.split('@')[0]
                user = Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username = username,password = password)
                user.phone_number = phone_number
                user.save()

                current_site = get_current_site(request)
                mail_subject = ' Please Activate Your Account'
                message = render_to_string('accounts/account_verification_email.html', {
                    'user' : user,
                    'domain' : current_site,
                    'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                    'token' : default_token_generator.make_token(user),
                })
                to_email = email
                send_email = EmailMessage(mail_subject, message, to=[to_email])
                send_email.send()
                return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form = RegistrationForm()
    context = {'form': form}
    return render(request,'accounts/register.html',context)


# user login 

def login(request):
    if request.method =='POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email,password=password)
        active = Account.objects.get(email=email)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))


                    cart_item = CartItem.objects.filter( user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                    
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity +=1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, 'You are Now Logged in.')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                print(query)
                params = dict(x.split('=') for x in query.split('&'))
                print(params)
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        elif active.is_active == False:
            messages.error(request, 'You were blocked')
            return redirect('login')
        else:
            messages.error(request, 'Invalid Login Credential')
            return redirect('login')
    return render(request,'accounts/login.html')





# user login with otp

random_otp = gen_otp()
msg_body = F'''
Welcome to GreatKart
Your OTP IS : {random_otp}

'''
user_mob = ''

# otp generation 

def otp_login(request):
    
    if request.method == 'POST':
        phone = request.POST['phone']
        user = Account.object.all()
        phone_num = []
        for i in user:
            x = i.phone_number
            phone_num.append(x)
        
        print(phone_num)
        if phone not in phone_num:
            messages.error(request, 'Please eneter a valid mobile number')
            return redirect('otp_login')

        else:
            user_phone = Account.object.get(phone_number=phone)
            if user_phone is not None:
                global user_mob
                user_mob = user_phone.phone_number
                send_sms(msg_body,user_phone.phone_number)
                print(user_mob)
                return redirect('enter_otp')
            else:
                messages.error(request, 'Please eneter a valid mobile number')
                return redirect('otp_login')


    return render(request,'accounts/otp_login.html')


# otp validation part

def enter_otp(request):
    if request.method == 'POST':
        otp = request.POST['otp']

        global user_mob
        phone = user_mob
        user_account = Account.object.get(phone_number = phone)
        print(user_account)

        if otp == random_otp:
            if user_account is not None:
                try:
                    cart = Cart.objects.get(cart_id = _cart_id(request))
                    is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                    if is_cart_item_exists:
                        cart_item = CartItem.objects.filter(cart=cart)

                        product_variation = []
                        for item in cart_item:
                            variation = item.variations.all()
                            product_variation.append(list(variation))


                        cart_item = CartItem.objects.filter( user=user_account)
                        ex_var_list = []
                        id = []
                        for item in cart_item:
                            existing_variation = item.variations.all()
                            ex_var_list.append(list(existing_variation))
                            id.append(item.id)
                        
                        for pr in product_variation:
                            if pr in ex_var_list:
                                index = ex_var_list.index(pr)
                                item_id = id[index]
                                item = CartItem.objects.get(id=item_id)
                                item.quantity +=1
                                item.user = user_account
                                item.save()
                            else:
                                cart_item = CartItem.objects.filter(cart=cart)
                                for item in cart_item:
                                    item.user = user_account
                                    item.save()
                except:
                    pass

                auth.login(request, user_account)
                return redirect('home')
        else:
            messages.error(request, 'Invalid OTP')
            return redirect('enter_otp')
    return render(request,'accounts/otp_enter.html')





# edit user profile

@login_required(login_url='login')
def edit_profile(request):
    # user_profile = UserProfile.objects.filter(user=request.user)
    user_profile = get_object_or_404(UserProfile, user= request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST , instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            
            profile_form.save()
            
            messages.success(request,'Your profile has been updates')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
    context = {
        'user_form' : user_form,
        'profile_form' : profile_form,
        'user_profile' : user_profile,
    }
    return render(request,'accounts/edit_profile.html',context)





# user change password

@login_required(login_url='login')
def change_password(request):
    if request.method =='POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.object.get(username__exact = request.user.username)
        
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                
                #auth.logout(request)
                messages.success(request,'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request,'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request,'Password doesnot match!')
            return redirect('change_password')
    return render(request,'accounts/change_password.html')






# user dashboard

@login_required(login_url= 'login')
def dashboard(request, rec_code = 0):
    user_profile = get_object_or_404(UserProfile, user= request.user)
    refferel = Refferel.objects.get(user_id=request.user.id)
    refferal_link = refferel.code
    orders = Order.objects.order_by('-created_at').filter(user_id = request.user.id, is_ordered=True)
    orders_count = orders.count()
    if RefCoupon.objects.filter(user = request.user ).exists():
        rec_code = RefCoupon.objects.get(user=request.user)
    

    context = {
        'user_profile':user_profile,
        'orders_count' : orders_count,
        'refferal_link':refferal_link,
        'rec_code' : rec_code,
        }
    return render(request,'accounts/dashboard.html',context)


# user orders

@login_required(login_url= 'login')
def my_orders(request):
    orders = OrderProduct.objects.filter(user=request.user)
    context = {'orders' : orders}
    return render(request,'accounts/my_orders.html',context)


# cancel order

def cancel_order(request,pk):
    order = OrderProduct.objects.get(id=pk)
    if request.method == 'POST':
        status = request.POST['status']
        order.status = status
        order.save()
        return redirect('order_management')


# cancel product

def user_product_cancel(request,pk):
    print(pk)
    order = OrderProduct.objects.get(id=pk)
    order.user_cancel = True
    print(order.user_cancel)
    order.save()
    pro = order.product.id
    product = Product.objects.get(id=pro)
    product.stock+=1
    product.save()
    return redirect('my_orders')



# user logout

@login_required(login_url= 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are Logged Out.')
    return redirect('login')




# user activation via email

def activate(request,uidb64, token):

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active =True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')




# forgot password

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.object.filter(email=email):
            user = Account.object.get(email__exact=email)
            
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Password resut email has been send to your email address.')
            return redirect('login')

        else:
            messages.error(request, 'Account doesnot exist!')
            return redirect('forgotPassword')
    return render(request,'accounts/forgotPassword.html')



# reset password validation

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.success(request,'Please resut you password')
        return redirect('resetPassword')
    else:
        messages.error(request,'This link have been expired')
        return redirect('login')



# reset password

def resetPassword(request):

    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.object.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Password reset successfull')
            return redirect('login')
        else:
            messages.error(request,'Password Donot Match')
            return redirect('resetPassword')

    else:
        return render(request,'accounts/resetPassword.html')






# admin login
# @cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)

@admin_decorator
def admin_login(request):
    
    if request.method == 'POST':
        
        uname = 'admin'
        pword = 'admin'
        username = request.POST['username']
        password = request.POST['password']
        if uname == username and password == pword:
            request.session['is_logged'] = True
            return render(request,'admin_panel_templates/admin_panel.html')
        else:
            return redirect(request,'admin_login')
    return render(request,'admin_panel_templates/login.html')




# admin panel

def admin_panel(request):    

    order=OrderProduct.objects.all()
    tptal_product = Order.objects.filter(is_ordered = True).count()
    today_order=OrderProduct.objects.filter(created_at__day=datetime.datetime.now().day).count()
    total_user = Account.objects.filter().count()
    pend=OrderProduct.objects.filter(status='Pending',user_cancel=False).count()
    accept=OrderProduct.objects.filter(status='Accepted').count()
    print(accept)
    cancelled=OrderProduct.objects.filter(status='Cancelled').count()
    print(cancelled)
    deliver=OrderProduct.objects.filter(status='Delivered').count
    user_cancelled=OrderProduct.objects.filter(user_cancel=True).count
    day1=datetime.datetime.now().day
    day2=day1-1
    day3=day2-1
    day4=day3-1
    day5=day4-1
    day6=day5-1
    day7=day6-1
    

    day1_order =OrderProduct.objects.filter(created_at__day=day1).count()
    day2_order =OrderProduct.objects.filter(created_at__day=day2).count()
    day3_order =OrderProduct.objects.filter(created_at__day=day3).count()
    day4_order =OrderProduct.objects.filter(created_at__day=day4).count()
    day5_order =OrderProduct.objects.filter(created_at__day=day5).count()
    day6_order =OrderProduct.objects.filter(created_at__day=day6).count()
    day7_order =OrderProduct.objects.filter(created_at__day=day7).count()

    sales = OrderProduct.objects.filter(status='Delivered').count()

    products = Product.objects.all()
    category_items = []
    shirt = 0
    t_shirt = 0
    pant = 0
    shoes = 0
    for i in products:
        x = i.category.category_name
        category_items.append(x)
    print(category_items)
    
    for i in category_items:
        if i == 'Shirts':
            shirt+=1
        elif i == 'Shoes':
            shoes += 1
        elif i == 'Jeans':
            pant +=1
        else:
            t_shirt+=1



    from django.db.models import Sum
    cod_amount = Payment.objects.filter(payment_method='Cash on Delivery').aggregate(Sum('amount_paid'))['amount_paid__sum']
    paypal_amount = Payment.objects.filter(payment_method='Paypal').aggregate(Sum('amount_paid'))['amount_paid__sum']
    razor_amount = Payment.objects.filter(payment_method='Razorpay').aggregate(Sum('amount_paid'))['amount_paid__sum']
    razor_amount = int(razor_amount)
    cod_amount = int(cod_amount)
    paypal_amount = int(paypal_amount)
    
    total_sales = paypal_amount+razor_amount+cod_amount
    context={
            'total_sales':total_sales,
            'total_user' : total_user,
            'tptal_product' : tptal_product,
            'new_order':today_order,
            'order':order,
            'sales':sales,
            'pend':pend,
            'accept':accept,
            'cancel':cancelled,
            'delivered':deliver,
            'user_cancelled':user_cancelled, 
            'cod_amount':cod_amount,'paypal_amount':paypal_amount,'razor_amount':razor_amount,
            'shirt' : shirt, 't_shirt' : t_shirt, 'pant' : pant,'shoes':shoes,
            'day1':day1_order,'day2':day2_order,'day3':day3_order,'day4':day4_order,'day5':day5_order,'day6':day6_order,'day7':day7_order
        }


    return render(request,'admin_panel_templates/admin_panel.html',context)





# displaying products in admin side

import json
from json import dumps
def product(request):    
    products = Product.objects.all()
    js_product_data = json.dumps(str(list(Product.objects.values())))
    context = {'products':products,'js_product_data':js_product_data}
    return render(request,'admin_panel_templates/product_details.html',context)
    

# update prduct

def update_product(request,pk):
    products = Product.objects.get(id=pk)
    if request.method == 'POST':
        products.product_name = request.POST['name']
        # products.images = request.POST.get('images')
        products.price = request.POST['price']
        products.size = request.POST['size']
        products.description = request.POST['description']
        products.slug = request.POST['slug']
        products.save()
        return redirect('update_product')
    context = {'products' : products}
    return render(request,'admin_panel_templates/update_product.html',context)
    

# add product
import base64
from django.core.files.base import ContentFile

def add_product(request):
    form = NewProductForm()
    if request.method == 'POST':
        form = NewProductForm(request.POST, request.FILES)
        if form.is_valid():
            

            product_name = form.cleaned_data['product_name']
            slug = form.cleaned_data['slug']
            description = form.cleaned_data['description']
            price = form.cleaned_data['price']
            stock = form.cleaned_data['stock']
            is_available = form.cleaned_data['is_available']
            category = form.cleaned_data['category']


            image1 = request.POST['pro_img1']
            image2 = request.POST['pro_img2']
            image3 = request.POST['pro_img3']
            image4 = request.POST['pro_img4']

            format, img1 = image1.split(';base64,')
            ext = format.split('/')[-1]
            img_data1 = ContentFile(base64.b64decode(img1), name=product_name + '1.' + ext)
            format, img2 = image2.split(';base64,')
            ext = format.split('/')[-1]
            img_data2 = ContentFile(base64.b64decode(img2), name=product_name + '2.' + ext)
            format, img3 = image3.split(';base64,')
            ext = format.split('/')[-1]
            img_data3 = ContentFile(base64.b64decode(img3), name=product_name + '3.' + ext)
            format, img4 = image4.split(';base64,')
            ext = format.split('/')[-1]
            img_data4 = ContentFile(base64.b64decode(img4), name=product_name + '4.' + ext)
            
            print('item not saved')
            product = Product(
                product_name = product_name,
                slug = slug,
                description = description,
                price = price,
                stock= stock,
                is_available = is_available,
                category = category,
                images_1 = img_data1,
                images_2 = img_data2,
                images_3 = img_data3,
                images_4 = img_data4,
            )
            product.save()
            print('item saved')


            return redirect('add_product')
    context = {'form':form}
    return render(request,'admin_panel_templates/add_product.html',context)



# delete product

def delete_pro(request,pk):
    products = Product.objects.filter(id=pk)
    products.delete()
    return redirect('product_details')



# add variations for a product

def add_variation(request):
    form = NewVariationForm(request.POST)
    if request.method =='POST':
        print(form)
        if form.is_valid():
            form.save()
        return redirect('add_variation')
    context = {'form' : form}

    return render(request,'admin_panel_templates/add_variation.html',context)


# displaying variations

def variation(request):
    variation = Variation.objects.all()
    context = {'variation' : variation}
    return render(request,'admin_panel_templates/variation.html',context)


# delete variation

def delete_variation(request,pk):
    variation = Variation.objects.filter(id=pk)
    variation.delete()
    return redirect('variation')




# displaying category in admin side

def view_category(request):
    category = Category.objects.all()
    context = {'category' : category}
    return render(request,'admin_panel_templates/view_category.html',context)


# add category

def category(request):
    form = NewCategorytForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('view_category')

    context = {'form' : form}
    return render(request,'admin_panel_templates/category.html',context)



# displaying user details

def user_details(request):    
    user = Account.objects.all()
    context = {'user':user}
    return render (request,'admin_panel_templates/user.html',context)



# blocking a user

def block_user(request,pk):
    user = Account.object.get(id=pk)
    user.is_active = False
    user.save()
    return redirect('user_details')


# unbloack a user

def unblock_user(request,pk):
    user = Account.object.get(id=pk)
    user.is_active = True
    user.save()
    return redirect('user_details')


# delete a user

def delete_user(request,pk):
    user = Account.object.get(id=pk)
    user.delete()
    return redirect('user_details')



# displaying orders

def order_management(request):

    order_product = OrderProduct.objects.all()
    p = Paginator(order_product,10)
    page_num = request.GET.get('page',1)

    try:
        page = p.page(page_num)
    except EmptyPage:
        page = p.page(1)
    context = {'order_products' : page}
    
    return render(request,'admin_panel_templates/order_management.html',context)




# displaying delivered items. It will also show you the report form a priod to another period

from django.core.paginator import EmptyPage, Paginator
def sales_management(request, page = 0):


    order_product = OrderProduct.objects.filter(status = 'Delivered')

    total = 0

    p = Paginator(order_product, 10)
    page_num = request.GET.get('page',1)

    try:
        page = p.page(page_num)
    except EmptyPage:
        page = p.page(1)


    for i in order_product:
        total += i.product_price +i.order.tax

    tot = int(total)

    context = {
        'order_products' : page,
        'total' : tot
        }
    return render(request,'admin_panel_templates/sales_management.html',context)
    


def period_report(request):
    
    if request.method == 'GET':
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        order_product = OrderProduct.objects.filter(status = 'Delivered' ,created_at__range=[from_date, to_date])
        print(order_product)
        
        total = 0
        for i in order_product:
            total += i.product_price + i.order.tax
        
        tot = int(total)

        
        context = {
            'order_products' : order_product,
            'total' : tot,
        }
        return render(request,'admin_panel_templates/sales_management.html',context)
    



# filtering to monthly report

def monthly_report(request):


    if request.method == 'GET':
        month = request.GET['month']
        extra_var =[]
        extra_var = month.split("-")
        month_only=int(extra_var[1])
        order_product=OrderProduct.objects.filter(status='Delivered',created_at__month=month_only)



        total=0
        for delive in order_product:
            total+=delive.product_price + delive.order.tax

        tot = int(total)

        context={
            'order_products':order_product,
            'total':tot,
        }
        

        return render(request,'admin_panel_templates/sales_management.html',context)
    else:
    
        order_product=OrderProduct.objects.filter(status='Delivered') 
        total=0 
        for delive in order_product:
                total+=delive.product_price + delive.order.tax

        tot = int(total)

        context={
                'order_products':order_product,
                'total':tot
            }

    return render(request,'admin_panel_templates/sales_management.html',context)




# filtering to yarly report

def yearly_report(request):
    if request.method=='GET':
        year=request.GET['year']
        order_product=OrderProduct.objects.filter(created_at__year=year,status='Delivered')
        total=0
        for delive in order_product:
            total+=delive.product_price + delive.order.tax

        tot = int(total)

        context={
            'order_products':order_product,
            'total':tot
            
        }
        return render(request,'admin_panel_templates/sales_management.html',context)
    
    
    


# product offer management

def product_offer(request):
    product_offers = ProductOffer.objects.all()
    products = Product.objects.all()
    if request.method == 'POST':
        
        product_id = int(request.POST.get('product'))
        percentage = request.POST.get('percentage')
        valid_from = request.POST['valid_from']
        valid_to = request.POST['valid_to']
        product = Product.objects.get(id=product_id)

        if ProductOffer.objects.filter(product=product_id).exists():

            product_off = ProductOffer.objects.get(product=product_id)
            product_off.product = product
            product_off.offer_price = percentage
            product_off.valid_from = valid_from
            product_off.valid_to = valid_to
            product_off.save()
            
        else:
            product_offer = ProductOffer(
                product = product,
                offer_price = percentage,
                valid_from = valid_from,
                valid_to = valid_to
            )
            product_offer.save()
        

        product_item = Product.objects.get(id=product_id)
        print(product_item)
        print(product_item.price)
        product_item.off_price = (product_item.price/100)*int(percentage)

        print(product_item.off_price)
        product_item.off_percentage = percentage
        product_item.save()
        return redirect('product_offer')



    context = {
        'products' : products,
        'product_offers': product_offers
    }
    return render(request,'admin_panel_templates/offer_management.html',context)



# delete product offer

def delete_product_offer(request,pk):
    product_offer = ProductOffer.objects.get(id=pk)
    product = Product.objects.get(product_name=product_offer.product)
    product.off_price = None
    product.off_percentage = None
    product.save()
    product_offer.delete()
    return redirect('product_offer')


# category offer management

def category_offer(request):
    category_offers = CategoryOffer.objects.all()
    category_items = Category.objects.all()
    if request.method == 'POST':
        category_name = request.POST.get('category')
        offer_percentage = request.POST['percentage']
        valid_from = request.POST['valid_from']
        valid_to = request.POST['valid_to']

        category = Category.objects.get(category_name=category_name)
        if CategoryOffer.objects.filter(category=category).exists():
            cats = CategoryOffer.objects.get(category=category)
            cats.category = category
            cats.offer_price = offer_percentage
            cats.valid_from = valid_from
            cats.valid_to = valid_to
            cats.save()
            print('Updated')
        else:
            category_i = CategoryOffer(
                category=category,
                offer_price = offer_percentage,
                valid_from = valid_from,
                valid_to = valid_to
            )
            category_i.save()
            print('item saved')

        product = Product.objects.filter(category=category.id)
        for item in product:
            item.off_price = (item.price/100)*int(offer_percentage)
            item.off_percentage = offer_percentage
            item.save()


    context = {'category_items':category_items,'category_offers':category_offers}
    return render(request,'admin_panel_templates/category_offer.html',context)



# delete category offer

def delete_category_offer(request,pk):
    category_offer = CategoryOffer.objects.get(id=pk)
    product = Product.objects.filter(category=category_offer.category)
    for i in product:
        i.off_price = None
        i.off_percentage = None
        i.save(update_fields = ['off_price','off_percentage'])
    category_offer.delete()
    return redirect('category_offer')



# coupon discount

def coupon_discount(request):

    coupons = CouponDiscount.objects.all()
    if request.method == 'POST':
        code = str(uuid.uuid4()).replace("-", "")[:10]
        disount = request.POST['discount']
        valid_from = request.POST['valid_from']
        valid_to = request.POST['valid_to']
        print('generated code is', code)
        coupon_discount = CouponDiscount(
            coupon_code = code,
            coupon_price = disount,
            valid_from = valid_from,
            valid_to = valid_to
        )
        coupon_discount.save()
    context = {'coupons':coupons}
    return render(request,'admin_panel_templates/coupon_discount.html',context)


# delete coupon

def delete_coupon(request,pk):
    coupon = CouponDiscount.objects.get(id=pk)
    coupon.delete()
    return redirect('coupon_discount')


# refferels
from accounts.models import Refferel
def refferels(request):
    reff = Refferel.objects.all()
    context = {'reff':reff}
    return render(request,'admin_panel_templates/refferel.html',context)


# export to pdf

def export_pdf(request):
    response = HttpResponse(content_type = 'application/pdf')
    response['Content-Disposition'] = 'inline; attachment; filename=SalesReport' + str(datetime.datetime.now())+'.pdf'

    response['Content-Transfer-Encoding']='binary'


    order_product = OrderProduct.objects.filter(status = 'Delivered')

    total = 0
    for i in order_product:
        total += i.product_price +i.order.tax

    tot = int(total)


    html_string = render_to_string('report/pdf_output.html',{'expenses':order_product,'total':tot})
    html = HTML(string=html_string)

    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()

        output=open(output.name, 'rb')
        response.write(output.read())

    return response




# export to excel
import xlwt
def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'inline; attachment; filename=SalesReport' + str(datetime.datetime.now())+'.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('SalesReport')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['Product','Amount','quantity','Date']

    for col_num in range(len(columns)):
        ws.write(row_num,col_num,columns[col_num],font_style)
    
    font_style = xlwt.XFStyle()

    rows = OrderProduct.objects.filter(status = 'Delivered').values_list('product','product_price','quantity','created_at')

    for row in rows:
        row_num += 1

        for col_num in range(len(row)):
            ws.write(row_num,col_num,str(row[col_num]),font_style)

    wb.save(response)
    
    return response





# admin logout

def admin_logout(request):
    del request.session['is_logged']
    return redirect('admin_login')


def admin_base(request):
    return render(request,'admin_panel_templates/admin_base.html')