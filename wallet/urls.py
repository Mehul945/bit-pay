from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('forget', views.forget_password, name='forget'),
    path('verify/<token>', views.verify ,name='verify'),
    path('reset/<token>', views.reset ,name='reset'),
    path('send', views.send, name='send'),
    path('logout', views.logout, name='logout'),
]