import json
from datetime import datetime, date

import numpy as np
import pandas as pd
from django.http import HttpResponse
from rest_framework.decorators import api_view

from djangoProject.utils import StockUtil
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
    df_qfq = StockUtil.getStockPandas(code, two_years_earlier(dateStr.replace('-', '')), dateStr.replace('-', ''));
    target_idx = df_qfq.index.get_loc(dateStr)  # 获取目标日期的位置
    list = []
    for strategySign in strategySignArr:
        if (strategySign == 'cyb_big_increase_high_open'):
            data1 = get_data(df_qfq, target_idx, scoreSign, code,"创业板大涨幅高开")
            list.append(data1)
        if (strategySign == 'cyb_small_increase_high_open'):
            data1 = get_data(df_qfq, target_idx, scoreSign, code,"创业板小涨幅高开")
            list.append(data1)
    print(list)
    return HttpResponse(json.dumps(list, default=default_converter))


def default_converter(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, date):
        return obj.strftime("%Y-%m-%d")
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def get_data(df_qfq, target_idx, scoreSign, code,strategyName):
    begin_index = 0
    if scoreSign == 'today':
        begin_index = 0
    if scoreSign == 'last':
        begin_index = 1
    score_period = 40
    if target_idx < 40:
        score_period = target_idx
    score_sum = sum([df_qfq.iloc[target_idx - i].skill_score for i in range(begin_index, begin_index + score_period)])
    lose_sum = sum([df_qfq.iloc[target_idx - i].lose_score for i in range(begin_index, begin_index + score_period)])

    stockBase =StockBase.objects.get(pk=code)
    return {
        'callAuctionPrice': df_qfq.iloc[target_idx].open,
        'callAuctionRate': round(
            (df_qfq.iloc[target_idx].open - df_qfq.iloc[target_idx - 1].close) / df_qfq.iloc[target_idx - 1].close, 4),
        'currPrice': df_qfq.iloc[target_idx].close,
        'currUpRate': round(
            (df_qfq.iloc[target_idx].close - df_qfq.iloc[target_idx - 1].close) / df_qfq.iloc[target_idx - 1].close, 4),
        'maxPrice': df_qfq.iloc[target_idx].high,
        'maxUpRate': round(
            (df_qfq.iloc[target_idx].high - df_qfq.iloc[target_idx - 1].close) / df_qfq.iloc[target_idx - 1].close, 4),
        'minPrice': df_qfq.iloc[target_idx].low,
        'minUpRate': round(
            (df_qfq.iloc[target_idx].low - df_qfq.iloc[target_idx - 1].close) / df_qfq.iloc[target_idx - 1].close, 4),
        'tradeAmount': df_qfq.iloc[target_idx].tradeAmount,
        'turnOverRate':df_qfq.iloc[target_idx].turnoverRate,
        'code': code,
        'name': stockBase.name,
        'theme':stockBase.theme,
        'industry':stockBase.industry,
        'strategyName':strategyName,
        'scoreDateStr': df_qfq.iloc[target_idx - begin_index].date,
        'killScore': np.int64(score_sum),
        'loseScore': np.int64(lose_sum)
    }


def two_years_earlier(date_str):
    # 将输入的字符串转换为 datetime 对象
    given_date = datetime.strptime(date_str, "%Y%m%d")

    # 计算两年前的日期
    new_date = given_date.replace(year=given_date.year - 2)

    # 将新日期转换回字符串格式并返回
    return new_date.strftime("%Y%m%d")
