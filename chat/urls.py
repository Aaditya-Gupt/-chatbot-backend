# C:\Users\Dell\chatbot_project\chat\urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/clear/', views.clear_chat, name='clear_chat'),  # Changed from 'clear/' to 'api/clear/'
    path('api/chat/', views.chat_api.as_view(), name='chat_api'),
    path('api/gif/', views.gif_view, name='gif_api'),
]