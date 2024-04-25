from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import (
    CategoryView,
    ProductView,
    CatalogView,
    PopularProduct,
    LimitedProduct,
    BannerView,
    TagsView,
    ProductReview,
    OrderView,
    SaleListAPIView,
    OrderDetail,
    PaymentView,
)

urlpatterns = [
    path('categories',  CategoryView.as_view(), name='category'),
    path('product/<int:pk>',  ProductView.as_view(), name='product'),
    path('product/<int:pk>/reviews',  ProductReview.as_view(), name='product-review'),
    path('products/popular',  PopularProduct.as_view(), name='products-popular'),
    path('products/limited',  LimitedProduct.as_view(), name='products-limited'),
    path('catalog',  CatalogView.as_view(), name='catalog'),
    path('banners',  BannerView.as_view(), name='banners'),
    path('tags',  TagsView.as_view(), name='tags'),
    path('orders',  OrderView.as_view(), name='orders'),
    path('order/<int:pk>',  OrderDetail.as_view(), name='order'),
    path('sales',  SaleListAPIView.as_view(), name='sales'),
    path('payment/<int:pk>',  PaymentView.as_view(), name='payment'),
]