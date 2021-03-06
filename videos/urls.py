"""webplayer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path

from .views import (
    videos_view,
    play_video_view,
    create_video_view,
    update_video_view,
    delete_video_view
)

urlpatterns = [
    path('', videos_view, name='videos'),
    path('create/', create_video_view, name='create-video'),
    path('<int:id>/', play_video_view, name='play-video'),
    path('<int:id>/update/', update_video_view, name='update-video'),
    path('<int:id>/delete/', delete_video_view, name='delete-video'),
]