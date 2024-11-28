from django.urls import path, include
from rest_framework.routers import DefaultRouter
from food.views import (MealViewSet, MealCompletionViewSet,
                        CompleteMealView,PreparationViewSet)
from django.conf import settings
from django.conf.urls.static import static

# Define routers for Meal and MealCompletion viewsets
meal_router = DefaultRouter()
meal_router.register(r'', MealViewSet, basename='meal')

meal_completion_router = DefaultRouter()
meal_completion_router.register(r'', MealCompletionViewSet, basename='mealcompletion')


preparation_router=DefaultRouter()
preparation_router.register(r'',PreparationViewSet,basename='preparation')


# Organized URL patterns
urlpatterns = [
    path('api/meals/', include((meal_router.urls, 'meal'))),
    path('api/mealcompletion/', include((meal_completion_router.urls, 'mealcompletion'))),
    path('api/preparation/',include((preparation_router.urls,'preparation'))),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
