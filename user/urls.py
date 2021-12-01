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
from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('register/', views.register),
    path('auth/',views.login),
    path('logout/',views.logout),
    path('verification/send/',views.send),
    path('verification/check/<str:token>/',views.check),
    path('password/forgot/',views.forgot),
    path('password/reset/',views.reset),
    path('register/check/',views.registercheck),
    path('user/',views.userset), #/<str:uid>
    path('user/default/',views.userdefault),
    path('user/setting/',views.userdata),
    path('notification/',views.notification),
    path("user/a1c/",views.showHbA1c),
    path("user/medical/",views.Medical_information),
    path("user/drug-used/",views.drug),
    path('share/', views.share), #抄
    path('user/badge/',views.badge),#抄
    path('news/', views.newnews),#抄
    path('share/<int:relation_type>', views.share_check),#抄
]
