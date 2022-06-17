from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # базовые, для управления пользователями в Django:
    path('auth/', include('djoser.urls')),
    # JWT-эндпоинты, для управления JWT-токенами:
    path('auth/', include('djoser.urls.jwt')),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
]
