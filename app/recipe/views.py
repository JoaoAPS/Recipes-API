from rest_framework import viewsets, mixins, permissions
from rest_framework.authentication import TokenAuthentication

from recipe import models, serializers


class TagViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
):
    """Manage tags in the database"""
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        """Return objects of the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a new tag"""
        serializer.save(user=self.request.user)
