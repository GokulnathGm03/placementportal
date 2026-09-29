from django.contrib import admin
from django.urls import path, include
from config.views import health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='api-health'),
    path('api/', include('placements.urls')),
    path('api/students/', include('students.urls')),
]
