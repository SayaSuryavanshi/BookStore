from django.shortcuts import render, HttpResponse,redirect
from .models import Categories, Products, Cart, Customers, Orders
from .forms import LoginForm, CustomersForm, ProductsForm, RegistrationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


# For Paypal payment
from django.conf import settings
import uuid 
from paypal.standard.forms import PayPalPaymentsForm
from django.urls import reverse

#For Forgot pwd
import random
from django.core.mail import send_mail
from django.contrib import messages

import datetime
from  django.utils import timezone

# Create your views here.

def home(request):
    # return HttpResponse("<h2>Welcome to Book Store....</h2>")
    cat=Categories.objects.all()
    # prod=Products.objects.all()
    prod=Products.objects.filter(is_deleted=False)
    return render(request,'index.html',{'cat':cat,'prod':prod})

def categorydetails(request, id):
    cate=Categories.objects.all()
    prod=Products.objects.filter(cat=id) #cat coming from model
    return render(request,'index.html',{'cat':cate,'prod':prod})

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            # Save address separately or in extended profile
            # For now just print or pass in context
            # address_info = Customers.objects.create(
            #     address=form.cleaned_data['address'],
            #     city=form.cleaned_data['city'],
            #     state=form.cleaned_data['state'],
            #     pincode=form.cleaned_data['pincode'],
            #     contact=form.cleaned_data['contact']
            # )
            # Optionally, save to a separate model
            messages.success(request, "Registration successful!")
            return redirect("logindetails")
    else:
        form = RegistrationForm()
    return render(request, "register.html", {"form": form})
    
def logindetails(request):
    if request.method=="POST":
        uname=request.POST['username']
        pwd=request.POST['password']

        user=authenticate(request, username=uname, password=pwd)
        if user is not None:
            login(request, user)
            request.session['last_activity']=str(datetime.datetime.now())
            request.session.set_expiry(800)     #8 minutes
            response=redirect('home')
            request.session['username']=uname
            response.set_cookie('Username', uname)
            response.set_cookie('time', datetime.datetime.now())
            return response
        else:
            return redirect('logindetails')
    else:
        fmlogin=LoginForm()
        return render(request, 'login.html', {'loginfm':fmlogin})

# To view product 
def viewproduct(request,id):
    prod=Products.objects.filter(id=id)
    return render(request, 'viewproduct.html',{'prod':prod})

#Functionality for Add to Cart
from django.db.models import Q
@login_required(login_url=logindetails)
def addtocart(request, id):
    prod=Products.objects.filter(id=id)
    userid=request.user.id           #to get userid of currently login user
    user=User.objects.filter(id=userid)

    q1=Q(uid=user[0])
    q2=Q(pid=prod[0])
    product=Cart.objects.filter(q1 & q2)

    n=len(product)
    if n==1:
        return render(request,'viewproduct.html',{'msg':'Already in cart!!! Please check','prod':prod})
    else:
        cartdetails=Cart.objects.create(pid=prod[0], uid=user[0])
        cartdetails.save()
        return render(request,'viewproduct.html',{'success':'Added to cart !','prod':prod})



#Functionality to view products added in cart and Calcualte total of product according to quantity
def viewcart(request):
    userid=request.user.id
    products=Cart.objects.filter(uid=userid)
    print(products)
    total=0
    for i in products:
        total=total + i.pid.prodprice * i.qty
    print(total)

    del_charge=0
    if total>=50000:
        del_charge=2000
    elif total>=20000:
        del_charge=1000
    elif total>=10000:
        del_charge=500
    elif total>=5000:
        del_charge:200
    elif total>=1000:
        del_charge=50
    else:
        del_charge=0
    
    total=del_charge+total
    # addedcart=Cart.objects.all()
    return render(request,'viewcart.html',{'prod':products, 'total':total})


#Functionality to increase quentity 
def updateqty(request, qv, id):
    cartdetails=Cart.objects.filter(id=id)
    if qv=='1':
        total=cartdetails[0].qty+1
        cartdetails.update(qty=total)
    else:
        if cartdetails[0].qty>1:
            total=cartdetails[0].qty-1
            cartdetails.update(qty=total)
    return redirect('/viewcart')

# Funcyionality to remove cart
def removeprod(request,id):
    prd=Cart.objects.filter(id=id)
    prd.delete()
    return redirect('viewcart')


# Functionality to Add Shipping Address of Customer
def customerdetails(request):
    if request.method=='POST':
        cust=CustomersForm(request.POST)
        if cust.is_valid():
            customer=cust.save(commit=False)
            customer.userid=request.user
            customer.save()
            return redirect('checkout')
        
    else:
        cust=CustomersForm()
    return render(request,'custdetails.html',{'cust':cust})


# Functionality to checkout purchase details
def checkout(request):
    userid=request.user.id
    products=Cart.objects.filter(uid=userid)
    print(products)
    total=0
    for i in products:
        total=total + i.pid.prodprice * i.qty
    print(total)
    del_charge=0
    if total>=50000:
        del_charge=2000
    elif total>=20000:
        del_charge=1000
    elif total>=10000:
        del_charge=500
    elif total>=5000:
        del_charge:200
    elif total>=1000:
        del_charge=50
    else:
        del_charge=0  
    
    total=del_charge+total
    cust_details=Customers.objects.filter(userid=userid).order_by('-id').first()
    
    # Generate unique order ID
    order_id = str(uuid.uuid4())

    # =================Paypa code=========================
    host= request.get_host() #will fetch the domain site is currently hosted on.

    paypal_checkout={
        'business': settings.PAYPAL_RECEIVER_EMAIL, #This is typically the email address
        'amount': total,    #The amount of money to be charged for the transcation
        'item_name':'BookStore',    #Describes the item being purchased
        'invoice': order_id,    #A unique identifier for the invoice. It uses uuid.uuid4
        'currency_code':'USD',
        'notify_url':f"http://{host}{reverse('paypal-ipn')}",       # The URL where Paypal will send
        'return_url':f"http://{host}{reverse('paymentsuccess')}?invoice={order_id}",   # The URL where the customer will success to payment
        'cancel_url':f"http://{host}{reverse('paymentfailed')}",    # The URL where the customer will failed to payment
    }
    paypal_payment=PayPalPaymentsForm(initial=paypal_checkout)
     # ================= Paypal code End=========================

    return render(request,'checkout.html',{'prod':products, 'total':total, 'cust_details':cust_details,
                                           'paypal_payment':paypal_payment })

# To show Payment Success 
def paymentsuccess(request):
    order_id = request.GET.get('invoice')
    userid=request.user.id
    products=Cart.objects.filter(uid=userid)
    print(products)
    total=0
    for i in products:
        total=total + i.pid.prodprice * i.qty

        del_charge=0
        if total>=50000:
            del_charge=2000
        elif total>=20000:
            del_charge=1000
        elif total>=10000:
            del_charge=500
        elif total>=5000:
            del_charge:200
        elif total>=1000:
            del_charge=50
        else:
            del_charge=0
        
        total=del_charge+total

        request.session["total_amount"] = str(total)

        orderdetails=Orders.objects.create(customer=i.uid, books=i.pid, quantity=i.qty, total_price=total)
        orderdetails.save()
        i.delete()

    orderdetails=Orders.objects.filter(customer=request.user.id)
    total_amount = request.session.get("total_amount", None)
    return render(request, 'paymentsuccess.html', {'orderdetails':orderdetails, 'order_id':order_id , 'total_amount':total_amount})

# To Show Payment Fail
def paymentfailed(request):
    return render(request, 'paymentfailed.html')

# Placed Orders 
def placedorders(request):
    placeedordersdetails=Orders.objects.filter(customer=request.user.id)
    return render(request, 'placedorders.html', {'placeedordersdetails':placeedordersdetails})

# Serach Functionality
def searchdata(request):
    if request.method==("POST"):
        searchdetails=request.POST['search']
        print(searchdetails)

        result=Products.objects.filter(prodname__icontains=searchdetails)
        print(result)

        return render(request, 'search.html', {'result':result})
    else:
        return render(request,'search.html')
    
# Forgot Password Functionality
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        users = User.objects.filter(email=email)
        if users.exists():
            user = users.first()
            otp = random.randint(100000, 999999)
            request.session['reset_otp'] = otp
            request.session['reset_email'] = email
            request.session['otp_purpose'] = 'forgot_password'  # ✅ Fixed purpose here
            subject = "Your Password Reset OTP"
            message = (
                f"Dear {user.username},\n\n"
                f"Your OTP for password reset is: {otp}\n\n"
                f"Please enter this OTP to reset your password.\n\n"
                f"Best Regards,\nYour Support Team."
            )
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False
            )
            return redirect('verify_otp')  # Redirect to OTP verification page
        else:
            messages.error(request, "Email not found! Please enter a registered email.")   
    return render(request, 'forgotpassword.html')


from django.shortcuts import render, redirect
from django.contrib import messages

# To verify OTP for forgot password
def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('reset_otp')
        otp_purpose = request.session.get('otp_purpose')

        if entered_otp == str(stored_otp):
            if otp_purpose == "forgot_password":
                return redirect('reset_password')
            else:
                messages.error(request, "Invalid OTP purpose.")
        else:
            messages.error(request, "Invalid OTP! Please try again.")
    
    return render(request, 'verifyotp.html')


# Reset password after forgot password
def reset_password(request):
    if request.method=="POST":
        new_pwd=request.POST['new_password']
        confirm_pwd=request.POST['confirm_password']
        email=request.session.get('reset_email')

        if new_pwd==confirm_pwd:
            try:
                user=User.objects.get(email=email)
                user.set_password(new_pwd)
                user.save()

                #clear session data
                del request.session['reset_otp']
                del request.session['reset_email']

                messages.success(request, "Password reset successful ! You can now login")
                return redirect('logindetails')
            except User.DoesNotExist:
                messages.error(request, "Something went wrong. Try Again")
                return redirect('forgot_password')
        else:
            messages.error(request, "Password does not match! Try Again")
            return render(request, 'resetpassword.html')
    return render(request, 'resetpassword.html')


# Functionality for Logout User
def signout(request):
    logout(request)
    return redirect('home')

# For soting products in asending or descending order by price
def sort(request, sv):
    if sv=='0':
        col='prodprice'     #asc
    else:
        col='-prodprice'    #desc
    
    prod=Products.objects.all().order_by(col)
    cat=Categories.objects.all()
    return render(request, 'index.html', {'prod':prod, 'cat':cat})

# For sorting products by price
def range(request):
    min=request.GET['min']
    max=request.GET['max']
    print(min)
    print(max)

    q1=Q(prodprice__lte=max)
    q2=Q(prodprice__gte=min)

    prod=Products.objects.filter(q1 & q2)
    cat=Categories.objects.all()
    return render(request, 'index.html', {'prod':prod, 'cat':cat})


from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CompanySerializers
from .models import Company

class simplerestcrud(APIView):
    def get(self, request):
        id=request.query_params.get('id',None)
        if id:
            try:
                companydata=Company.objects.get(id=id)
                compdetails=CompanySerializers(companydata)
                return Response(customerdetails.data, status=status.HTTP_200_OK)
            except :
                return Response(customerdetails.data, status=status.HTTP_404_NOT_FOUND)
        else:
            companydata=Company.objects.all()
            compdetails=CompanySerializers(companydata, many=True)
            return Response(compdetails.data, status=status.HTTP_200_OK)
    
    
    def post(self, resquest):
        company=resquest.data
        print(company)
        comp_data=CompanySerializers(data=company)
        if comp_data.is_valid():
            comp_data.save()
            return Response({'msg':'Record is added'}, status=status.HTTP_200_OK)
        return Response({'msg':'Data is not available'}, status=status.HTTP_404_NOT_FOUND)
    
    
    def patch(self, request):
        newdata=request.data
        id=newdata.get("id",None)
        if id:
            companydata=Company.objects.get(id=id)
            companydetails=CompanySerializers(companydata, newdata, partial=True)
            if companydetails.is_valid():
                companydetails.save()
                return Response({'msg':'record is successfully updated'}, status=status.HTTP_200_OK)
            else:
                return Response({'msg':'Data is not available'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request):
        id=request.data.get("id",None)
        if id:
            companydata=Company.objects.get(id=id)
            companydata.delete()
            return Response({'msg':'This is the delete resquest'}, status=status.HTTP_200_OK)
        return Response({'msg':'This is delete request'}, status=status.HTTP_404_NOT_FOUND)
    
    #Admin Panel for Add Product

#Admin Panel to Add Products
def addproduct(request):
    if request.method=="POST":
        prdform=ProductsForm(request.POST,request.FILES)  #if we want save image then we have to use request.FILES
        print(prdform)
        if prdform.is_valid():
            prdform.save()
            return redirect('home')
        else:
            return redirect('addproduct')
    else:
        prdform=ProductsForm()
        return render(request, 'addproduct.html', {'prdform':prdform})
    
#Admin Panel To Delete product
def deleteProduct(request, id):
    prddelete=Products.objects.get(id=id, is_deleted=False)
    prddelete.is_deleted=True
    prddelete.delete_details=timezone.now()
    prddelete.save()
    return redirect('home')

#Admin Panel To delete product
def updateproduct(request, id):
    prdupdate=Products.objects.get(id=id)
    if request.method=="POST":
        prdform=ProductsForm(request.POST, request.FILES, instance=prdupdate)
        if prdform.is_valid():
            prdform.save()
            return redirect('home')
    else:
        prdform=ProductsForm(instance=prdupdate)
    return render(request, 'updateproduct.html', {'prdform':prdform, 'prdupdate':prdupdate})
    
# ContactUs
def contact(request):
    return render(request, 'contact.html')

# AboutUs
def aboutus(request):
    return render(request, 'about.html')

