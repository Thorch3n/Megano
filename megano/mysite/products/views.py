"""
API для взаимодействия с категориями, товарами, отзывами, заказами, акциями и корзиной.

Предоставляет возможность получения данных о категориях, товарам, отзывах, заказах, акциях и корзине, а также создания новых заказов и обновления статуса заказов.
"""
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count, Avg
from django.http import HttpRequest
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from basket.models import Basket, BasketItem
from .models import Category, Product, Tag, Review, Order, Sale
from .serializers import CategorySerializer, ProductSerializer, TagSerializer, ReviewSerializer, \
    BannerProductSerializer, SaleSerializer


class CategoryView(APIView):
    """
        API для взаимодействия с категориями.

        Методы:
            - GET: Получение списка категорий.
    """
    def get(self, request):
        """
            Получение списка категорий.

            Возвращает:
                JSON-ответ с данными о категориях.
        """
        categories = Category.objects.filter(parent__isnull=True)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class ProductView(APIView):
    """
        API для взаимодействия с товарами.

        Методы:
            - GET: Получение информации о товаре по его идентификатору.
    """
    def get(self, request, pk):
        """
            Получение информации о товаре по его идентификатору.

            Аргументы:
                pk: Идентификатор товара.

            Возвращает:
                JSON-ответ с данными о товаре.
        """
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


        serializer = ProductSerializer(product)
        data = serializer.data# Добавляем список словарей спецификаций в данные сериализатора
        return Response(data)

class CatalogView(APIView):
    """
        API для взаимодействия с каталогом товаров.

        Методы:
            - GET: Получение каталога товаров с применением заданных фильтров и пагинацией.
    """
    count_rate = 0
    full_rate = 0
    product_rate = 0
    def get(self, request: HttpRequest):
        """
            Получение каталога товаров с применением заданных фильтров и пагинацией.

            Аргументы:
                request: Объект запроса.

            Возвращает:
                JSON-ответ с данными о каталоге товаров.
        """
        # Получаем параметры фильтрации из запроса
        filter_params = request.GET

        # Получаем объекты товаров, соответствующие параметрам фильтрации
        products = Product.objects.filter(is_deleted=False)


        # Применяем фильтрацию по имени товара, если указано
        name = filter_params.get('filter[name]')
        if name:
            products = products.filter(title=name)

        # Применяем фильтрацию по минимальной цене, если указано
        min_price = filter_params.get('filter[minPrice]')
        if min_price:
            products = products.filter(price__gte=min_price)

        # Применяем фильтрацию по максимальной цене, если указано
        max_price = filter_params.get('filter[maxPrice]')
        if max_price:
            products = products.filter(price__lte=max_price)

        # Применяем фильтрацию по бесплатной доставке, если указано
        free_delivery = filter_params.get('filter[freeDelivery]') == 'true'
        if free_delivery:
            products = products.filter(freeDelivery=free_delivery)

        # Применяем фильтрацию по наличию товара, если указано
        available = filter_params.get('filter[available]')
        if available is not None:
            products = products.filter(count__gt=0)

        category = filter_params.get('category')
        if category is not None:
            products = products.filter(category=category)

        tags = request.query_params.getlist("tags[]")
        if tags:
            products = products.filter(tags__in=tags)


        # Получаем параметры сортировки из запроса
        sort_by = filter_params.get('sort')
        sort_type = filter_params.get('sortType')


        if sort_by:
            if sort_by == 'reviews':
                products = products.annotate(num_reviews=Count('reviews')).order_by(
                    '-num_reviews' if sort_type == 'dec' else 'num_reviews')
            elif sort_by == 'rating':
                products = products.order_by('-number_of_sales' if sort_type == 'dec' else 'number_of_sales')
            elif sort_by == 'price':
                products = products.order_by('-price' if sort_type == 'dec' else 'price')
            elif sort_by == 'date':
                products = products.order_by('-date' if sort_type == 'dec' else 'date')

        # Пагинация
        page = request.GET.get('page', 1)
        items_per_page = 10
        paginator = Paginator(products, items_per_page)
        try:
            paginated_products = paginator.page(page)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages)

        # Формируем список товаров для вывода
        items = []
        for product in paginated_products:
            product_reviews = Review.objects.filter(product=product.id)
            product_reviews_data = []
            for product_review in product_reviews:
                product_review_data = {
                    'author': product_review.author,
                    'email': product_review.email,
                    'text': product_review.text,
                    'rate': product_review.rate,
                    'date': product_review.date,
                }
                product_reviews_data.append(product_review_data)
                self.count_rate += 1
                self.full_rate += float(product_review.rate)
                self.product_rate = self.full_rate / self.count_rate
            item = {
                'id': product.id,
                'category': product.category.id,
                'price': float(product.price),  # Преобразуем Decimal в float
                'count': product.count,
                'date': product.date.strftime('%a %b %d %Y %H:%M:%S GMT%z (%Z)'),
                'title': product.title,
                'description': product.description,
                'fullDescription': product.fullDescription,
                'freeDelivery': product.freeDelivery,
                'images': [{'src': image.src.url, 'alt': image.alt} for image in product.images.all()],
                'tags': [{'name': tag.name} for tag in product.tags.all()],
                'reviews': product_reviews_data,
                'rating': self.product_rate,
            }
            items.append(item)

        # Формируем ответ
        response_data = {
            'items': items,
            'currentPage': paginated_products.number,
            'lastPage': paginated_products.paginator.num_pages,
        }

        return Response(response_data)


class PopularProduct(APIView):
    """
        API для получения популярных товаров.

        Методы:
            - GET: Получение списка популярных товаров.
    """
    def get(self, request):
        """
            Получение популярных товаров с сортировкой по индексу сортировки, либо количеству продаж.

            Аргументы:
                request: Объект запроса.

            Возвращает:
                JSON-ответ с данными о популярных товаров.
        """
        # Получаем продукты и сортируем их по индексу сортировки и количеству покупок
        products = Product.objects.annotate(avg_rating=Avg('reviews__rate')).order_by('-index_sort', '-number_of_sales').filter(is_deleted=False)

        # Отбираем первые восемь продуктов
        products = products[:8]

        # Сериализуем выбранные продукты
        serializer = ProductSerializer(products, many=True)

        return Response(serializer.data)


class LimitedProduct(APIView):
    """
        API для получения товаров с ограниченным тиражом.

        Методы:
            - GET: Получение списка товаров с ограниченным тиражом.
    """
    def get(self, request):
        """
            Получение товаров с огрниченным тиражом с фильтрацией по limited_edition.

            Аргументы:
                request: Объект запроса.

            Возвращает:
                JSON-ответ с данными о товарах с ограниченным тиражом.
        """
        # Получаем товары, отфильтрованные по limited_edition
        limited_products = Product.objects.filter(limited_edition=True, is_deleted=False)[:16]

        # Сериализуем выбранные товары
        serializer = ProductSerializer(limited_products, many=True)

        return Response(serializer.data)


class BannerView(APIView):
    """
        API для получения товаров для баннеров.

        Методы:
            - GET: Получение списка товаров для использования в баннерах.
    """
    def get(self, request):
        """
            Получение товаров для баннеров.

            Аргументы:
                request: Объект запроса.

            Возвращает:
                JSON-ответ с данными о товарах.
        """

        products = Product.objects.order_by('-date').filter(is_deleted=False)[:3]  # Получаем три последних продукта
        serializer = BannerProductSerializer(products, many=True)
        return Response(serializer.data)


class TagsView(APIView):
    """
        API для получения списка тегов.

        Методы:
            - GET: Получение списка всех тегов.
    """
    def get(self, request):
        """
        Получение всех существующих тегов.

        Аргументы:
            request: Объект запроса.

        Возвращает:
            JSON-ответ с данными о тегах
        """
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)

class ProductReview(APIView):
    """
        API для добавления отзыва о товаре.

        Методы:
            - POST: Добавление нового отзыва о товаре.
    """
    def post(self, request, pk):
        """
        Добавление нового отзыва о товаре

        Аргументы:
            request: Объект запроса.
            pk: Основной ключ продукта.

        Возвращает:
            JSON-ответ с данными о созданом товара и статусом 201
        """
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()

        serializer = ReviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderView(APIView):
    """
        API для взаимодействия с заказами.

        Методы:
            - GET: Получение списка заказов текущего пользователя.
            - POST: Создание нового заказа.
    """
    def get(self, request):
        """
        Получение списка заказов текущего пользователя

        Аргументы:
            request: Объект запроса

        Возвращает:
            JSON-ответ со всеми заказами пользователя
        """
        orders = Order.objects.filter(user=request.user)
        if not orders:
            return Response([])  # Возвращаем пустой список заказов
        order_data = []
        for order in orders:
            order_info = {
                'id': order.id,
                'createdAt': order.createdAt,
                'fullName': order.fullName,
                'email': order.email,
                'phone': order.phone,
                'deliveryType': order.deliveryType,
                'paymentType': order.paymentType,
                'totalCost': order.totalCost,
                'status': order.status,
                'city': order.city,
                'address': order.address,
                'products': order.products
            }
            order_data.append(order_info)
        return Response(order_data)

    def post(self, request):
        """
        Создание нового заказа

        Аргументы:
            request: Объект запроса

        Возвращает:
            Json-ответ с основным ключом созданного заказа
        """
        # Получаем данные о продуктах из запроса
        products_data = request.data
        if request.user.is_authenticated:
            user = request.user
            order = Order.objects.create(user=user)
        else:
            order = Order.objects.create()
        total_cost = 0
        for product in products_data:
            product_info = {
                'id': product['id'],
                'category': product['category'],
                'price': product['price'],
                'count': product['count'],
                'date': product['date'],
                'title': product['title'],
                'description': product['description'],
                'freeDelivery': product['freeDelivery'],
                'images': product['images'],
            }
            total_cost += product['price']
            print(product_info)
            order.products.append(product_info)
            order.totalCost = total_cost

            order.save()
        if total_cost < 2000:
            order.totalCost = total_cost + 200
            order.save()
        basket = Basket.objects.get(user=request.user)
        basket_items = BasketItem.objects.filter(basket=basket)
        basket_items.delete()

        return Response({'orderId': order.id}, status=status.HTTP_201_CREATED)

class OrderDetail(APIView):
    """
        API для получения информации о конкретном заказе и его обновления.

        Методы:
            - GET: Получение информации о конкретном заказе.
            - POST: Обновление информации о конкретном заказе.
    """
    def get(self, request, pk):
        """
        Получение информации о конкретном заказе

        Аргументы:
            request: Объект запроса
            pk: Основной ключ заказа

        Возвращает:
            Json-ответ с информацией о заказе
        """

        order = Order.objects.get(pk=pk)

        order_info = {
            'id': order.id,
            'createdAt': order.createdAt,
            'fullName': order.fullName,
            'email': order.email,
            'phone': order.phone,
            'deliveryType': order.deliveryType,
            'paymentType': order.paymentType,
            'totalCost': order.totalCost,
            'status': order.status,
            'city': order.city,
            'address': order.address,
            'products': order.products
        }

        return Response(order_info)

    def post(self, request, *args, **kwargs):
        """
            Обновление информации о конкретном заказе

            Аргументы:
                request: Объект запроса

            Возвращает:
                Json-ответ с основным ключом заказа
        """
        order = Order.objects.get(pk=kwargs['pk'])
        order.fullName = request.data['fullName']
        order.email = request.data['email']
        order.phone = request.data['phone']
        order.deliveryType = request.data['deliveryType']
        order.paymentType = request.data['paymentType']
        order.totalCost = request.data['totalCost']
        order.status = request.data['status']
        order.city = request.data['city']
        order.address = request.data['address']
        order.save()

        return Response({'orderId': order.id})


class PaymentView(APIView):
    """
        API для обработки оплаты заказа.

        Методы:
            - POST: Установка статуса оплаты заказа.
    """
    def post(self, request, pk):
        """
        Установка статуса оплаты заказа

        Аргументы:
            request: Объект заказа
            pk: Основной ключ заказа

        Возвращает:
            Ответ 200 об успешной оплате товара

        """
        print(request.data)
        order = Order.objects.get(pk=pk)
        order.status = 'Accepted'
        order.save()
        return Response(status=status.HTTP_200_OK)
class SaleListAPIView(APIView):
    """
        API для получения списка акций.

        Методы:
            - GET: Получение списка акций.
    """
    def get(self, request):
        """
        Получение списка акций

        Аргументы:
            request: Объект заказа

        Возвращает:
            JSON-ответ с информацией об акциях, текущей страницы и количеством страниц
        """
        # Получаем параметры запроса
        currentPage = request.GET.get('currentPage', 1)

        # Здесь может быть логика для фильтрации или сортировки акций, если требуется

        # Получаем объекты Sale
        sales = Sale.objects.all()

        # Создаем объект сериализатора и сериализуем данные
        serializer = SaleSerializer(sales, many=True)

        # Возвращаем список акций в JSON формате
        return Response({
            'items': serializer.data,
            'currentPage': currentPage,
            'lastPage': 10  # Здесь нужно указать общее количество страниц
        })