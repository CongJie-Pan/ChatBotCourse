from django.urls import path
from . import views

# URL patterns for the translateapi application
urlpatterns = [
    path('callback', views.callback, name='callback'),  # LINE Bot webhook callback endpoint
] 