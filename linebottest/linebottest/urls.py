"""
URL configuration for linebottest project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin  # import Django admin site for administration interface
from django.urls import path, re_path  # path for simple routes, re_path for regex-based routes
from testapp.views import callback  # import webhook callback view to handle incoming LINE events

urlpatterns = [
    # Define LINE webhook callback route: match exact '/callback' URL using regex
    # This endpoint receives POST requests from LINE platform to trigger message handling
    re_path(r'^callback$', callback, name='linebot_callback'),
    # Define Django admin interface route under '/admin/' URL
    path('admin/', admin.site.urls, name='admin'),
]

