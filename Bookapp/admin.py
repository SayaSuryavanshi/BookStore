from django.contrib import admin
from .models import Categories,Products, Cart, Orders

# Register your models here.
class CategoriesAdmin(admin.ModelAdmin):
    list_display=['categoryname','catedec']
admin.site.register(Categories,CategoriesAdmin)

class ProductsAdmin(admin.ModelAdmin):
    list_display=['prodname','proddesc','prodprice','prodrating','prodimage','cat', 'is_deleted', 'delete_details']
admin.site.register(Products,ProductsAdmin)
    
class CardAdmin(admin.ModelAdmin):
    list_display=['uid','pid','qty']
admin.site.register(Cart,CardAdmin)

class OrdersAdmin(admin.ModelAdmin):
    list_display=['customer','books','quantity','order_date','status','total_price']
admin.site.register(Orders, OrdersAdmin)

