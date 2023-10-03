from django.urls import path
from .views import LoginView, UploadView, DownloadView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('upload/', UploadView.as_view(), name='upload'),
    path('download/', DownloadView.as_view(), name='download'),
]
