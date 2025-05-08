
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new", views.new_post, name="new_post"),
    path("following", views.following, name="following"),
    # Acts as both normal route and API route
    path("profile/<int:id>", views.profile, name="profile"),

    # API route
    path("post_actions/<int:id>", views.post_actions, name="post_actions")
]
