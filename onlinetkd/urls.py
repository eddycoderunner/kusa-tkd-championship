from django.contrib import admin
from django.urls import path 
from django.views.generic import RedirectView

from .views import register_competitor, success_view, competitors_list, draws_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/register/', permanent=False)),
    path('register/', register_competitor, name='register_competitor'),
    path('success/', success_view, name='success'),
    path('competitors/', competitors_list, name='competitors_list'),
    path('draws/', draws_view, name='draws'),
]

