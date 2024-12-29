"""
URL configuration for rss_client project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    # Front-End urls
    path('', include('accounts.urls'), name='home'),
    path('accounts/', include('accounts.urls'), name='accounts'),
    # API urls
    path('api/v1/accounts/', include('accounts.urls'), name='accounts'),
    path('api/v1/sources/', include('sources.urls'), name='sources'),
    path('api/v1/groups/', include('groups.urls'), name='groups'),
    path('api/v1/feeds/', include('feeds.urls'), name='feeds'),
    path('api/v1/chat/', include('chat.urls'), name='chat'),
    path('api/v1/news/', include('rss_client.urls'), name='news'),
    path('admin/', admin.site.urls),
    # API documentation
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
