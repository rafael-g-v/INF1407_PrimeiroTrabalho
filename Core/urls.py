from django.urls import path
from Core import views

app_name = 'Core'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registrar/', views.register_view, name='registrar'),
]