from django.contrib import admin
from django.urls import include, path

from pages.views import (
    home_view,
    about_view,
    register_view,
    login_view,
    logout_view,
    matomo_view
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('about/', about_view, name='about'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('videos/', include('videos.urls')),
    path('matomo/', matomo_view, name='matomo')
]
