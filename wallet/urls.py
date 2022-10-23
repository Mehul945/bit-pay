from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('verify/<token>', views.verify ,name='verify'),
    path('send', views.send, name='send'),
    path('logout', views.logout, name='logout'),
]