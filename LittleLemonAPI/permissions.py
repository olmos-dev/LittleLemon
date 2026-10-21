from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsManagerOrReadonlyUser(BasePermission):
  def has_permission(self, request, view):
    #Not autenticated, access denied
    if not request.user.is_authenticated:
      return False
    
    #GET HEAD AND OPTIONS
    if request.method in SAFE_METHODS:
      return True
    
    #POST, PUT, PATCH, DELETE only for manager
    print(request.user)
    return request.user.groups.filter(name="Manager").exists()

class IsManagerOnly(BasePermission):
  def has_permission(self, request, view):
    #Not autenticated, access denied
    if not request.user.is_authenticated:
      return False
    
    #All crud operations
    return request.user.groups.filter(name="Manager").exists()

class IsDeliverCrewOnly(BasePermission):
  def has_permission(self, request, view):
    #Not autenticated, access denied
    if not request.user.is_authenticated:
      return False
    
    #All crud operations
    return request.user.groups.filter(name="Delivery crew").exists()

class IsClientOnly(BasePermission):
  def has_permission(self, request, view):
    #Not autenticated, access denied
    if not request.user.is_authenticated:
      return False
    
    #access
    return not request.user.groups.exists()
  