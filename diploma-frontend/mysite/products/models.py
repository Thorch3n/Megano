
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Avg


class CategoryImage(models.Model):
    src = models.ImageField(upload_to='categoryImages/')
    alt = models.CharField(max_length=255, default='Category Image')

    def __str__(self):
        return self.alt


class Category(models.Model):
    title = models.CharField(max_length=100)
    image = models.ForeignKey(CategoryImage, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.RESTRICT, null=True, blank=True, related_name='subcategories')
    is_deleted = models.BooleanField(default=False)
    def __str__(self):
        return self.title

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    # Менеджер модели для исключения удаленных записей из запросов
    objects = models.Manager()

    class ActiveManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(is_deleted=False)

    active_objects = ActiveManager()

class ProductImages(models.Model):
    src = models.ImageField(upload_to='products/')
    alt = models.CharField(max_length=255, default='Product images')

    def __str__(self):
        return self.alt

class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name



class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count = models.PositiveIntegerField(null=True)
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True)
    fullDescription = models.TextField(null=True)
    freeDelivery = models.BooleanField(default=False)
    images = models.ManyToManyField(ProductImages)
    tags = models.ManyToManyField(Tag, null=True)
    number_of_sales = models.PositiveIntegerField(default=0)
    index_sort = models.PositiveIntegerField(default=0)
    limited_edition = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    @property
    def rating(self):
        """
        Calculates the average rating of the product based on reviews.
        """
        return self.reviews.aggregate(Avg('rate'))['rate__avg'] or 0

    def __str__(self):
        return self.title

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    # Менеджер модели для исключения удаленных записей из запросов
    objects = models.Manager()

    class ActiveManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(is_deleted=False)

    active_objects = ActiveManager()
class Specification(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    product = models.ManyToManyField(Product)

    def __str__(self):
        return self.name

class Review(models.Model):
    author = models.CharField(max_length=20)
    email = models.EmailField()
    text = models.TextField(max_length=255)
    rate = models.IntegerField(default=5)
    date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True, related_name='reviews')

class OrderManager(models.Manager):
    pass
class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    DELIVERY_TYPE_CHOICES = [
        ('free', 'Free'),
        ('express', 'Express'),
    ]

    PAYMENT_TYPE_CHOICES = [
        ('online', 'Online'),
        ('cash', 'Cash on delivery'),
    ]

    createdAt = models.DateTimeField(auto_now_add=True)
    fullName = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    deliveryType = models.CharField(max_length=10, choices=DELIVERY_TYPE_CHOICES, default='free', null=True, blank=True)
    paymentType = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES, default='online', null=True, blank=True)
    totalCost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    products = models.JSONField(blank=True, default=list)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    def soft_delete(self):
        self.is_deleted = True
        self.save()

    # Менеджер модели для исключения удаленных записей из запросов
    objects = models.Manager()

    class ActiveManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(is_deleted=False)

    active_objects = ActiveManager()

class SaleImage(models.Model):
    src = models.ImageField(upload_to='sales/')
    alt = models.CharField(max_length=255, default='Sales images')

class Sale(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    salePrice = models.DecimalField(max_digits=10, decimal_places=2)
    dateFrom = models.DateField()
    dateTo = models.DateField()
    title = models.CharField(max_length=255)
    images = models.ManyToManyField(SaleImage)

    def __str__(self):
        return self.title

