import json
from collections import defaultdict

from django.http import HttpResponse
from pytdx.hq import TdxHq_API
from rest_framework.decorators import api_view

from djangoProject.service.stock_tick import get_sz_sz_type
from djangoProject.utils.busi_convert import convert_buy_sell_flag
from djangoProject.utils.number_string_format import str_to_num


@api_view(['POST'])
def getMinuterInfo(request):
    postBody = request.body
    json_result = json.loads(postBody)
    dateStr = json_result.get("dateStr");
    code = json_result.get("code");
    api = TdxHq_API()
    list = []
    with api.connect('119.147.212.81', 7709):
        dateFormatStr = dateStr.replace("-", "");
        # 数据总共4800
        data = api.get_history_minute_time_data(get_sz_sz_type(code), code, int(dateFormatStr));
        return HttpResponse(json.dumps(data))
    return HttpResponse(json.dumps(list))


@api_view(['POST'])
def getNewMinuterInfo(request):
    postBody = request.body
    json_result = json.loads(postBody)
    dateStr = json_result.get("dateStr");
    code = json_result.get("code");
    api = TdxHq_API()
    list = []
    with api.connect('119.147.212.81', 7709):
        dateFormatStr = dateStr.replace("-", "");
        # 数据总共4800
        data1 = api.get_history_transaction_data(get_sz_sz_type(code), code, 0, 2000, int(dateFormatStr))
        data2 = api.get_history_transaction_data(get_sz_sz_type(code), code, 2000, 2000, int(dateFormatStr))
        data3 = api.get_history_transaction_data(get_sz_sz_type(code), code, 4000, 2000, int(dateFormatStr))
        data = data3 + data2 + data1

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
    return HttpResponse(json.dumps(calculate_cumulative_and_current_vol_avg_price(list)))

def calculate_cumulative_and_current_vol_avg_price(data):
    grouped_data = defaultdict(lambda: {'vol_sum': 0, 'prices': [], 'vol_price_sum': 0})
    cumulative_data = {}
    vol_total_sum = 0  # Total volume up to the current minute
    vol_price_total_sum = 0  # Total volume*price up to the current minute

    for entry in data:
        minute_key = entry['time'][:5]  # HH:MM format
        second = int(entry['time'][6:8])  # Extracting seconds
        vol = entry['vol']
        price = entry['price']
        # Update sums for the current minute
        grouped_data[minute_key]['vol_sum'] += vol
        grouped_data[minute_key]['prices'].append((second, price))
        grouped_data[minute_key]['vol_price_sum'] += vol * price

    for minute, info in sorted(grouped_data.items()):
        vol_total_sum += info['vol_sum']
        vol_price_total_sum += info['vol_price_sum']
        cumulative_avg_price = vol_price_total_sum / vol_total_sum if vol_total_sum else 0
        max_second_price = max(info['prices'], key=lambda x: x[0])[1]
        # Store cumulative and current minute data
        cumulative_data[minute] = {
            'avg_price': round(cumulative_avg_price, 2),
            'vol': info['vol_sum'],
            'price': max_second_price,
        }
    return cumulative_data


@api_view(['POST'])
def getTickInfo(request):
    postBody = request.body
    json_result = json.loads(postBody)
    dateStr = json_result.get("dateStr");
    code = json_result.get("code");
    api = TdxHq_API()
    list = []
    with api.connect('119.147.212.81', 7709):
        dateFormatStr = dateStr.replace("-", "");
        # 数据总共4800
        data1 = api.get_history_transaction_data(get_sz_sz_type(code), code, 0, 2000, int(dateFormatStr))
        data2 = api.get_history_transaction_data(get_sz_sz_type(code), code, 2000, 2000, int(dateFormatStr))
        data3 = api.get_history_transaction_data(get_sz_sz_type(code), code, 4000, 2000, int(dateFormatStr))
        data = data3 + data2 + data1

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
    return HttpResponse(json.dumps(list, ensure_ascii=False))