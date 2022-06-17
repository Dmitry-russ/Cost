from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken import views

urlpatterns = [
    path('api/v1/api-token-auth/', views.obtain_auth_token),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
]
