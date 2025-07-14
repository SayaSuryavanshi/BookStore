from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from .models import Customers, Products
from django.core.exceptions import ValidationError

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class RegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email'
        })
    )
    contact = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contact number'
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )

    
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already registered.")
        return email

    def clean_contact(self):
        contact = self.cleaned_data['contact']
        if not contact.isdigit():
            raise ValidationError("Contact must be numeric.")
        if len(contact) < 10:
            raise ValidationError("Contact must be at least 10 digits.")
        return contact

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

class LoginForm(AuthenticationForm):
    username=forms.CharField(label="Enter Username ", widget=forms.TextInput(attrs={'class':'form-control'}))
    password=forms.CharField(label="Enter Password ", widget=forms.PasswordInput(attrs={'class':'form-control'}))

    class Meta:
        model=User
        fields=['username','password']

class CustomersForm(forms.ModelForm):
    class Meta:
        model=Customers
        fields=['custname','custaddress','city','state','custcontact','pincode']

        labels={
            'custname':'Enter Custname ',
            'custaddress':'Enter Address  ',
            'city':'Enter City ',
            'state':'Select State ',
            'custcontact':'Enter Contact ',
            'pincode':'Enter pincode ',
        }

        widgets={
            'custname':forms.TextInput(attrs={'class':'form-control'}),
            'custaddress':forms.TextInput(attrs={'class':'form-control'}),
            'city':forms.TextInput(attrs={'class':'form-control'}),
            'state':forms.Select(attrs={'class':'form-control'}),
            'custcontact':forms.TextInput(attrs={'class':'form-control'}),
            'pincode':forms.TextInput(attrs={'class':'form-control'}),
        }

#For Admin Panel
class ProductsForm(forms.ModelForm):
    class Meta:
        model=Products
        fields=['prodname','proddesc','prodprice','prodrating','prodimage','cat']

        labels={
            'prodname':'Enter Product name ',
            'proddesc':'Enter Description  ',
            'prodprice':'Enter Price ',
            'prodrating':'Enter Rating ',
            'prodimage':'Enter Image ',
            'cat':'Select Category ',
        }

        widgets={
            'prodname':forms.TextInput(attrs={'class':'form-control'}),
            'proddesc':forms.TextInput(attrs={'class':'form-control'}),
            'prodprice':forms.TextInput(attrs={'class':'form-control'}),
            'prodrating':forms.TextInput(attrs={'class':'form-control'}),
            'prodimage':forms.FileInput(attrs={'class':'form-control'}),
            'cat':forms.Select(attrs={'class':'form-control'}),
        }

        def clean_prodName(self):
            prodName=self.cleaned.data.get('prodname')
            if not prodName.isalpha():
                raise forms.ValidationError('Product name must contain only alphabets.')
            return prodName

