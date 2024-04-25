"""
Административная панель для управления товарами, категориями, тегами, акциями и заказами.

Это административная панель Django, которая предоставляет возможность управления товарами, категориями, тегами, акциями и заказами.

Методы:
    mark_free_delivery: Делает бесплатную доставку для выбранных товаров.
    remove_free_delivery: Убирает бесплатную доставку для выбранных товаров.
    make_soft_delete: Отмечает выбранные элементы как удаленные.
    remove_soft_delete: Убирает пометку удаления для выбранных элементов.
"""

from django import forms
from django.contrib import admin
from django.db.models import QuerySet, ManyToManyField
from django.forms import SelectMultiple, ModelMultipleChoiceField
from django.http import HttpRequest
from .models import Product, Category, Tag, Sale, SaleImage, Specification, Order, ProductImages, CategoryImage
from .admin_mixins import ExportAsCSVMixin


@admin.action(description='Make free delivery')
def mark_free_delivery(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet) -> None:
    queryset.update(freeDelivery=True)


@admin.action(description='Remove free delivery')
def remove_free_delivery(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet) -> None:
    queryset.update(freeDelivery=False)


@admin.action(description='Make soft delete')
def make_soft_delete(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet) -> None:
    queryset.update(is_deleted=True)


@admin.action(description='Remove soft delete')
def remove_soft_delete(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet) -> None:
    queryset.update(is_deleted=False)



"""
Класс для встраивания изображений товаров в административную панель.
"""
@admin.register(ProductImages)
class ProductImagesAdmin(admin.ModelAdmin):
    list_display = ['id', 'src', 'alt']
    list_display_links = ['id', 'src']
    list_filter = ['src']
    search_fields = ['alt']

"""
Форма администратора для спецификации товара.
"""

class SpecificationAdminForm(forms.ModelForm):
    product = forms.ModelMultipleChoiceField(queryset=Product.objects.all(), widget=forms.SelectMultiple)

    class Meta:
        model = Specification
        fields = '__all__'

"""
Администратор спецификации товара.
"""

@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    form = SpecificationAdminForm
    list_display = 'name', 'value'
    ordering = ('name',)
    fieldsets = [
        (None, {
            'fields': (
                'name', 'value', 'product',
            )
        }),
    ]

"""
Администратор товаров.
"""

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    actions = [
        mark_free_delivery,
        remove_free_delivery,
        make_soft_delete,
        remove_soft_delete,
        'export_as_csv',
    ]

    formfield_overrides = {
        ManyToManyField: {'widget': SelectMultiple},
    }

    list_display = 'pk', 'category', 'title', 'price', 'count', 'date', 'description', 'freeDelivery', 'is_deleted'
    list_display_links = 'pk', 'title'
    list_free = ('category',)
    ordering = ('title', 'pk', 'price', 'count', 'freeDelivery')
    search_fields = ('title', 'description', 'price')
    fieldsets = [
        (None, {
            'fields': (
                'title', 'description', 'fullDescription', 'tags', 'category', 'images', 'limited_edition',
                'index_sort'),
        }),
        ('Price and count options', {
            'fields': ('price', 'count'),
            'classes': ('collapse', 'wide'),
        }),
        ('Extra options', {
            'fields': ('freeDelivery',),
            'classes': ('collapse', 'wide'),
            'description': 'Extra options. Field "freeDelivery" is for make a free delivery for this product.',
        })
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('category').filter(
            is_deleted=False)  # Исключаем удаленные записи из списка в административной панели

    def delete_model(self, request, obj):
        obj.soft_delete()  # Вызываем метод мягкого удаления для объекта
        obj.save()  # Сохраняем изменения


@admin.register(CategoryImage)
class CategoryImage(admin.ModelAdmin):
    list_display = ['id', 'src', 'alt']
    list_display_links = ['id', 'src']
    list_filter = ['src']
    search_fields = ['alt']

"""
Администратор категорий.
"""

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    actions = [
        make_soft_delete,
        remove_soft_delete,
        'export_as_csv',
    ]
    list_display = 'pk', 'title', 'is_deleted'
    list_display_links = 'pk', 'title'
    ordering = ('title', 'pk', 'parent')
    search_fields = ['title']
    fieldsets = [
        (None, {
            'fields': ('title', 'image', 'parent'),
        }),
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_deleted=False)  # Исключаем удаленные записи из списка в административной панели

    def delete_model(self, request, obj):
        obj.soft_delete()  # Вызываем метод мягкого удаления для объекта
        obj.save()  # Сохраняем изменения

"""
Администратор тегов.
"""

@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    actions = [
        'export_as_csv',
    ]
    list_display = 'pk', 'name'
    list_display_links = 'pk', 'name'
    ordering = ('name', 'pk')
    search_fields = ['name']
    fieldsets = [
        (None, {
            'fields': ['name', ],
        }),
    ]

"""
Класс для встраивания изображений акций в административную панель.
"""

class SaleImageInline(admin.TabularInline):
    model = Sale.images.through
    extra = 1

"""
Администратор акций.
"""

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price', 'salePrice', 'dateFrom', 'dateTo')
    list_filter = ('dateFrom', 'dateTo')
    search_fields = ('title',)
    inlines = [
        SaleImageInline,
    ]
    fieldsets = [
        (None, {
            'fields': ['title', 'price', 'salePrice', 'dateFrom', 'dateTo', 'images'],
        })
    ]


admin.site.register(SaleImage)


"""
Форма заказов в админ панели.
"""

class OrderForm(forms.ModelForm):
    products = ModelMultipleChoiceField(queryset=Product.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Order
        fields = '__all__'

    def clean_products(self):
        products = self.cleaned_data['products']
        products_list = []
        for product in products:
            product_dict = {
                'id': product.id,
                'category': product.category.pk,
                'title': product.title,
                'price': float(product.price),
                'date': product.date.strftime('%Y-%m-%d %H:%M:%S'),
                'description': product.description,
                'freeDelivery': product.freeDelivery,
                'images': [{'src': image.src.url, 'alt': image.alt} for image in product.images.all()],
                'count': 1
            }
            products_list.append(product_dict)
        return products_list


"""
Администратор заказов.
"""

class OrderAdmin(admin.ModelAdmin):
    form = OrderForm
    list_display = (
    'fullName', 'email', 'phone', 'deliveryType', 'paymentType', 'totalCost', 'status', 'city', 'address', 'user',
    'is_deleted')
    list_filter = ('deliveryType', 'paymentType', 'status')
    search_fields = ('fullName', 'email', 'phone', 'city', 'address')
    actions = ['soft_delete_orders']

    def save_model(self, request, obj, form, change):
        obj.products = form.cleaned_data['products']
        obj.total_cost = sum(product['price'] for product in form.cleaned_data['products'])
        super().save_model(request, obj, form, change)

    def soft_delete_orders(self, request, queryset):
        # Метод для мягкого удаления выбранных заказов
        queryset.update(is_deleted=True)


admin.site.register(Order, OrderAdmin)
