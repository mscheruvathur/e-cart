from django.shortcuts import render,redirect
from django.http import HttpResponse
from store.models import Product
from accounts.models import Account
from .forms import NewProductForm

# Create your views here.

def admin_panel(request):
       
        return render(request,'admin_panel_templates/add_product.html')
    


#----------------------------------------------------------------------------------#

def product(request):
    # products = Product.objects.all()
    # context = {'products':products}
    return render(request,'admin_panel_templates/product_details.html')


def update_product(request):
    return render(request,'admin_templates/update_product.html')

def add_product(request):
        form = NewProductForm(request.POST, request.FILES)
        if request.method == 'POST':
            if form.is_valid():

                name = form.cleaned_data['product_name']
                description = form.cleaned_data['description']
                stock = form.cleaned_data['stock']
                images = form.cleaned_data['images']
                category = form.cleaned_data['category']
                price = form.cleaned_data['price']

                # name = request.POST['name']
                # price = request.POST['price']
                # description = request.POST['description']
                # stock = request.POST['stock']
                # image = form.cleaned_data['image']
                # category = form.cleaned_data['category']
                items = Product(product_name=name,price=price,description=description,stock=stock,images=images,category=category)
                items.save()
                return redirect('add_product')
        context = {'form':form}
        return render(request,'admin_panel_templates/add_product.html',context)

def category(request):
    return render(request,'admin_panel_teplates/category.html')





#----------------------------------------------------------------------------------#
def user_details(request):
    user = Account.object.all
    context = {'user':user}
    return render (request,'admin_panel_templates/user.html',context)


def block_user(request,pk):
    user = Account.object.get(id=pk)
    user.is_active = False
    user.save()
    return redirect('admin_panel')

def unblock_user(request,pk):
    user = Account.object.get(id=pk)
    user.is_active = True
    user.save()
    return redirect('admin_panel')

def delete_user(request,pk):
    user = Account.object.get(id=pk)
    user.delete()
    return redirect('admin_panel')