"""MedTech URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import include, path, re_path
from django.views.generic import RedirectView

from rest_framework import routers

from contacts import views

router = routers.DefaultRouter()
router.register(r'rest/contacts', views.ContactViewSet)
router.register(r'rest/companies', views.CompanyViewSet)


urlpatterns = [
    path('', views.ContactsList.as_view(), name='index'),
    path('companies/', views.CompaniesList.as_view(), name='companies'),
    path('contacts/', include(('contacts.urls', 'contacts'), namespace='contacts')),
    path('favicon.ico', RedirectView.as_view(url='/static/images/favicon.ico')),
    re_path(r'^', include(router.urls)),
    re_path('^api-auth/', include('rest_framework.urls'))
]
