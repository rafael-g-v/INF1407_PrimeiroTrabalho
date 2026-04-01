from django.urls import path
from Core import views

app_name = 'Core'

urlpatterns = [
    path('', views.home),
]