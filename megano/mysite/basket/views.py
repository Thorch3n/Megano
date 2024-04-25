"""
API представление для работы с корзиной.

Это представление API используется для выполнения операций над корзиной, такими как получение, добавление и удаление товаров из корзины.

Методы:
    get_or_create_basket: Получает или создает корзину для данного запроса.
    get: Обрабатывает запрос GET для получения содержимого корзины.
    post: Обрабатывает запрос POST для добавления товара в корзину.
    delete: Обрабатывает запрос DELETE для удаления товара из корзины.
"""

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from basket.models import Basket, BasketItem
from basket.serializers import BasketSerializer
from products.models import Product


class BasketAPIView(APIView):
    def get_or_create_basket(self, request):
        """
            Получает или создает корзину для данного запроса.

            Args:
                request: Запрос HTTP.

            Returns:
                Basket: Объект корзины.
        """
        # Получаем или создаем объект сессии для данного запроса
        session_key = request.session.session_key
        if request.user.is_authenticated:
            basket, _ = Basket.objects.get_or_create(user=request.user)
            return basket
        # Получаем идентификатор корзины из сессии
        basket_id = request.session.get('basket_id')

        # Если корзина не существует, создаем новую
        if not basket_id:
            basket = Basket.objects.create()
            basket_id = basket.id
            # Сохраняем идентификатор корзины в сессии
            request.session['basket_id'] = basket_id
            request.session.save()
        else:
            # Если корзина существует, получаем ее из базы данных
            basket = Basket.objects.get(id=basket_id)
        if request.user.is_authenticated:
            user_basket, _ = Basket.objects.get_or_create(user=request.user)
            for item in basket.items.all():
                item.basket = user_basket
                item.save()
            basket.delete()
            return user_basket

        return basket

    def get(self, request):
        """
            Обрабатывает запрос GET для получения содержимого корзины.

            Args:
                request: Запрос HTTP.

            Returns:
                Response: Ответ HTTP с данными корзины.
        """
        basket = self.get_or_create_basket(request)

        # Возвращаем данные корзины
        serializer = BasketSerializer(basket.items.all(), many=True)
        return Response(serializer.data)

    def post(self, request):
        """
            Обрабатывает запрос POST для добавления товара в корзину.

            Args:
                request: Запрос HTTP.

            Returns:
                Response: Ответ HTTP с обновленными данными корзины.
        """
        basket = self.get_or_create_basket(request)

        # Обработка добавления товара в корзину
        product_id = request.data.get('id')
        print(product_id)
        count = request.data.get('count', 0)
        print(count)
        product = get_object_or_404(Product, id=product_id)
        basket_item, created = BasketItem.objects.get_or_create(basket=basket, product=product)
        basket_item.count += int(count)
        basket_item.save()

        # Возвращаем обновленные данные корзины
        serializer = BasketSerializer(basket.items.all(), many=True)
        return Response(serializer.data)

    def delete(self, request):
        """
            Обрабатывает запрос DELETE для удаления товара из корзины.

            Args:
                request: Запрос HTTP.

            Returns:
                Response: Ответ HTTP с обновленными данными корзины.
        """
        basket = self.get_or_create_basket(request)

        # Обработка уменьшения количества товара в корзине
        product_id = request.data.get('id')
        basket_item = get_object_or_404(BasketItem, basket=basket, product_id=product_id)
        basket_item.count -= request.data.get('count', 0)
        if basket_item.count > 0:
            basket_item.save()
        else:
            basket_item.delete()
        serializer = BasketSerializer(basket.items.all(), many=True)
        return Response(serializer.data)
