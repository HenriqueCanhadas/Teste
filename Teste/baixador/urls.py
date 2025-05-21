from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('videos.urls')),  # ✅ Isso aponta para o urls.py do seu app
]