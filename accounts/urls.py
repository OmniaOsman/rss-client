from django.urls import path
from . import views

urlpatterns = [
    path("register", views.RegisterView.as_view(), name="register"),
    path("login", views.LoginView.as_view(), name="login"),
    path("uid", views.RetriveUUIDView.as_view(), name="uuid"),
    path("logout", views.LogoutPageView.as_view(), name="logout"),
    
    # Front-End urls
    path("", views.HomePageView.as_view(), name="home"),
    path("signup", views.RegisterPageView.as_view(), name="register"),
    path("signin", views.LoginPageView.as_view(), name="login"),
]
