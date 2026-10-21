from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from .models import (
  Category,
  MenuItem,
  Cart,
  Order, 
  OrderItem
)

#CATEGORY
class CategorySerializer(serializers.ModelSerializer):
  class Meta:
    model = Category
    fields = ["id","title","slug"]

#MENU ITEM
class MenuItemSerializer(serializers.ModelSerializer):
  category = serializers.StringRelatedField(read_only = True)
  category_id = serializers.PrimaryKeyRelatedField(
    queryset = Category.objects.all(),
    source = "category",
    write_only = True,
  )
  featured = serializers.BooleanField(write_only = True)
  featured_display = serializers.SerializerMethodField(
    method_name="get_featured"
  )
  
  class Meta:
    model = MenuItem
    fields = ["id","title","price","featured","featured_display","category","category_id"]
  
  def get_featured(self, obj):
      return "Available" if obj.featured else "Sold out"

#CART
class CartSerializer(serializers.ModelSerializer):
  user = serializers.SerializerMethodField(method_name="get_user")
  menuitem = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all(), write_only = True)
  menuitem_title = serializers.CharField(source="menuitem.title", read_only=True)
  
  class Meta:
    model = Cart
    fields = ["id","user","menuitem","menuitem_title","quantity","unit_price","price"]
    read_only_fields = ["user","unit_price","price"]
    extra_kwargs = {
      "quantity":{"min_value":1}
    }
      
  def create(self, validated_data):
    menuitem = validated_data["menuitem"]
    quantity = validated_data["quantity"]
    
    unit_price = menuitem.price
    price = quantity * unit_price
    
    validated_data["unit_price"] = unit_price
    validated_data["price"] = price
    
    return super().create(validated_data)
  
  def validate_menuitem(self, value):
    if not value.featured:
      raise serializers.ValidationError("This menuitem is out of stock.")
    return value
  
  def get_user(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()

#ORDERS
class OrderItemSerializer(serializers.ModelSerializer):
  menuitem = serializers.StringRelatedField()
  class Meta:
    model = OrderItem
    fields = ["menuitem","quantity","unit_price","price"]
    
class OrderSerilizer(serializers.ModelSerializer):
  user = serializers.SerializerMethodField(method_name="get_user_name")
  delivery_crew_id = serializers.PrimaryKeyRelatedField(queryset = User.objects.all(), source = "delivery_crew", write_only=True, required = False)
  status = serializers.BooleanField(write_only = True, required = False)
  delivery_crew = serializers.SerializerMethodField(method_name="get_delivery_crew_name")
  status_display = serializers.SerializerMethodField(method_name="get_status")
  items = OrderItemSerializer(many=True, read_only=True)
  
  class Meta:
    model = Order
    fields = ['id','user','delivery_crew_id','delivery_crew','status','status_display','total','date','items']
    read_only_fields = ['total','date']
    
  def get_status(self, obj):
    return "Delivered" if obj.status else "Not delivered"
  
  def get_user_name(self, obj):
    return f"{obj.user.first_name} {obj.user.last_name}".strip()
  
  def get_delivery_crew_name(self, obj):
    if obj.delivery_crew is None:
      return "Not assigned"
    return (f"{obj.delivery_crew.first_name} " f"{obj.delivery_crew.last_name}").strip()
  
  def validate_delivery_crew_id(self, user):
    if not user.groups.filter(name="Delivery crew").exists():
        raise serializers.ValidationError("This selected user is not a Delivery crew")
    return user
  
#USERS
class UserGroupsSerializer(serializers.Serializer):  
  #write only 
  user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source="user", write_only=True)
  
  #read only
  id = serializers.IntegerField(read_only=True)
  username = serializers.CharField(read_only = True)
  email = serializers.CharField(read_only = True)
  first_name = serializers.CharField(read_only = True)
  last_name = serializers.CharField(read_only = True)
  groups = serializers.StringRelatedField(many = True, read_only = True)
  
  
    
