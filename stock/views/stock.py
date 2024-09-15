import json
from collections import defaultdict

from django.http import HttpResponse
from pytdx.hq import TdxHq_API
from rest_framework.decorators import api_view

from djangoProject.service.stock_tick import get_sz_sz_type
from djangoProject.utils.ElasticUtil import ElasticsearchTool
from djangoProject.utils.busi_convert import convert_buy_sell_flag
from djangoProject.utils.klineUtil import calculate_cumulative_and_current_vol_avg_price, his_tick_list
from djangoProject.utils.number_string_format import str_to_num
from stock.models import StockSimulateTradeDetail, StockBase


@api_view(['POST'])
def getMinuterInfo(request):
    postBody = request.body
    json_result = json.loads(postBody)
    dateStr = json_result.get("dateStr");
    code = json_result.get("code");
    api = TdxHq_API()
    list = []
    with api.connect('110.41.147.114', 7709):
        dateFormatStr = dateStr.replace("-", "");
        # 数据总共4800
        data = api.get_history_minute_time_data(get_sz_sz_type(code), code, int(dateFormatStr));
        return HttpResponse(json.dumps(data))
    return HttpResponse(json.dumps(list))

# 包含竞价数据
@api_view(['POST'])
def getNewMinuterInfo(request):
    postBody = request.body
    json_result = json.loads(postBody)
    dateStr = json_result.get("dateStr");
    code = json_result.get("code");
    list = his_tick_list(dateStr, code)
    return HttpResponse(json.dumps(calculate_cumulative_and_current_vol_avg_price(list)))



@api_view(['POST'])
def getTickInfo(request):
    postBody = request.body
    json_result = json.loads(postBody)
    dateStr = json_result.get("dateStr");
    code = json_result.get("code");
    list = his_tick_list(dateStr, code)
    return HttpResponse(json.dumps(list, ensure_ascii=False))

@api_view(['POST'])
def getAuctionTickInfo(request):
    postBody = request.body
    json_result = json.loads(postBody)
    dateStr = json_result.get("dateStr");
    code = json_result.get("code");
    es = ElasticsearchTool()
    esInfoArr = es.search_documents(index_name="his_tick_auction", query={
        "bool": {
            "must": [
                {"term": {"code": code}},
                {"term": {"dateStr": dateStr}}
            ]
        }
    })
    list = []
    if len(esInfoArr)>0:
        list =json.loads(esInfoArr[0]['jsonStr'])
    return HttpResponse(json.dumps(list, ensure_ascii=False))