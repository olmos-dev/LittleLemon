from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
  CategoryViewSet,
  MenuItemListCreateView,
  MenuItemDetailView, 
  UserManagerAPIView,
  UserDeliveryCrewAPIView,
  CartAPIView,
  OrderGenericView,
  OrderDetailGenericView,
)


router = DefaultRouter()

router.register('categories', CategoryViewSet)

urlpatterns = [
  path('menu-items',  MenuItemListCreateView.as_view()),
  path('menu-items/<int:pk>', MenuItemDetailView.as_view()),
  path('groups/manager/users', UserManagerAPIView.as_view()),
  path('groups/manager/users/<int:userId>', UserManagerAPIView.as_view()),
  path('groups/delivery-crew/users', UserDeliveryCrewAPIView.as_view()),
  path('groups/delivery-crew/users/<int:userId>', UserDeliveryCrewAPIView.as_view()), 
  path('cart/menu-items', CartAPIView.as_view()),
  path('orders', OrderGenericView.as_view()),
  path('orders/<int:orderId>', OrderDetailGenericView.as_view())
]

urlpatterns += router.urls
