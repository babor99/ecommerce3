from django.contrib.auth.models import User
from django import forms

from .models import Order, Customer, Product


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['ordered_by', 'email', 'mobile', 'shipping_address']


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput())
    email = forms.EmailField(widget=forms.EmailInput())
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Customer
        fields = ['username', 'full_name', 'email', 'password', 'address']

    def clean_username(self):
        uname = self.cleaned_data['username']
        if User.objects.filter(username=uname).exists():
            raise forms.ValidationError("User with this username: '" + uname + "' already exists. Try with another username.")
        return uname


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'Enter the registered email..'}))

    def clean_email(self):
        em = self.cleaned_data.get('email')
        if Customer.objects.filter(user__email=em):
            pass
        else:
            raise forms.ValidationError(em + " doesn't match your account. Try another.")
        return em


class PasswordResetForm(forms.Form):
    new_password = forms.CharField(widget=(forms.PasswordInput(attrs={
        'class': 'form-control',
        'autocomplete': 'new_password',
        'placeholder': 'Enter new password'
    })), label='New Password')
    confirm_new_password = forms.CharField(widget=(forms.PasswordInput(attrs={
        'class': 'form-control',
        'autocomplete': 'new_password',
        'placeholder': 'Confirm new password'
    })), label='Confirm New Password')

    def clean_confirm_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        confirm_new_password = self.cleaned_data.get('confirm_new_password')
        if confirm_new_password != new_password:
            raise forms.ValidationError("Passwords didn't match")
        return confirm_new_password


class AdminProductAddForm(forms.ModelForm):
    extra_images = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-control', 'multiple':True}))
    class Meta:
        model = Product
        fields = ['title', 'slug', 'category', 'image', 'extra_images', 'marked_price',
         'selling_price', 'description', 'warranty', 'return_policy']
         
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Enter title..'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Enter slug..'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'
            }),
            'marked_price': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'selling_price': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Enter description..'
            }),
            'warranty': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Enter warranty..'
            }),
            'return_policy': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Enter return policy..'
            }),
        }
        