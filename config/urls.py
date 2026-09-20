from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from reports.views import dashboard
urlpatterns = [path('admin/', admin.site.urls), path('', dashboard, name='dashboard'), path('accounts/', include('accounts.urls')), path('', include('inventory.urls')), path('suppliers/', include('suppliers.urls')), path('reports/', include('reports.urls')), path('audit/', include('audit.urls'))]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
