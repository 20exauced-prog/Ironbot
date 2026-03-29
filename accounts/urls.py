from django.urls import path

from .views import IronbotLoginView, signup

urlpatterns = [
    path('login/', IronbotLoginView.as_view(), name='login'),
    path('signup/', signup, name='signup'),
]
