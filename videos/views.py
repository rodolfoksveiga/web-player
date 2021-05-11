from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
import requests
import vimeo

from .models import Video
from .forms import VideoForm


def videos_view(request, *args, **kwargs):
    queryset = Video.objects.all()
    context = {
        'obj_list': queryset
    }
    return render(request, 'video/videos.html', context)


def play_video_view(request, id):
    client = vimeo.VimeoClient(
        key='',
        secret=''
    )
    vimeo_authorization_url = client.auth_url(
        scope=['public', 'private'],
        redirect='http://localhost:8000/videos/',
        state='state'
    )
    try:
        code = request.GET.get('code')
        token, user, scop = client.exchange_code(
            code,
            'http://localhost:8000/videos/'
        )
        print(token)
    except:
        print('BAD!')

    # get video's iframe
    # response = client.get('/videos/538327228')
    # iframe = response.json().get('embed').get('html')

    # update video's information
    # client.patch(
    #     '/videos/538327228',
    #     data={
    #         'name': 'NEW Test Video 1',
    #         'description': 'NEW This is a test.'
    #     }
    # )

    obj = get_object_or_404(Video, id=id)
    context = {
        'obj': obj,
        'auth': vimeo_authorization_url,
    }
    return render(request, 'video/play_video.html', context)


@login_required(login_url='login')
def create_video_view(request, *args, **kwargs):
    form = VideoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('../')
    context = {
        'form': form
    }
    return render(request, 'video/create_video.html', context)


@login_required(login_url='login')
def update_video_view(request, id, *args, **kwargs):
    obj = get_object_or_404(Video, id=id)
    values = {
        'title': obj.title,
        'url': obj.url
    }
    form = VideoForm(request.POST or None, initial=values, instance=obj)
    if form.is_valid():
        form.save()
        return redirect('../')
    context = {
        'form': form
    }
    return render(request, 'video/update_video.html', context)


@login_required(login_url='login')
def delete_video_view(request, id, *args, **kwargs):
    obj = get_object_or_404(Video, id=id)
    if request.method == 'POST':
        obj.delete()
        return redirect('../../')
    context = {
        'obj': obj
    }
    return render(request, 'video/delete_video.html', context)
