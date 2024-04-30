
from django.urls import include, path


from stock import views


from .views import getMinuterInfo_index,getTickInfo_index,getNewMinuterInfo_index,getDayDateScore_index,getAuctionTickInfo_index


urlpatterns = [
    path('stock/getMinuterInfo', getMinuterInfo_index, name='getMinuterInfo'),
    path('stock/getNewMinuterInfo', getNewMinuterInfo_index, name='getNewMinuterInfo'),
    path('stock/getTickInfo', getTickInfo_index, name='getTickInfo'),
    path('stock/getAuctionTickInfo', getAuctionTickInfo_index, name='getAuctionTickInfo'),

    path('strategy/getDayDateScore', getDayDateScore_index, name='getDayDateScore'),

]
