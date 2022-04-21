from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.say_hello, name="say_hello"),
    path('hello2/', views.HelloView.as_view(), name="HelloView"),
]
