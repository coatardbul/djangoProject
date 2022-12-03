import json

from django.http import HttpResponse
from django_redis import get_redis_connection
from pytdx.hq import TdxHq_API
from rest_framework.decorators import api_view

from djangoProject.service.stock_tick import get_sz_sz_type
from djangoProject.utils.busi_convert import convert_buy_sell_flag
from djangoProject.utils.number_string_format import str_to_num
from djangoProject.utils.redis_key import get_his_tick


@api_view(['POST'])
def refreshTIckInfo(request):
    postBody = request.body
    json_result = json.loads(postBody)
    dateStr = json_result.get("dateStr");
    codeArr = json_result.get("codeArr");
    conn = get_redis_connection()
    api = TdxHq_API()
    with api.connect('119.147.212.81', 7709):
        for code in codeArr:
            dateFormatStr = dateStr.replace("-", "");
            # 数据总共4800
            data1 = api.get_history_transaction_data(get_sz_sz_type(code), code, 0, 2000, int(dateFormatStr))
            data2 = api.get_history_transaction_data(get_sz_sz_type(code), code, 2000, 2000, int(dateFormatStr))
            data3 = api.get_history_transaction_data(get_sz_sz_type(code), code, 4000, 2000, int(dateFormatStr))
            data = data3 + data2 + data1

            list = []
            currtime = ""
            currNum = 0;
            for item in data:
                if currtime.find(item['time']) > -1:
                    currNum += 3
                else:
                    currtime = item['time']
                    currNum = 1
                stockBaseInfo = {
                    'time': item['time'] + ":" + str_to_num(currNum),
                    'price': item['price'],
                    'vol': item['vol'],
                    'buySellFlag': convert_buy_sell_flag(item['buyorsell'])
                }
                list.append(stockBaseInfo)
            listJsonStr = json.dumps(list, ensure_ascii=False)
            conn.set(get_his_tick(dateStr, code), listJsonStr, ex=2 * 24 * 60 * 60)
    return HttpResponse("")


@api_view(['POST'])
def learn(request):
    return HttpResponse("1111")
