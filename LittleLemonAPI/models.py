from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
  title = models.CharField(max_length=255, db_index=True)
  slug = models.SlugField()
  
  class Meta:
    db_table = "category"
    
  def __str__(self):
    return self.title


class MenuItem(models.Model):
  title = models.CharField(max_length=255, db_index=True)
  price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
  featured = models.BooleanField(db_index=True)
  category = models.ForeignKey("Category", on_delete=models.PROTECT)
  
  class Meta:
    db_table = "menu_item"
      
  def __str__(self):
    return self.title
  
class Cart(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  menuitem = models.ForeignKey("MenuItem", on_delete=models.CASCADE)
  quantity = models.SmallIntegerField()
  unit_price = models.DecimalField(max_digits=6, decimal_places=2)
  price = models.DecimalField(max_digits=6, decimal_places=2)
  
  class Meta:
    unique_together = ('menuitem','user')
    db_table = "cart"
    
    
class Order(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  delivery_crew = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="delivery_crew", null=True)
  status = models.BooleanField(db_index=True, default=0)
  total = models.DecimalField(max_digits=6, decimal_places=2)
  date = models.DateField(db_index=True)
  
  class Meta:
    db_table = "order"
    
class OrderItem(models.Model):
  order = models.ForeignKey("Order",related_name="items", on_delete=models.CASCADE)
  menuitem = models.ForeignKey("MenuItem", on_delete=models.CASCADE)
  quantity = models.SmallIntegerField()
  unit_price = models.DecimalField(max_digits=6, decimal_places=2)
  price = models.DecimalField(max_digits=6, decimal_places=2)
  
  class Meta:
    unique_together = ('order','menuitem')
    db_table = "order_item"

