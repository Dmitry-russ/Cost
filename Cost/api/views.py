from api.models import Cost, Group
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .permissions import IsAuthorOrReadOnly
from .serializers import CostSerializer, GroupSerializer


class CostViewSet(viewsets.ModelViewSet):
    queryset = Cost.objects.all()
    serializer_class = CostSerializer
    permission_classes = (IsAuthenticated, IsAuthorOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
