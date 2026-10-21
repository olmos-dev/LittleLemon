from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import generics, viewsets, status, filters, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from datetime import date
from django.db.models import Sum
from django.db import transaction

from .models import (
  Category,
  MenuItem,
  Cart,
  Order, 
  OrderItem
)
from .serializers import (
  CategorySerializer,
  MenuItemSerializer, 
  UserGroupsSerializer,
  CartSerializer,
  OrderSerilizer,
  OrderItemSerializer
)
from .permissions import (
  IsManagerOrReadonlyUser,
  IsManagerOnly, 
  IsDeliverCrewOnly,
  IsClientOnly,
)


#CATEGORY
class CategoryViewSet(viewsets.ModelViewSet):
  permission_classes = [IsManagerOrReadonlyUser]
  queryset = Category.objects.all() 
  serializer_class = CategorySerializer

#MENU ITEM
class MenuItemListCreateView(generics.ListCreateAPIView):
  permission_classes = [IsManagerOrReadonlyUser]
  filter_backends = [filters.OrderingFilter, filters.SearchFilter]
  ordering_fields = ["price","featured","category__title"]
  search_fields = ["title"]
  queryset = MenuItem.objects.select_related('category').all()
  serializer_class = MenuItemSerializer
  
  def get_queryset(self):
    """
    Clients can only see menu items where featured is True.
    """
    queryset = MenuItem.objects.select_related("category").all()
    
    if not self.request.user.groups.exists():
      return queryset.filter(featured=True)
     
    return queryset
  
class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
  permission_classes = [IsManagerOrReadonlyUser]
  queryset = MenuItem.objects.select_related('category').all()
  serializer_class = MenuItemSerializer

#CART
class CartAPIView(APIView):
    permission_classes = [IsClientOnly]

    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(cart_items, many=True)

        return Response(serializer.data)

    def post(self, request):
      serializer = CartSerializer(data=request.data)
      serializer.is_valid(raise_exception=True)
      
      try:
        serializer.save(user=request.user)
      except IntegrityError:
          return Response({"message": "This menuitem is already in the cart."},status=status.HTTP_400_BAD_REQUEST)
        
      return Response(serializer.data,status=status.HTTP_201_CREATED)

    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

#ORDERS
class OrderGenericView(generics.ListCreateAPIView):
  permission_classes = [permissions.IsAuthenticated]
  serializer_class = OrderSerilizer
  filter_backends = [filters.SearchFilter ,filters.OrderingFilter]
  ordering_fields = ["status","total","date"]
  search_fields = ["items__menuitem__title", "user__first_name", "user__last_name"]
  
  def get_permissions(self):
    if self.request.method == "POST":
      permission_classes = [IsClientOnly]
    else:
      permission_classes = [permissions.IsAuthenticated]
      
    return [permission() for permission in permission_classes]
  
  def get_queryset(self):
    user = self.request.user
    
    #Manager
    if self.request.user.groups.filter(name="Manager").exists():
      return (Order.objects.select_related('user','delivery_crew').prefetch_related('items__menuitem'))
      
    #Delivery crew
    if self.request.user.groups.filter(name="Delivery crew").exists():
          return (Order.objects.filter(delivery_crew = user).select_related('user','delivery_crew').prefetch_related('items__menuitem'))
    
    #Client
    return Order.objects.filter(user = user).select_related('user','delivery_crew').prefetch_related('items__menuitem')
  
  @transaction.atomic
  def perform_create(self, serializer):
    user = self.request.user
    cart_items = Cart.objects.filter(user=user)
    
    if not cart_items.exists():
      raise ValidationError({"message":"The cart is empty"})
    
    #orders
    order = serializer.save(
        user=user,
        delivery_crew = None,
        status = False,
        total=self.get_total(),
        date=date.today()
    )
    
    #orderItems
    order_items = [
      OrderItem(
        order = order,
        menuitem = item.menuitem,
        quantity = item.quantity,
        unit_price = item.unit_price,
        price = item.price
      )
      for item in cart_items
    ]
    
    OrderItem.objects.bulk_create(order_items)
    
    #delete cart
    cart_items.delete()
    
  def get_total(self):
    """Calculate the total price of all items in the user's cart"""
    return Cart.objects.filter(user=self.request.user).aggregate(total=Sum("price"))["total"]or 0

class OrderDetailGenericView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerilizer
    lookup_field = "id"
    lookup_url_kwarg = "orderId"
    
    def get_permissions(self):
      if self.request.method == "PUT":
        permission_classes = [IsManagerOnly]
      
      elif self.request.method == "PATCH":
          permission_classes = [IsManagerOnly | IsDeliverCrewOnly]

      elif self.request.method == "DELETE":
          permission_classes = [IsManagerOnly]
          
      else:
          permission_classes = [permissions.IsAuthenticated]

      return [permission() for permission in permission_classes]

    def get_queryset(self):
      user = self.request.user
      
      #Manager
      if self.request.user.groups.filter(name="Manager").exists():
        return (Order.objects.select_related('user','delivery_crew').prefetch_related('items__menuitem'))
            
      #Delivery crew
      if self.request.user.groups.filter(name="Delivery crew").exists():
            return (Order.objects.filter(delivery_crew = user).select_related('user','delivery_crew').prefetch_related('items__menuitem'))
          
      #Client
      return Order.objects.filter(user = user).select_related('user','delivery_crew').prefetch_related('items__menuitem')
    
    def perform_update(self, serializer):
      user = self.request.user
      
      if user.groups.filter(name="Delivery crew").exists():
          invalid_fields = set(self.request.data) - {"status"}

          if invalid_fields:
            raise ValidationError("Delivery crew can only modify the status.")
          
      serializer.save()
        
      

#USERS
class UserManagerAPIView(APIView):
  
  permission_classes = [IsManagerOnly]
  
  def get(self, request, userId):
    users = User.objects.filter(groups__name="Manager").prefetch_related("groups").distinct()
    serializer = UserGroupsSerializer(users, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)
  
  def post(self, request):
    serializer = UserGroupsSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = serializer.validated_data["user"]
    group = Group.objects.get(name="Manager")
    user.groups.add(group)
    
    return Response(status=status.HTTP_201_CREATED)

  def delete(self, request, userId):    
    user = get_object_or_404(User, id = userId)
    group = Group.objects.get(name="Manager")
    user.groups.remove(group)
    
    return Response(status=status.HTTP_200_OK)

class UserDeliveryCrewAPIView(APIView):
  
  permission_classes = [IsManagerOnly]
  
  def get(self, request, userId):
    users = User.objects.filter(groups__name="Delivery crew").prefetch_related("groups").distinct()
    serializer = UserGroupsSerializer(users, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)
  
  def post(self, request):
    serializer = UserGroupsSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = serializer.validated_data["user"]
    group = Group.objects.get(name="Delivery crew")
    user.groups.add(group)
    
    return Response(status=status.HTTP_201_CREATED)

  def delete(self, request, userId):    
    user = get_object_or_404(User, id=userId)
    group = Group.objects.get(name="Delivery crew")
    user.groups.remove(group)
    
    return Response(status=status.HTTP_200_OK)
  
  
  
 
