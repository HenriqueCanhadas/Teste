from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('download/<str:filename>', views.download_file, name='download_file'),
    path('stream-download/', views.stream_download, name='stream_download'),  # ✅ ESSA LINHA É ESSENCIAL
    path('download-zip/', views.download_zip, name='download_zip'),
]