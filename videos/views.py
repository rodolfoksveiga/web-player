from django.shortcuts import render, get_object_or_404, redirect
import requests

from .models import Video
from .forms import VideoForm

def videos_view(request, *args, **kwargs):
    queryset = Video.objects.all()
    context = {
        'obj_list': queryset
    }
    return render(request, 'video/videos.html', context)

def play_video_view(request, id):
    # requests.get('https://vimeo.com/api/oembed.json?url=' + obj.url)
    obj = get_object_or_404(Video, id=id)
    context = {
        'obj': obj
    }
    return render(request, 'video/play_video.html', context)

def create_video_view(request, *args, **kwargs):
    form = VideoForm(request.POST or None)
    if form.is_valid():
        form.save()
        form = VideoForm() # change here to return to videos views
    context = {
        'form': form
    }
    return render(request, 'video/create_video.html', context)

def update_video_view(request, id, *args, **kwargs):
    obj = get_object_or_404(Video, id=id)
    values = {
        'title': obj.title,
        'url': obj.url
    }
    form = VideoForm(request.POST or None, initial=values, instance=obj)
    if form.is_valid():
        form.save()
        form = VideoForm() # change here to return to videos views
    context = {
        'form': form
    }
    return render(request, 'video/update_video.html', context)

def delete_video_view(request, id, *args, **kwargs):
    obj = get_object_or_404(Video, id=id)
    if request.method == 'POST':
        obj.delete()
        return redirect('../../')
    context = {
        'obj': obj
    }
    return render(request, 'video/delete_video.html', context)

