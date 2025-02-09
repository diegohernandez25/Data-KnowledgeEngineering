"""proj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path, re_path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from uaggregator import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('news/', views.news, name ='news'),
    path('schedule/', views.schedule, name='schedule'),
    path('room/', views.room, name ='room'),
    path('canteen/', views.canteen, name ='canteen'),
    path('parkinglot/', views.parkinglot, name ='parkinglot'),
    path('weather/', views.weather, name ='weather'),
    path('sac/',views.sac, name='sac'),
	path('', views.index, name = 'index'),
]

urlpatterns += staticfiles_urlpatterns()
