import requests
import json
import pandas as pd
import plotly.graph_objs as plygo
import plotly.offline as plyo

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm

from secret_keys import MATOMO_TOKEN


def get_data(date):
    url = 'https://collect.mayflower.live/index.php?module=API&method=VisitTime.getVisitInformationPerLocalTime&idSite=2&date=' + \
        date + '&period=day&format=json&filter_limit=24&token_auth=' + MATOMO_TOKEN
    data = requests.get(url).text
    data = json.loads(data)
    return data


def home_view(request):
    return render(request, 'home.html', {})


def about_view(request):
    return render(request, 'about.html', {})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            return redirect('login')
    form = UserCreationForm()
    context = {
        'form': form
    }
    return render(request, 'registration/register.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    form = AuthenticationForm()
    context = {
        'form': form
    }
    return render(request, 'registration/login.html', context)


@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('login')


@user_passes_test(lambda user: user.is_superuser)
def matomo_view(request, *args, **kwargs):
    if request.method == 'POST':
        date = request.POST.get('date')
        date = str(date)
        data = get_data(date)
        df = pd.json_normalize(data)[['nb_uniq_visitors', 'segment']]
        df.segment = pd.to_numeric(
            df.segment.str.replace(r'visitLocalHour==', ''))
        trace = plygo.Scatter(x=df.segment, y=df.nb_uniq_visitors,
                              mode='lines+markers', marker=dict(color='rgba(0, 0, 0, 0.8)'))
        layout = plygo.Layout(xaxis=dict(title='Hour', title_font_size=20),
                              yaxis=dict(title='Number of Unique Visitors', title_font_size=20))
        graph = plygo.Figure(data=trace, layout=layout)
        graph_div = plyo.plot(graph, auto_open=False, output_type='div')
        context = {
            'data': data,
            'graph': graph_div,
            'image': 'https://collect.mayflower.live/index.php?module=API&method=ImageGraph.get&apiModule=DevicesDetection&apiAction=getBrowsers&graphType=evolution&period=day&date=previous30&width=500&height=250&token_auth=' + MATOMO_TOKEN + '&idSite=2'
        }
        return render(request, 'matomo/graph.html', context)
    return render(request, 'matomo/form.html')
