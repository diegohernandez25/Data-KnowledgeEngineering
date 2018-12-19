"""proj2 URL Configuration

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
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from airlines import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name = 'index'),
    path('api/country/<str:country>/cities', views.getCities, name = 'getCities'),
    path('api/country/<str:country>/airports', views.getAirports, name = 'getAirports'),
    path('api/routes/city/<str:src>/city/<str:dst>', views.getAirports, name = 'getAirports'),
    path('api/routes/country/<str:src>/city/<str:dst>', views.getAirports, name = 'getAirports'),
    path('api/routes/city/<str:src>/country/<str:dst>', views.getAirports, name = 'getAirports'),
    path('api/routes/continent/<str:src>/city/<str:dst>', views.getAirports, name = 'getAirports'),
    path('api/routes/city/<str:src>/continent/<str:dst>', views.getAirports, name = 'getAirports'),
    path('api/routes/country/<str:src>/country/<str:dst>', views.getAirports, name = 'getAirports'),
    path('api/routes/continent/<str:src>/continent/<str:dst>', views.getAirports, name = 'getAirports'),
    path('api/routes/continent/<str:src>/country/<str:dst>', views.getAirports, name = 'getAirports'),
    path('api/routes/country/<str:src>/continent/<str:dst>', views.getAirports, name = 'getAirports'),
	path('api/city/<str:city>/monuments', views.getMonumentCoords, name = 'getMonumentCoords'),
	path('api/monument/<str:obj>', views.getDestination, name = 'getDestination'),
    path('api/city/<str:city>/airports', views.getCityAirports, name = 'getCityAirports'),
    path('api/country/<str:country>/airports', views.getCountryAirports, name = 'getCountryAirports'),
    path('api/routes/<str:src>/<str:dst>', views.getRoutes, name = 'getRoutes'),
    path('api/city/orig/<str:orig>/dest/<str:dest>/coord', views.getCityCoords, name = 'getCityCoords'),
]

urlpatterns += staticfiles_urlpatterns()
