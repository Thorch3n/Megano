"""
Сериализаторы для взаимодействия с моделями категорий, изображений категорий, товаров, отзывов, изображений товаров, тегов, акций и изображений акций.

Сериализаторы обеспечивают преобразование данных из формата моделей в формат JSON и обратно для взаимодействия с REST API.

Сериализаторы:
    CategoryImageSerializer: Сериализатор изображений категорий.
    CategorySerializer: Сериализатор категорий.
    ProductImageSerializer: Сериализатор изображений товаров.
    TagSerializer: Сериализатор тегов.
    ReviewSerializer: Сериализатор отзывов.
    SpecificationSerializer: Сериализатор спецификаций товаров.
    ProductSerializer: Сериализатор товаров.
    BannerProductSerializer: Сериализатор товаров для баннеров.
    SaleImageSerializer: Сериализатор изображений акций.
    SaleSerializer: Сериализатор акций.
"""

from rest_framework import serializers
from .models import Category, CategoryImage, Product, Review, ProductImages, Tag, Sale, SaleImage, Specification


class CategoryImageSerializer(serializers.ModelSerializer):
    """
        Сериализатор изображений категорий.
    """
    class Meta:
        model = CategoryImage
        fields = ('src', 'alt')


class CategorySerializer(serializers.ModelSerializer):
    """
        Сериализатор категорий.
    """
    image = CategoryImageSerializer()
    subcategories = serializers.SerializerMethodField()

    def get_subcategories(self, obj):
        subcategories = obj.subcategories.all()
        return CategorySerializer(subcategories, many=True).data

    class Meta:
        model = Category
        fields = ('id', 'title', 'image', 'subcategories')


class ProductImageSerializer(serializers.ModelSerializer):
    """
        Сериализатор изображений товаров.
    """
    class Meta:
        model = ProductImages
        fields = ('src', 'alt')
class TagSerializer(serializers.ModelSerializer):
    """
        Сериализатор тегов.
    """
    class Meta:
        model = Tag
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    """
        Сериализатор отзывов.
    """
    class Meta:
        model = Review
        fields = ['author', 'email', 'text', 'rate', 'date']

class SpecificationSerializer(serializers.ModelSerializer):
    """
        Сериализатор спецификаций товаров.
    """
    class Meta:
        model = Specification
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    """
        Сериализатор товаров.
    """
    category = CategorySerializer()
    tags = TagSerializer(many=True)
    images = ProductImageSerializer(many=True)
    specifications = SpecificationSerializer(many=True, source='specification_set')
    reviews = ReviewSerializer(many=True)
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        return obj.rating

    class Meta:
        model = Product
        fields = (
        'id', 'category', 'price', 'count', 'date', 'title', 'description', 'freeDelivery', 'tags', 'images', 'reviews',
        'rating', 'specifications', 'number_of_sales')



class BannerProductSerializer(serializers.ModelSerializer):
    """
        Сериализатор товаров для баннеров.
    """
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    images = ProductImageSerializer(many=True)
    class Meta:
        model = Product
        fields = ('id', 'category', 'price', 'count', 'date', 'title', 'description', 'freeDelivery', 'images', 'tags', 'rating')


class SaleImageSerializer(serializers.ModelSerializer):
    """
        Сериализатор изображений акций.
    """
    class Meta:
        model = SaleImage
        fields = ('src', 'alt')

class SaleSerializer(serializers.ModelSerializer):
    """
        Сериализатор акций.
    """
    images = SaleImageSerializer(many=True, read_only=True)

    class Meta:
        model = Sale
        fields = ('id', 'price', 'salePrice', 'dateFrom', 'dateTo', 'title', 'images')
