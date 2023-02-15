from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

# from .views import UserViewSet
from .views import (IngredientViewSet, RecipeViewSet, SubscriptionsViewSet,
                    TagViewSet)

router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
# router.register('users', UserViewSet)


urlpatterns = [
    path('api/', include(router.urls)),
    path('api/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),

    path('api/users/subscriptions/',
         SubscriptionsViewSet.as_view({'get': 'list'})),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc')
]
