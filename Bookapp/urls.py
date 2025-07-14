"""
URL configuration for BookStore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .import views

urlpatterns = [
    path('',views.home, name='home'),
    path('cat/<int:id>',views.categorydetails),
    path('register/', views.register, name='register'),
    path('logindetails/', views.logindetails, name='logindetails'),
    path('signout',views.signout,name='signout'),
    path('viewproduct/<int:id>',views.viewproduct, name='viewproduct'),
    path('addtocart/<int:id>',views.addtocart, name='addtocart'),
    path('viewcart/', views.viewcart, name='viewcart'),
    path('updateqty/<qv>/<id>/',views.updateqty),
    path('removeprod/<int:id>', views.removeprod, name='removeprod'),
    path('customerdetails/',views.customerdetails, name='customerdetails'),
    path('searchdata/', views.searchdata, name='searchdata'),
    path('checkout/',views.checkout, name='checkout'),
    path('paymentsuccess',views.paymentsuccess, name="paymentsuccess"),
    path('paymentfailed', views.paymentfailed, name="paymentfailed"),
    
    path('placedorders',views.placedorders, name="placedorders"),

    path('forgot_password/', views.forgot_password, name="forgot_password"),
    path('verify_otp/', views.verify_otp, name="verify_otp"),
    path('reset_password/', views.reset_password, name="reset_password"),

    # path('send_otp', views.send_otp, name="send_otp"),
    path('restcrud/',views.simplerestcrud.as_view()), #class based view
    path('sort/<sv>', views.sort, name="sort"),
    path('range', views.range, name="range"),
    path('addproduct', views.addproduct, name="addproduct"),
    path('deleteProduct/<int:id>', views.deleteProduct, name="deleteProduct"),
    path('updateproduct/<int:id>', views.updateproduct, name="updateproduct"),
    path('contact', views.contact, name="contact"),
    path('aboutus', views.aboutus, name="aboutus")
]
