# urls.py

from django.urls import path


from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('validate/', views.ValidateView.as_view(), name='validate'),
    
    
]
