from django.urls import path
from . import views
urlpatterns = [path('stock/<str:direction>/', views.stock, name='stock'), path('transactions/', views.transactions, name='transactions')]
for slug, prefix in [('products', 'product'), ('categories', 'category')]:
    urlpatterns += [path(f'{slug}/', getattr(views, prefix + '_list'), name=slug + '-list'), path(f'{slug}/new/', getattr(views, prefix + '_edit'), name=slug + '-create'), path(f'{slug}/<int:pk>/', getattr(views, prefix + '_detail'), name=slug + '-detail'), path(f'{slug}/<int:pk>/edit/', getattr(views, prefix + '_edit'), name=slug + '-edit'), path(f'{slug}/<int:pk>/archive/', getattr(views, prefix + '_archive'), name=slug + '-archive')]
