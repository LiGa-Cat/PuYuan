"""PuYuan URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from .views import friend_accept, friend_code, friend_list, friend_refuse, friend_remove, friend_remove_more, friend_requests, friend_results, friend_send
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("code/",friend_code),
    path("list/",friend_list),
    path("send/",friend_send),
    path("requests/",friend_requests),
    path("<int:friend_data_id>/accept/",friend_accept),
    path("<int:friend_data_id>/refuse/",friend_refuse),
    path("<int:friend_data_id>/remove/",friend_remove),
    path("results/",friend_results),
    path("remove/",friend_remove_more)
]
