
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from exercise.views import (ProgramViewSet, SessionViewSet,
                            ExerciseViewSet, WorkoutCategoryViewSet,
                            UserProgramViewSet,UserFullProgramDetailView,ProgressView,
                            UserProgramAllViewSet,StartSessionView)
from food.views import CompleteMealView

# Initialize a single router for all viewsets
router = DefaultRouter()
router.register(r'programs', ProgramViewSet, basename='program')
router.register(r'sessions', SessionViewSet, basename='session')
router.register(r'exercises', ExerciseViewSet, basename='exercise')
router.register(r'workout-categories', WorkoutCategoryViewSet, basename='workoutcategory')
router.register(r'userprogram', UserProgramViewSet, basename='userprogram')

# Define the API URL patterns
urlpatterns = [
    path('api/', include(router.urls)),
]


urlpatterns += [
    path('user/full-program/', UserFullProgramDetailView.as_view(), name='user-full-program-detail'),
    path('user/userprogramall/', UserProgramAllViewSet.as_view(),name='all-user-programs'),
    # path('user/userprogress/', UpdateProgressView.as_view(), name='user-progress'),
    path('sessions/complete/', StartSessionView.as_view(), name='start_session'),
    path('user/statistics/',ProgressView.as_view(),name='user-progress'),
    path('api/meal/complete/', CompleteMealView.as_view(), name='complete-meal'),
]