from rest_framework import serializers
from products.serializers import ProductSerializer, ProductImageSerializer, TagSerializer
class BasketSerializer(serializers.Serializer):
    """
    Сериализатор для объектов корзины.

    Этот сериализатор используется для сериализации объектов корзины, которые представляют собой товары в корзине покупок.
    Он использует класс `serializers.Serializer` из Django Rest Framework.

    Атрибуты:
        product: Вложенное поле сериализатора, представляющее связанный объект Product.
        id: Целочисленное поле, представляющее идентификатор связанного объекта Product.
        category: Строковое поле, представляющее идентификатор категории связанного объекта Product.
        price: Целочисленное поле, представляющее цену связанного объекта Product.
        count: Целочисленное поле, представляющее количество единиц товара в корзине.
        date: Поле даты и времени, представляющее дату связанного объекта Product.
        title: Строковое поле, представляющее название связанного объекта Product.
        description: Строковое поле, представляющее описание связанного объекта Product.
        freeDelivery: Строковое поле, представляющее наличие бесплатной доставки для связанного объекта Product.
        images: Вложенное поле сериализатора, представляющее изображения связанного объекта Product.
        tags: Вложенное поле сериализатора, представляющее теги связанного объекта Product.
        reviews: Метод для получения количества отзывов о связанном объекте Product.
        rating: Метод для получения рейтинга связанного объекта Product.
    """
    product = ProductSerializer(read_only=True)
    id = serializers.IntegerField(source='product.id')
    category = serializers.CharField(source='product.category.id')
    price = serializers.IntegerField(source='product.price')
    count = serializers.IntegerField()
    date = serializers.DateTimeField(source='product.date')
    title = serializers.CharField(source='product.title')
    description = serializers.CharField(source='product.description')
    freeDelivery = serializers.CharField(source='product.freeDelivery')
    images = ProductImageSerializer(source='product.images', many=True)
    tags = TagSerializer(source='product.tags', many=True)
    reviews = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        """
            Возвращает рейтинг связанного объекта Product.

            Returns:
                int: Рейтинг товара.
        """
        return obj.product.rating
    def get_reviews(self, obj):
        """
            Возвращает количество отзывов о связанном объекте Product.

            Returns:
                int: Количество отзывов.
        """
        return obj.product.reviews.count()

