from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),  # Home app URLs
    path('users/', include('users.urls')),  # Users app URLs
]
