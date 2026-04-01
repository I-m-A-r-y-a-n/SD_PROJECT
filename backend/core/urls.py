from django.urls import path
from .views import register_user, login_user, login_page, signup_page, home_page
from . import views

urlpatterns = [
    # API endpoints
    path("api/register/", register_user),
    path("api/login/", login_user),
    path("api/search/", views.search_api, name="search_api"),
    path("api/history/", views.history_api, name="history_api"),
    path("api/logout/", views.logout_user, name="logout_user"),
    path("api/feedback/", views.feedback_api, name="feedback_api"),
    path("api/bookmark/", views.bookmark_api, name="bookmark_api"),
    path("api/bookmarks/", views.get_bookmarks_api, name="get_bookmarks_api"),
    
    # NEW APIs
    path("api/profile/", views.profile_api, name="profile_api"),
    path("api/profile/update/", views.profile_update_api, name="profile_update_api"),
    path("api/search/history/", views.search_history_api, name="search_history_api"),
    path("api/feedback/all/", views.feedback_all_api, name="feedback_all_api"),
    path("api/feedback/submit/", views.feedback_submit_api, name="feedback_submit_api"),
    path("api/recommendations/", views.recommendations_api, name="recommendations_api"),

    # Pages
    path("login/", login_page, name="login"),
    path("signup/", signup_page, name="signup"),
    path("home/", home_page, name="home"),
    path("bookmarks/", views.bookmarks_page, name="bookmarks_page"),
    path("feedback/", views.feedback_page, name="feedback_page"),
    path("profile/", views.profile_page, name="profile_page"),
]