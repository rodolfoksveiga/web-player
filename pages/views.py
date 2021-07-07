import requests
import json
import pandas as pd
import plotly.express as plyx
import plotly.graph_objs as plygo
import plotly.offline as plyo

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

from piwikapi.analytics import PiwikAnalytics

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm

from secret_keys import MATOMO_TOKEN


def get_data(method, date):
    pa = PiwikAnalytics()
    pa.set_api_url('https://collect.mayflower.live/index.php')
    pa.set_id_site(2)
    pa.set_parameter('token_auth', MATOMO_TOKEN)
    pa.set_format('json')
    pa.set_method(method)
    pa.set_period('day')
    pa.set_date(date)
    return json.loads(pa.send_request())


def get_live_widget():
    pa = PiwikAnalytics()
    pa.set_api_url('https://collect.mayflower.live/index.php')
    pa.set_id_site(2)
    pa.set_parameter('token_auth', MATOMO_TOKEN)
    # pa.set_format('json')
    pa.set_period('day')
    pa.set_date('today')
    pa.set_parameter('module', 'Widgetize')
    pa.set_parameter('action', 'iframe')
    pa.set_parameter('widget', 1)
    pa.set_parameter('moduleToWidgetize', 'Live')
    pa.set_parameter('actionToWidgetize', 'getSimpleLastVisitCount')
    return pa.send_request()


def process_data(data):
    columns = ['userId', 'datetime', 'action', 'eventName',
               'operatingSystemName', 'browserName', 'city']
    df = pd.DataFrame(columns=columns)
    for visit in data:
        for action in visit['actionDetails']:
            if 'subtitle' in action:
                if action['subtitle'] == "Category: \"videoroom', Action: \"vr:enter\"":
                    df = df.append(pd.DataFrame([[
                        visit['userId'],
                        action['timestamp'],
                        'enter',
                        action['eventName'],
                        visit['operatingSystemName'],
                        visit['browserName'],
                        visit['city']
                    ]], columns=columns))
                if action['subtitle'] == "Category: \"videoroom', Action: \"vr:leave\"":
                    df = df.append(pd.DataFrame([[
                        visit['userId'],
                        action['timestamp'],
                        'leave',
                        action['eventName'],
                        visit['operatingSystemName'],
                        visit['browserName'],
                        visit['city']
                    ]], columns=columns))
    df['datetime'] = pd.to_datetime(df['datetime'], unit='s')
    df = df.sort_values('datetime')
    count = 0
    usersSum = []
    for action in df['action']:
        if action == 'enter':
            count += 1
            usersSum.append(count)
        else:
            count -= 1
            usersSum.append(count)
    df['usersSum'] = usersSum
    return df


def home_view(request):
    return render(request, 'home.html')


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


@ login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('login')


@ user_passes_test(lambda user: user.is_superuser)
def matomo_view(request, *args, **kwargs):
    if request.method == 'POST':
        method = request.POST.get('method')
        date = request.POST.get('date')
        color = request.POST.get('color')
        date = str(date)
        data = get_data('Live.getLastVisitsDetails', date)
        df = process_data(data)
        # trace = plygo.Scatter(x=df.datetime, y=df.usersSum,
        #                       mode='lines+markers', marker=dict(color='rgba(0, 0, 0, 0.8)'))
        # layout = plygo.Layout(xaxis=dict(title='Hour', title_font_size=20),
        #                       yaxis=dict(title='Number Visitors', title_font_size=20))
        # graph = plygo.Figure(data=trace, layout=layout)
        if color != 'noColor':
            graph = plyx.line(df, x="datetime", y="usersSum", color=color)
        else:
            graph = plyx.line(df, x="datetime", y="usersSum")
        graph_div = plyo.plot(graph, auto_open=False, output_type='div')
        context = {
            'data': data,
            'graph': graph_div,
            'image': 'https://collect.mayflower.live/index.php?module=API&method=ImageGraph.get&apiModule=DevicesDetection&apiAction=getBrowsers&graphType=evolution&period=day&date=previous30&width=500&height=250&token_auth=' + MATOMO_TOKEN + '&idSite=2'
        }
        return render(request, 'matomo/graph.html', context)
    return render(request, 'matomo/form.html')


def live_widget_view():
    return ''
