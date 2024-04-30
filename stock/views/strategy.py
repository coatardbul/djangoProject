import json
import traceback
from datetime import datetime, date, timedelta
import akshare as ak

from djangoProject.utils.StockUtil import is_up_limit
from djangoProject.utils.klineUtil import calculate_cumulative_and_current_vol_avg_price, his_tick_list

import numpy as np
import pandas as pd
from django.http import HttpResponse
from rest_framework.decorators import api_view

from djangoProject.utils import StockUtil
from djangoProject.utils.sinaKlineUtil import get_stock_minuter_list
from stock.models import StockBase


# 获取日的数据及得分
@api_view(['POST'])
def getDayDateScore(request):
    postBody = request.body
    json_result = json.loads(postBody)
    dateStr = json_result.get("dateStr");
    code = json_result.get("code");
    strategySignArr = json_result.get("strategySignArr");
    scoreSign = json_result.get("scoreSign");
    list = []
    try:
        df_qfq = StockUtil.getStockPandas(code, two_years_earlier(dateStr.replace('-', '')), dateStr.replace('-', ''));
        sdfds=1
    except Exception as e:
        traceback.print_exc()
        return HttpResponse(json.dumps(list, default=default_converter))
    else:
        print("读取成功")
    target_idx = df_qfq.index.get_loc(dateStr)  # 获取目标日期的位置
    for strategySign in strategySignArr:
        if (strategySign == 'cyb_big_increase_high_open'):
            if df_qfq.iloc[target_idx-1].increaseRate>10 and df_qfq.iloc[target_idx-1].increaseRate<19 and df_qfq.iloc[target_idx-1].tradeAmount>80000000:
                data1 = get_data(df_qfq, target_idx, scoreSign, code,"创业板大涨幅高开")
                list.append(data1)
        if (strategySign == 'cyb_small_increase_high_open'):
            if (df_qfq.iloc[target_idx-1].increaseRate>5 and df_qfq.iloc[target_idx-1].increaseRate<10 and df_qfq.iloc[target_idx-1].tradeAmount>80000000
                    and df_qfq.iloc[target_idx-2].increaseRate<7 and df_qfq.iloc[target_idx-3].increaseRate<7 and  df_qfq.iloc[target_idx-1].open/ df_qfq.iloc[target_idx-2].close< 1.02):
                data1 = get_data(df_qfq, target_idx, scoreSign, code,"创业板小涨幅高开")
                list.append(data1)
        #小涨幅
        if (strategySign == 'cyb_small_increase'):
            if (abs(df_qfq.iloc[target_idx-1].savgol_MA5_slope)<0.2 and abs(df_qfq.iloc[target_idx-2].savgol_MA5_slope)<0.2 and abs(df_qfq.iloc[target_idx-3].savgol_MA5_slope)<0.2
            and abs(df_qfq.iloc[target_idx-1].savgol_MA10_slope)<0.1 and abs(df_qfq.iloc[target_idx-2].savgol_MA10_slope)<0.1 and abs(df_qfq.iloc[target_idx-3].savgol_MA10_slope)<0.1):
                data1 = get_data(df_qfq, target_idx, scoreSign, code,"创业板小涨幅")
                list.append(data1)
        #长抢不倒
        if (strategySign == 'cyb_cqbd'):
            # # 五日线的斜率一定要往下
            # and data.savgol_MA5_slope[-3] < 0.1
            # and data.savgol_MA5_slope[-4] < 0.1
            #
            # # 涨幅当日实体的长度一定要大于上下影线的长度
            # and data.close[-2] - data.open[-2] > (
            #         data.high[-2] - data.close[-2] + data.open[-2] - data.low[-2]) * 1.3
            # # 后一低开不能太多
            # and data.open[-1] / data.close[-2] > 0.98
            #
            # # 后二不要有长下影线
            # and (data.open[0] - data.low[0]) / (data.high[0] - data.low[0]) < 0.4
            if(df_qfq.iloc[target_idx-3].savgol_MA5_slope<0.1 and df_qfq.iloc[target_idx-4].savgol_MA5_slope<0.1
            and df_qfq.iloc[target_idx-2].close-df_qfq.iloc[target_idx-2].open>
                    (df_qfq.iloc[target_idx-2].high-df_qfq.iloc[target_idx-2].close+df_qfq.iloc[target_idx-2].open-df_qfq.iloc[target_idx-2].low)*1.3
            and df_qfq.iloc[target_idx-1].open/df_qfq.iloc[target_idx-2].close>0.98
            and (df_qfq.iloc[target_idx].open-df_qfq.iloc[target_idx].low)/(df_qfq.iloc[target_idx].high-df_qfq.iloc[target_idx].low)<0.4):
                data1 = get_data(df_qfq, target_idx, scoreSign, code,"创业板长抢不倒")
                list.append(data1)
        if (strategySign == 'special'):
            data1 = get_data(df_qfq, target_idx, scoreSign, code,"")
            list.append(data1)
    return HttpResponse(json.dumps(list, default=default_converter))


def default_converter(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, date):
        return obj.strftime("%Y-%m-%d")
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def get_data(df_qfq, target_idx, scoreSign, code,strategyName):
    begin_index = 0
    if scoreSign == 'today' or scoreSign is None:
        begin_index = 0
    if scoreSign == 'last':
        begin_index = 1
    score_period = 40
    if target_idx < 40:
        score_period = target_idx
    score_sum = sum([df_qfq.iloc[target_idx - i].skill_score for i in range(begin_index, begin_index + score_period)])
    last_begin_15_score_sum=0
    if score_period==40:
        last_begin_15_score_sum = sum(
            [df_qfq.iloc[target_idx - i].skill_score for i in range(24, 40)])
    last_middle_15_score_sum = 0
    if score_period > 25:
        last_middle_15_score_sum = sum(
            [df_qfq.iloc[target_idx - i].skill_score for i in range(15, 25)])
    last_end_15_score_sum = 0
    if score_period > 15:
        last_end_15_score_sum = sum(
            [df_qfq.iloc[target_idx - i].skill_score for i in range(0, 14)])
    lose_sum = sum([df_qfq.iloc[target_idx - i].lose_score for i in range(begin_index, begin_index + score_period)])
    last_begin_15_lose_sum = 0
    if score_period == 40:
        last_begin_15_lose_sum = sum(
            [df_qfq.iloc[target_idx - i].lose_score for i in range(24, 40)])
    last_middle_15_lose_sum = 0
    if score_period > 25:
        last_middle_15_lose_sum = sum(
            [df_qfq.iloc[target_idx - i].lose_score for i in range(15, 25)])
    last_end_15_lose_sum = 0
    if score_period > 15:
        last_end_15_lose_sum = sum(
            [df_qfq.iloc[target_idx - i].lose_score for i in range(0, 14)])
    upLimitcount = 0
    for i in  range(begin_index, begin_index + score_period):
        if is_up_limit(code,df_qfq.iloc[target_idx - i-1].close,df_qfq.iloc[target_idx - i].close):
            upLimitcount += 1
    greate5count = 0
    for i in range(begin_index, begin_index + score_period):
        if df_qfq.iloc[target_idx - i].increaseRate>5 and df_qfq.iloc[target_idx - i].increaseRate<10 and not is_up_limit(code,df_qfq.iloc[target_idx - i-1].close,df_qfq.iloc[target_idx - i].close):
            greate5count += 1
    greate10count = 0
    for i in range(begin_index, begin_index + score_period):
        if df_qfq.iloc[target_idx - i].increaseRate > 10 and df_qfq.iloc[target_idx - i].increaseRate < 15 and not is_up_limit(code,df_qfq.iloc[target_idx - i-1].close,df_qfq.iloc[target_idx - i].close):
            greate10count += 1
    greate15count = 0
    for i in range(begin_index, begin_index + score_period):
        if df_qfq.iloc[target_idx - i].increaseRate > 15 and df_qfq.iloc[target_idx - i].increaseRate < 20 and not is_up_limit(code,df_qfq.iloc[target_idx - i-1].close,df_qfq.iloc[target_idx - i].close):
            greate15count += 1
    less5count = 0
    less10count = 0
    less15count = 0
    for i in range(begin_index, begin_index + score_period):
        increase_rate = df_qfq.iloc[target_idx - i].increaseRate
        if -10 < increase_rate < -5:
            less5count += 1
        elif -15 < increase_rate < -10:
            less10count += 1
        elif -20 < increase_rate < -15:
            less15count += 1

    maxPrice=0
    minPrice=0
    for i in range(begin_index, begin_index + score_period):
        currClose = df_qfq.iloc[target_idx - i].close
        if currClose > maxPrice:
            maxPrice = currClose
        if minPrice==0:
            minPrice = currClose
        if currClose < minPrice:
            minPrice = currClose
    lastDateStr=df_qfq.iloc[target_idx-1].date.strftime("%Y-%m-%d")
    dateStr=df_qfq.iloc[target_idx].date.strftime("%Y-%m-%d")
    currDateStr=datetime.now().strftime("%Y-%m-%d")
    callAuctionAmount=0
    if(dateStr==currDateStr):
        qwewq=1
        #todo 新浪竟然封ip，再想想办法
        # minute_kline_data = get_stock_minuter_list(code)
        # if len(minute_kline_data)>0:
        #     callAuctionAmount=float(minute_kline_data[0]['price']) *float( minute_kline_data[0]['vol'])
    else:
        list = his_tick_list(dateStr, code)
        minute_kline_data=calculate_cumulative_and_current_vol_avg_price(list)
        callAuctionAmount = minute_kline_data[0]['price'] * minute_kline_data[0]['vol']*100
    stockBase =StockBase.objects.get(pk=code)
    return {
        'rangeRate': round(
            (df_qfq.iloc[target_idx].close - df_qfq.iloc[target_idx - score_period].close) / df_qfq.iloc[target_idx - score_period].close,
            4),
        'rangeMaxMinRate': round(
            (maxPrice - minPrice) /minPrice ,
            4),
        'currPrice': df_qfq.iloc[target_idx].close,
        'upLimitcount':upLimitcount,
        'greate5count':greate5count,
        'greate10count':greate10count,
        'greate15count':greate15count,
        'less5count':less5count,
        'less10count':less10count,
        'less15count':less15count,
        'upDownRange':str(greate15count)+'-'+str(greate10count)+'-'+str(greate5count)+'--'+str(less5count)+'-'+str(less10count)+'-'+str(less15count),
        'callAuctionPrice': df_qfq.iloc[target_idx].open,
        'callAuctionAmount': callAuctionAmount,
        'callAuctionRate': round(
            (df_qfq.iloc[target_idx].open - df_qfq.iloc[target_idx - 1].close) / df_qfq.iloc[target_idx - 1].close, 4),
        'lastCallAuctionRate': round(
            (df_qfq.iloc[target_idx-1].open - df_qfq.iloc[target_idx - 2].close) / df_qfq.iloc[target_idx - 2].close, 4),
        'currPrice': df_qfq.iloc[target_idx].close,
        'lastLastClosePrice': df_qfq.iloc[target_idx - 2].close,
        'lastClosePrice':df_qfq.iloc[target_idx-1].close,
        'currUpRate': round(
            (df_qfq.iloc[target_idx].close - df_qfq.iloc[target_idx - 1].close) / df_qfq.iloc[target_idx - 1].close, 4),
        'lastUpRate': round(
            (df_qfq.iloc[target_idx-1].close - df_qfq.iloc[target_idx - 2].close) / df_qfq.iloc[target_idx - 2].close, 4),
        'maxPrice': df_qfq.iloc[target_idx].high,
        'maxUpRate': round(
            (df_qfq.iloc[target_idx].high - df_qfq.iloc[target_idx - 1].close) / df_qfq.iloc[target_idx - 1].close, 4),
        'minPrice': df_qfq.iloc[target_idx].low,
        'minUpRate': round(
            (df_qfq.iloc[target_idx].low - df_qfq.iloc[target_idx - 1].close) / df_qfq.iloc[target_idx - 1].close, 4),
        'tradeAmount': df_qfq.iloc[target_idx].tradeAmount,
        'lastTradeAmount': df_qfq.iloc[target_idx-1].tradeAmount,
        'callAuctionTurnOverRate':0 if  stockBase.total_share_capital is None else round(callAuctionAmount/(stockBase.total_share_capital*df_qfq.iloc[target_idx].close)*100 ,4),
        'turnOverRate':df_qfq.iloc[target_idx].turnoverRate,
        'lastTurnOverRate': df_qfq.iloc[target_idx-1].turnoverRate,
        'code': code,
        'name': stockBase.name,
        'marketValue':0 if  stockBase.total_share_capital is None else stockBase.total_share_capital*df_qfq.iloc[target_idx].close ,
        'circulateMarketValue': 0 if stockBase.circulate_share_capital is None else stockBase.circulate_share_capital * df_qfq.iloc[target_idx].close,
        'theme':stockBase.theme,
        'industry':stockBase.industry,
        'strategyName':strategyName,
        'scoreDateStr': df_qfq.iloc[target_idx - begin_index].date,
        'dateStr': df_qfq.iloc[target_idx].date,
        'killScore': np.int64(score_sum),
        'killScoreRange': str(last_begin_15_score_sum) + '-' + str(last_middle_15_score_sum) + '-' + str(last_end_15_score_sum),
        'loseScore': np.int64(lose_sum),
        'loseScoreRange': str(last_begin_15_lose_sum) + '-' + str(last_middle_15_lose_sum) + '-' + str(last_end_15_lose_sum),
    }


def two_years_earlier(date_str):
    # 将输入的字符串转换为 datetime 对象
    given_date = datetime.strptime(date_str, "%Y%m%d")

    # 计算两年前的日期
    new_date = given_date - timedelta(days=700)

    # 将新日期转换回字符串格式并返回
    return new_date.strftime("%Y%m%d")







