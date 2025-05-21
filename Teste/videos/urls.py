from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('download/<str:filename>', views.download_file, name='download_file'),
    path('stream-download/', views.stream_download, name='stream_download'),  # ✅ ESTA LINHA!
]
