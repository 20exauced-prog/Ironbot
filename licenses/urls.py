from django.urls import path
from .views import my_licenses

urlpatterns = [
    path('my-licenses/', my_licenses, name='my_licenses'),
]
