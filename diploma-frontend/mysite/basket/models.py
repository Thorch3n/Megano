from django.db import models
from django.contrib.auth.models import User

from products.models import Product


class Basket(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='cart')


    def __str__(self):
        return f"{self.user.username}'s Basket"

    @property
    def subtotal(self):
        """
        Calculates the subtotal for the product in the basket.
        """
        return self.product.price * self.count

class BasketItem(models.Model):
    basket = models.ForeignKey('Basket', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)

