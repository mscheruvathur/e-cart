from django import forms
from django.db import models
from django.db.models import fields
from .models import Account, UserProfile
from store.models import Product
from category.models import Category
from orders.models import OrderProduct,ProductOffer,CategoryOffer
from store.models import Variation

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : 'Enter Password',
        'class' : 'form-control'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : 'Confirm Password',
        'class' : 'form-control'
    }))
    
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']

    def __init__(self,*args, **kwargs):
        super(RegistrationForm,self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(RegistrationForm,self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                'Password Doesnot Match!'
            )



class NewProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name','slug','description','price','stock','is_available','category','images_1','images_2','images_3','images_4']

    def __init__(self,*args, **kwargs):
        super(NewProductForm, self).__init__(*args, **kwargs)
        self.fields['product_name'].widget.attrs['placeholder'] = 'enter the name of the product'
        self.fields['description'].widget.attrs['placeholder'] = 'add description'
        self.fields['price'].widget.attrs['placeholder'] = 'price prer unit'
        self.fields['stock'].widget.attrs['placeholder'] = 'number of stock availbable'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class NewCategorytForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

    def __init__(self,*args, **kwargs):
        super(NewCategorytForm, self).__init__(*args, **kwargs)
        self.fields['category_name'].widget.attrs['placeholder'] = 'enter the name of the product'
        self.fields['description'].widget.attrs['placeholder'] = 'add description'
    
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class NewOrderProductForm(forms.ModelForm):
    class Meta:
        model = OrderProduct
        fields = ['status']


class NewVariationForm(forms.ModelForm):
    class Meta:
        model = Variation
        fields = '__all__'


class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name' , 'phone_number')

    def __init__(self,*args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages= {'invalid' : ("Image Files only")}, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ('profile_picture',)


