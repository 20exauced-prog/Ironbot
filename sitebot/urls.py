from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.views.generic import TemplateView

from .views import healthcheck

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('health/', healthcheck, name='healthcheck'),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('licenses/', include('licenses.urls')),
]
