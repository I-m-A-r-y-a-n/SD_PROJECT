from django.urls import path
from .views import register_user, login_user, login_page, signup_page, home_page
from . import views

urlpatterns = [
    path("api/register/", register_user),
    path("api/login/", login_user),
    path("api/search/", views.search_api, name="search_api"),
    path("api/history/", views.history_api, name="history_api"),
    path("api/logout/", views.logout_user, name="logout_user"),

    path("login/", login_page, name="login"),
    path("signup/", signup_page, name="signup"),
    path("home/", home_page, name="home"),
    path("api/feedback/", views.feedback_api, name="feedback_api"),
]