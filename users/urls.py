from django.urls import path
from .views import logout_api, register_api
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from .views import register_api,login_api


urlpatterns = [
    path("register/", register_api, name="register_api"),
    path("login/", login_api, name="login_api"),
    path("logout/", logout_api, name="logout_api"),
]
