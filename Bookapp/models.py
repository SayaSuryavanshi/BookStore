from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Categories(models.Model):
    categoryname=models.CharField(max_length=100)
    catedec=models.TextField()

    def __str__(self):
        return self.categoryname
    
    
class Products(models.Model):
    prodname=models.CharField(max_length=100)
    proddesc=models.TextField()
    prodprice=models.DecimalField(max_digits=6, decimal_places=2)
    prodrating=models.DecimalField(max_digits=2, decimal_places=1)
    prodimage=models.ImageField(upload_to='images/')
    cat=models.ForeignKey(Categories,on_delete=models.PROTECT)
    is_deleted=models.BooleanField(default=False)
    delete_details=models.DateTimeField(null=True, blank=True)
    

    def __str__(self):
        return self.prodname
    

class Cart(models.Model):
    uid=models.ForeignKey(User,on_delete=models.CASCADE, db_column='uid')
    pid=models.ForeignKey(Products, on_delete=models.CASCADE, db_column='pid')
    qty=models.PositiveBigIntegerField(default=1)


class Customers(models.Model):
    STATE_CHOICES=[       
        ('AP','Andra Pradesh'),
        ('GA','Goa'),
        ('GJ','Gujarat'),
        ('KL','Kerala'),
        ('MP','Madhya Pradesh'),
        ('MH','Maharashtra'),
    ]
    userid=models.ForeignKey(User, on_delete=models.CASCADE)
    custname=models.CharField(max_length=100)
    custaddress=models.TextField()
    city=models.CharField(max_length=100)
    state=models.CharField(max_length=2,choices=STATE_CHOICES)
    custcontact=models.BigIntegerField()
    pincode=models.IntegerField()
   
    def __str__(self):
        return self.custname
    

class Orders(models.Model):
    STATUS_CHOICES=[
        ('PENDING','Pending'),
        ('PROCESSING','Processing'),
        ('SHIPPED','Shipped'),
        ('DELIVERED','Delivered'),
        ('CANCELLED','Cancelled'),
    ]

    customer=models.ForeignKey(User, on_delete=models.CASCADE)
    books=models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
    order_date=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_price=models.DecimalField(max_digits=10, decimal_places=2)
    bookorder_id = models.CharField(max_length=100, unique=True, null=True)


    def __str__(self):
        return f"Order {self.bookorder_id} - {self.customer}"

    


# For Rest API
class Company(models.Model):
    name=models.CharField(max_length=100)
    contact=models.BigIntegerField()
    address=models.TextField()