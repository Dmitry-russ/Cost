from django.shortcuts import get_object_or_404
from api.models import Cost, Group, User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from djoser.views import UserViewSet

from .permissions import IsAuthorOrReadOnly
from .serializers import CostSerializer, GroupSerializer, CustomUserSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer


class CostViewSet(viewsets.ModelViewSet):
    serializer_class = CostSerializer
    permission_classes = (IsAuthenticated, IsAuthorOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        author = get_object_or_404(User, id=self.request.user.id)
        return author.costs.all()


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
