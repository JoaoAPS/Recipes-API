from rest_framework import viewsets, mixins, permissions, authentication

from recipe import models, serializers


class BaseRecipeAttrViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
):
    """Superclass with the base functionality for api viewsets"""
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def get_queryset(self):
        """Return objects of the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('name')

    def perform_create(self, serializer):
        """Create a new object setting the user"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags on the database"""
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients on the database"""
    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes on the database"""
    queryset = models.Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes for authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('title')

    def get_serializer_class(self):
        """Return the serializer to be used in the response"""
        if self.detail:
            return serializers.RecipeDetailSerializer
        return self.serializer_class
