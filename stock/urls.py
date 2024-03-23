
from django.urls import include, path


from stock import views


from .views import getMinuterInfo_index,getTickInfo_index,getNewMinuterInfo_index,getDayDateScore_index


urlpatterns = [
    path('stock/getMinuterInfo', getMinuterInfo_index, name='getMinuterInfo'),
    path('stock/getNewMinuterInfo', getNewMinuterInfo_index, name='getNewMinuterInfo'),
    path('stock/getTickInfo', getTickInfo_index, name='getTickInfo'),

    path('strategy/getDayDateScore', getDayDateScore_index, name='getDayDateScore'),

]
