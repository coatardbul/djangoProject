"""djangoProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path
from pytdx.hq import TdxHq_API
from pytdx.params import TDXParams
import json
import time
import random
from django.core.cache import cache

from django.shortcuts import HttpResponse

from djangoProject import views


def test(request):


    api = TdxHq_API()
    with api.connect('119.147.212.81', 7709):
        data = api.get_history_transaction_data(TDXParams.MARKET_SZ, '000625', 4000, 2000, 20221130)
    print(type(data))
    print(len(data))

    for i in range(len(data)):
        print(data[i])
    return HttpResponse("22222");


urlpatterns = [
    # path('admin/', admin.site.urls),
    path('test/', test),
    path('test2/', views.refreshTIckInfo),
    path('tick/refreshTIckInfo/', views.learn),

]
