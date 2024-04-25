
from django.urls import path
from django.views.generic import RedirectView

from .views import BasketAPIView

urlpatterns = [
    path('basket/', BasketAPIView.as_view(), name='basket'),
]