from django.urls import path
from . import views
urlpatterns = [path('', views.supplier_list, name='suppliers-list'), path('new/', views.supplier_edit, name='suppliers-create'), path('<int:pk>/', views.supplier_detail, name='suppliers-detail'), path('<int:pk>/edit/', views.supplier_edit, name='suppliers-edit'), path('<int:pk>/archive/', views.supplier_archive, name='suppliers-archive')]
