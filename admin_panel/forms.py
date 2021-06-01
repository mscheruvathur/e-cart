from django import forms
from store.models import Product

class NewProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self,*args, **kwargs):
        super(NewProductForm, self).__init__(*args, **kwargs)
        self.fields['product_name'].widget.attrs['placeholder'] = 'enter the name of the product'
        self.fields['description'].widget.attrs['placeholder'] = 'add description'
        self.fields['price'].widget.attrs['placeholder'] = 'price prer unit'
        self.fields['stock'].widget.attrs['placeholder'] = 'number of stock availbable'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'