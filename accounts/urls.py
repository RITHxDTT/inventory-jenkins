from django.urls import path, include
from . import views
urlpatterns = [path('', include('django.contrib.auth.urls')), path('profile/', views.profile, name='profile'), path('users/', views.users, name='users'), path('users/new/', views.user_edit, name='users-create'), path('users/<int:pk>/edit/', views.user_edit, name='users-edit'), path('roles/', views.roles, name='roles'), path('roles/new/', views.role_edit, name='roles-create'), path('roles/<int:pk>/edit/', views.role_edit, name='roles-edit')]
