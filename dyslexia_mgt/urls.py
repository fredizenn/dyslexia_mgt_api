"""
URL configuration for dyslexia_mgt project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from user.views import CustomTokenObtainPairView, ExerciseDetailView, ExerciseListCreateView, NextExerciseView, ProfileDetailView, ProgressDetailView, ProgressHistoryView, ProgressReportView, ProgressSummaryView, RetrieveProgressView, TextContentDetailView, TextContentListCreateView, UpdateProgressView, register_user
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('login/', LoginUser.as_view(), name='login'),
    path('api/profile/', ProfileDetailView.as_view(), name='profile_detail'),
    path('api/register/', register_user, name='register_user'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/text-content/', TextContentListCreateView.as_view(), name='text-content-list-create'),
    path('api/text-content/<int:pk>/', TextContentDetailView.as_view(), name='text-content-detail'),
    path('api/exercises/', ExerciseListCreateView.as_view(), name='exercise-list-create'),
    path('api/exercises/<int:pk>/', ExerciseDetailView.as_view(), name='exercise-detail'),
    path('api/progress/', RetrieveProgressView.as_view(), name='retrieve-progress'),
    path('api/progress/<int:pk>/', ProgressDetailView.as_view(), name='progress-detail'),
    path('api/progress/update/', UpdateProgressView.as_view(), name='update-progress'),
    path('api/progress/report/', ProgressReportView.as_view(), name='progress-report'),
    path('api/progress/history/', ProgressHistoryView.as_view(), name='progress-history'),
    path('api/progress/summary/', ProgressSummaryView.as_view(), name='progress-summary'),
    path('api/exercises/next/', NextExerciseView.as_view(), name='next-exercise'),
]
