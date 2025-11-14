
from collections import defaultdict
from datetime import datetime, timedelta

import requests
from pytdx.hq import TdxHq_API

from djangoProject.service.stock_tick import get_sz_sz_type
from djangoProject.utils.ElasticUtil import ElasticsearchTool
from djangoProject.utils.busi_convert import convert_buy_sell_flag
from djangoProject.utils.number_string_format import str_to_num



#将tick数据转换成分钟数据，可以是5分钟，15分钟，30分钟，60分钟
# {
#     "id": "2022-01-21_001234",
#     "code": "001234",
#     "dateStr": "2022-01-21",
#     "name": "泰慕士",
#     "openPrice": 50.03,
#     "currIncreaseRate": -10.22,
#     "closePrice": 40.75,
#     "minPrice": 40.75,
#     "maxPrice": 50.03,
#     "lastClosePrice": 45.39,
#     "turnOverRate": 79.85,
#     "quantityRelativeRatio": null,
#     "volume": 212922,
#     "tradeAmount": 1014265600,
#     "maxSubRate": 20.45
# }

def calculate_minuter_kline(tickArr, minute):
    #请求river数据
    url = "http://111.229.40.64:9002/river/timeInterval/getTimeList"

    # 要发送的数据对象
    data = {
        "intervalType": minute,  # 5分钟，15分钟，30分钟，60分钟
        # 更多的键值对
    }
    # tickArr=his_tick_list('2024-03-27', '001234')
    # tickArr =his_tick_list('2024-03-27', '001234')
    list=[]
    # 发起POST请求
    response = requests.post(url, json=data)
    if response.status_code == 200:
        timeIntervalArr=response.json().get("data", [])
        for index, item in enumerate(timeIntervalArr[1:], start=1):
            print(f"Index: {index}, Item: {item}")
            # 过滤出09:30到09:35之间的数据
            filtered_data = [item for item in tickArr if timeIntervalArr[index-1] <= item['time'] <= timeIntervalArr[index]]
            # 计算a*b的总和
            tradeAmount = sum(item["price"] * item["vol"]*100 for item in filtered_data)

            # 计算b的总和
            vol = sum(item["vol"] for item in filtered_data)

            # 找出a的最大值和最小值
            maxPrice = max(item["price"] for item in filtered_data)
            minPrice = min(item["price"] for item in filtered_data)
            tickInfo={
                # "id": "2022-01-21_001234",
                # "code": "001234",
                "dateStr":  timeIntervalArr[index],
                # "name": "泰慕士",
                "openPrice": filtered_data[0]["price"],
                # "currIncreaseRate": -10.22,
                "closePrice": filtered_data[len(filtered_data)-1]["price"],
                "minPrice":minPrice,
                "maxPrice": maxPrice,
                # "lastClosePrice": 45.39,
                # "turnOverRate": 79.85,
                # "quantityRelativeRatio": null,
                "volume": vol,
                "tradeAmount": tradeAmount,
                # "maxSubRate": 20.45
            }
            list.append(tickInfo)
    return list;


def calculate_cumulative_and_current_vol_avg_price(data):
    grouped_data = defaultdict(lambda: {
        'vol_sum': 0,
        'prices': [],
        'vol_price_sum': 0,
        'tick_count': 0,  # 每分钟 tick 数
        'tick_arr': []    # 存放该分钟的所有 tick
    })
    cumulative_data = {}
    vol_total_sum = 0  # Total volume up to the current minute
    pm_vol_total_sum = 0.01
    pm2_vol_total_sum = 0.01

    vol_price_total_sum = 0
    pm_vol_price_total_sum = 0
    pm2_vol_price_total_sum = 0

    list = []
    result = []
    for entry in data:
        minute_key = entry['time'][:5]  # HH:MM format
        second = int(entry['time'][6:8])  # Extracting seconds
        vol = entry['vol']
        price = entry['price']

        # Update sums for the current minute
        grouped_data[minute_key]['vol_sum'] += vol
        grouped_data[minute_key]['prices'].append((second, price))
        grouped_data[minute_key]['vol_price_sum'] += vol * price
        grouped_data[minute_key]['tick_count'] += 1   # 每个 tick 加 1
        grouped_data[minute_key]['tick_arr'].append(entry)  # 直接保存原始 tick 数据

    # 定义两个时间段
    morning_start = '09:30'
    morning_end = '11:30'
    afternoon_start = '13:01'
    afternoon_end = '15:00'

    # 生成两个时间段的时间列表
    morning_times = generate_time_range(morning_start, morning_end)
    afternoon_times = generate_time_range(afternoon_start, afternoon_end)
    all_times = ['09:25'] + morning_times + afternoon_times

    for minute, info in sorted(grouped_data.items()):
        vol_total_sum += info['vol_sum']
        vol_price_total_sum += info['vol_price_sum']
        if minute >= '13:00':
            pm_vol_total_sum += info['vol_sum']
            pm_vol_price_total_sum += info['vol_price_sum']
        if minute >= '14:00':
            pm2_vol_total_sum += info['vol_sum']
            pm2_vol_price_total_sum += info['vol_price_sum']

        cumulative_avg_price = vol_price_total_sum / vol_total_sum if vol_total_sum else 0
        pm_cumulative_avg_price = pm_vol_price_total_sum / pm_vol_total_sum if pm_vol_total_sum else 0
        pm2_cumulative_avg_price = pm2_vol_price_total_sum / pm2_vol_total_sum if pm_vol_total_sum else 0

        max_second_price = max(info['prices'], key=lambda x: x[0])[1]
        max_price = max(info['prices'], key=lambda x: x[1])[1]
        min_price = min(info['prices'], key=lambda x: x[1])[1]
        first_price = info['prices'][0][1]

        cumulative_data = {
            'minuter': minute,
            'avg_price': round(cumulative_avg_price, 2),
            'pm_avg_price': round(pm_cumulative_avg_price, 2),
            'pm2_avg_price': round(pm2_cumulative_avg_price, 2),
            'vol': info['vol_sum'],
            'price': max_second_price,
            'begin_price': first_price,
            'max_price': max_price,
            'min_price': min_price,
            'vol_price_sum': round(info['vol_price_sum'], 2),
            'trade_amount': round(info['vol_price_sum'] * 100, 0),
            'tickCount': info['tick_count'],    # 每分钟 tick 数
            'tickArr': info['tick_arr']         # 一分钟的 tick 数据数组
        }
        list.append(cumulative_data)

    lastInfo = list[0]
    for minute in all_times:
        filtered_grouped_data = [entry for entry in list if entry['minuter'] == minute]

        if len(filtered_grouped_data) > 0:
            result.append(filtered_grouped_data[0])
            lastInfo = filtered_grouped_data[0]
        else:
            cumulative_data = {
                'minuter': minute,
                'avg_price': lastInfo['avg_price'],
                'pm_avg_price': lastInfo['pm_avg_price'],
                'pm2_avg_price': lastInfo['pm2_avg_price'],
                'vol': 0,
                'price': lastInfo['price'],
                'tickCount': 0,   # 没有 tick 的分钟补 0
                'tickArr': []     # 没有 tick 的分钟补空数组
            }
            result.append(cumulative_data)
    return result



def generate_time_range(start_time_str, end_time_str, interval_minutes=1):
    start_time = datetime.strptime(start_time_str, '%H:%M')
    end_time = datetime.strptime(end_time_str, '%H:%M')
    time_range = []

    while start_time <= end_time:
        time_range.append(start_time.strftime('%H:%M'))
        start_time += timedelta(minutes=interval_minutes)

    return time_range

def his_auction_tick_list(dateStr, code):
    es = ElasticsearchTool()
    auctionArr = es.search_documents(index_name="his_tick_auction", query={
        "bool": {
            "must": [
                {"term": {"code": "001234"}},
                {"term": {"dateStr": "2024-04-29"}}
            ]
        }
    })

def his_tick_list(dateStr, code):
    api = TdxHq_API()
    list = []
    with api.connect('110.41.147.114', 7709):
        dateFormatStr = dateStr.replace("-", "");

        # 转为日期对象
        target_date = datetime.strptime(dateStr, "%Y-%m-%d").date()
        # 获取今天日期
        today = datetime.today().date()
        # 判断是否为当天
        if target_date == today:
            # 数据总共4800
            data1 = api.get_transaction_data(get_sz_sz_type(code), code, 0, 2000)
            data2 = api.get_transaction_data(get_sz_sz_type(code), code, 2000, 2000)
            data3 = api.get_transaction_data(get_sz_sz_type(code), code, 4000, 2000)
            # ⚠️ 自动过滤 None，然后拼接
            data = []
            for part in (data3, data2, data1):
                if part:
                    data.extend(part)
        else:
            # 数据总共4800
            data1 = api.get_history_transaction_data(get_sz_sz_type(code), code, 0, 2000, int(dateFormatStr))
            data2 = api.get_history_transaction_data(get_sz_sz_type(code), code, 2000, 2000, int(dateFormatStr))
            data3 = api.get_history_transaction_data(get_sz_sz_type(code), code, 4000, 2000, int(dateFormatStr))
            # ⚠️ 自动过滤 None，然后拼接
            data = []
            for part in (data3, data2, data1):
                if part:
                    data.extend(part)



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
                'price':item['price']/10 if code[0] == '1' else item['price'] ,
                'vol': item['vol'],
                'buySellFlag': convert_buy_sell_flag(item['buyorsell'])
            }
            list.append(stockBaseInfo)
    return list

def his_minuter_list(dateStr, code):
    list =his_tick_list(dateStr, code)
    return calculate_cumulative_and_current_vol_avg_price(list)

