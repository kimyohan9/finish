from django.urls import path
from .views import logout_api, register_api, UserUpdateAPIView, UserDeleteAPIView
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from .views import register_api,login_api,kakao_login
from .views import kakao_login
from .views import ProfileView #EditProfileView

urlpatterns = [
    path("register/", register_api, name="register_api"),
    path("login/", login_api, name="login_api"),
    path("logout/", logout_api, name="logout_api"),
    path("api/kakao/login/", kakao_login, name="kakao_login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    #path('profile/edit/', EditProfileView.as_view(), name='edit_profile'),
    path("update/", UserUpdateAPIView.as_view(), name="user_update"),
    path("delete/", UserDeleteAPIView.as_view(), name="user_delete"),

]
