from api.models import Cost, Group, User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from djoser.views import UserViewSet

from .permissions import IsAuthorOrReadOnly
from .serializers import CostSerializer, GroupSerializer, CustomUserSerializer


class CustomUserViewSet(UserViewSet):
    """Функция обработки запросов к базе данных пользователей."""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer


class CostViewSet(viewsets.ModelViewSet):
    """Функция обработки запрсов к базе данных расходов."""
    serializer_class = CostSerializer
    permission_classes = (IsAuthenticated, IsAuthorOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        chat_id = self.kwargs.get("id")
        return Cost.objects.filter(chat_id=chat_id)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """Функция обработки запросов к базе данных категорий расхода."""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
