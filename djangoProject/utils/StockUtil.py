import traceback
from datetime import datetime
import time
from decimal import Decimal, ROUND_HALF_UP

import numpy as np
import pandas as pd
from backtrader.feeds import PandasData
import akshare as ak
from scipy.signal import savgol_filter
import backtrader as bt


class StockDetail:
  # Constructor (called when creating an object)
  def __init__(self, code, name,nameAbbr,industry,theme):
    # Instance attributes (unique to each object)
    self.code = code
    self.name = name
    self.nameAbbr = nameAbbr
    self.industry = industry
    self.theme = theme

config = {
  'user': 'root',      # 你的MySQL用户名
  'password': 'Dream1226.27!',  # 你的MySQL密码
  'host': '43.142.151.181',          # MySQL服务器地址，本地为localhost
  'database': 'stock',  # 要连接的数据库名
  'raise_on_warnings': True
}



# 定义额外列的名称
class ExtraData(PandasData):
    lines = (
        'code', 'dateNum', 'tradeAmount', 'maxSubRate', 'increaseRate', 'increaseAmount', 'turnoverRate', 'MA5',
        'days_since_start',
        'savgol_MA5', 'savgol_MA5_slope','savgol_MA10_slope','savgol_MA20_slope','savgol_MA30_slope','savgol_min_slope',
        'savgol_max_slope','MA5_std_dev_3','savgol_MA5_std_dev_3_slope','skill_score','lose_score')  # 添加你的额外列名

    # 将额外数据列与lines属性映射
    params = (
        ('code', -1),
        ('dateNum', -1),
        ('tradeAmount', -1),
        ('increaseRate', -1),
        ('maxSubRate', -1),
        ('increaseAmount', -1),
        ('turnoverRate', -1),
        ('MA5', -1),
        ('days_since_start', -1),
        ('savgol_MA5', -1),
        ('savgol_MA5_slope', -1),
        ('savgol_MA10_slope', -1),
        ('savgol_MA20_slope', -1),
        ('savgol_MA30_slope', -1),
        ('savgol_min_slope', -1),
        ('savgol_max_slope', -1),
        ('MA5_std_dev_3', -1),
        ('savgol_MA5_std_dev_3_slope',-1),
        ('skill_score',-1),
        ('lose_score',-1)

    )


def allStockCerebroInfo(sdate, edate,stockList,cerebro):
    for obj in stockList:
        try:
            # 打开一个不存在的文件
            code = obj.code  # 股票代码
            df_qfq = getStockPandas(code, sdate, edate)
            # 把date作为日期索引，以符合Backtrader的要求
            df_qfq.index = pd.to_datetime(df_qfq['date'])
            start_date = datetime.strptime(sdate, "%Y%m%d")  # 转换日期格式
            end_date = datetime.strptime(edate, "%Y%m%d")
            data = ExtraData(dataname=df_qfq)  # 规范化数据格式
            cerebro.adddata(data, name=code)  # 加载数据
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
        except Exception as e:
            # 文件不存在时执行的代码
            # traceback.print_exc()
            print(f"读取stock  {obj.code} {obj.name}  异常")

def getStockPandas(code, sdate, edate):
    # 利用AKShare获取股票的前复权数据的前6列
    df_qfq = ak.stock_zh_a_hist(symbol=code, adjust="qfq", start_date=sdate, end_date=edate).iloc[:, :11]
    # 处理字段命名，以符合Backtrader的要求
    df_qfq.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'tradeAmount', 'maxSubRate', 'increaseRate',
                      'increaseAmount', 'turnoverRate']


    df_qfq['MA5'] = df_qfq['close'].rolling(window=5).mean()
    df_qfq['MA5'].fillna(1, inplace=True)

    df_qfq['MA10'] = df_qfq['close'].rolling(window=10).mean()
    df_qfq['MA10'].fillna(1, inplace=True)

    df_qfq['MA20'] = df_qfq['close'].rolling(window=20).mean()
    df_qfq['MA20'].fillna(1, inplace=True)

    df_qfq['MA30'] = df_qfq['close'].rolling(window=30).mean()
    df_qfq['MA30'].fillna(1, inplace=True)

    # 计算天数差
    df_qfq['days_since_start'] = (df_qfq['date'] - df_qfq['date'].min()).dt.days

    df_qfq['code'] = int(code)
    df_qfq['dateNum'] = pd.to_datetime(df_qfq['date']).dt.strftime('%Y%m%d').astype(int)



    # 计算斜率参数
    window_length, poly_order = 17, 16
    df_qfq['savgol_MA5'] = savgol_filter(df_qfq['MA5'], window_length=window_length, polyorder=poly_order)
    # 计算斜率
    df_qfq['savgol_MA5_slope'] = np.gradient(df_qfq['savgol_MA5'], df_qfq['days_since_start']).round(2)
    df_qfq['savgol_MA5_slope'] = df_qfq['savgol_MA5'].diff().round(2)

    df_qfq['savgol_MA10'] = savgol_filter(df_qfq['MA10'], window_length=window_length, polyorder=poly_order)
    # 计算斜率
    df_qfq['savgol_MA10_slope'] = np.gradient(df_qfq['savgol_MA10'], df_qfq['days_since_start']).round(2)
    df_qfq['savgol_MA10_slope'] = df_qfq['savgol_MA10'].diff().round(2)

    df_qfq['savgol_MA20'] = savgol_filter(df_qfq['MA20'], window_length=window_length, polyorder=poly_order)
    # 计算斜率
    df_qfq['savgol_MA20_slope'] = np.gradient(df_qfq['savgol_MA20'], df_qfq['days_since_start']).round(2)
    df_qfq['savgol_MA20_slope'] = df_qfq['savgol_MA20'].diff().round(2)

    df_qfq['savgol_MA30'] = savgol_filter(df_qfq['MA30'], window_length=window_length, polyorder=poly_order)
    # 计算斜率
    df_qfq['savgol_MA30_slope'] = np.gradient(df_qfq['savgol_MA30'], df_qfq['days_since_start']).round(2)
    df_qfq['savgol_MA30_slope'] = df_qfq['savgol_MA30'].diff().round(2)

    # boll 计算斜率
    df_qfq['MA5_std_dev']   = df_qfq['MA5'].rolling(window=5).std()
    df_qfq['MA5_std_dev'].fillna(1, inplace=True)
    df_qfq['MA5_std_dev_3']   = df_qfq['MA5_std_dev']*3
    df_qfq['MA5_std_dev_3_slope'] = savgol_filter(df_qfq['MA5_std_dev_3'], window_length=window_length, polyorder=poly_order)
    # df_qfq['savgol_MA5_std_dev_3_slope'] = np.gradient(df_qfq['MA5_std_dev_3'], df_qfq['days_since_start']).round(2)
    df_qfq['savgol_MA5_std_dev_3_slope'] = df_qfq['MA5_std_dev_3_slope'].round(2)

    # 计算最大最小收盘价
    df_qfq['maxOpenClosePrice'] = df_qfq[['open', 'close']].max(axis=1)
    df_qfq['minOpenClosePrice'] = df_qfq[['open', 'close']].min(axis=1)

    # 计算斜率参数
    df_qfq['savgol_max'] = savgol_filter(df_qfq['maxOpenClosePrice'], window_length=window_length, polyorder=poly_order)
    df_qfq['savgol_max_slope'] = np.gradient(df_qfq['savgol_max'], df_qfq['days_since_start']).round(2)
    df_qfq['savgol_max_slope'] = df_qfq['savgol_max'].diff().round(2)
    # 计算斜率最小值
    df_qfq['savgol_min'] = savgol_filter(df_qfq['minOpenClosePrice'], window_length=window_length, polyorder=poly_order)
    df_qfq['savgol_min_slope'] = np.gradient(df_qfq['savgol_min'], df_qfq['days_since_start']).round(2)
    df_qfq['savgol_min_slope'] = df_qfq['savgol_min'].diff().round(2)

    df_qfq['skill_score'] = 0
    for i in range(1, len(df_qfq)):
        #先跌后涨
        if df_qfq['increaseRate'].iloc[i - 1] < -8 and df_qfq['increaseRate'].iloc[i] > 9:
            df_qfq.loc[df_qfq.index[i], 'skill_score'] += 2
        # 30开头的股票，前一天涨幅小于19，当天开盘降价涨幅大于1%
        if (code[:2] == "30" and df_qfq['open'].iloc[i - 1] <df_qfq['close'].iloc[i - 1] and
                df_qfq['increaseRate'].iloc[i - 1] > 4 and  df_qfq['increaseRate'].iloc[i - 1] < 19
                and df_qfq['open'].iloc[i]/df_qfq['close'].iloc[i-1] >1.02) :
            df_qfq.loc[df_qfq.index[i], 'skill_score'] += 1
        # 60开头的股票，前一天涨幅小于9，当天开盘降价涨幅大于1%
        if ((code[:2] == "60" or code[:2]=='00') and df_qfq['open'].iloc[i - 1] <df_qfq['close'].iloc[i - 1] and
                df_qfq['increaseRate'].iloc[i - 1] > 3 and  df_qfq['increaseRate'].iloc[i - 1] < 9
                and df_qfq['open'].iloc[i]/df_qfq['close'].iloc[i-1] >1.01) :
            df_qfq.loc[df_qfq.index[i], 'skill_score'] += 1
        # 主板股票，涨停后往下杀
        if ((code[:2] == "60" or code[:2]=='00') and df_qfq['open'].iloc[i ] >df_qfq['close'].iloc[i]
                and df_qfq['open'].iloc[i]/df_qfq['close'].iloc[i-1] >1.09  and df_qfq['close'].iloc[i-1]/df_qfq['close'].iloc[i-2] <1.09):
            df_qfq.loc[df_qfq.index[i], 'skill_score'] += 2
        # # 创业板股票，涨停后往下杀
        # if (code[:2] == "30"  and df_qfq['open'].iloc[i ] >df_qfq['close'].iloc[i]
        #         and df_qfq['open'].iloc[i]/df_qfq['close'].iloc[i-1] >1.09  and df_qfq['open'].iloc[i]/df_qfq['close'].iloc[i-1] <1.18
        #         and df_qfq['close'].iloc[i-1]/df_qfq['close'].iloc[i-2] <1.09):
        #     df_qfq.loc[df_qfq.index[i], 'skill_score'] += 3

    df_qfq['lose_score'] = 0
    for i in range(1, len(df_qfq)):
        #前一天收红，第二天低开，
        if df_qfq['open'].iloc[i-1 ] <df_qfq['close'].iloc[i-1 ] and  df_qfq['open'].iloc[i ] >df_qfq['close'].iloc[i ] and df_qfq['increaseRate'].iloc[i - 1] > 5 and df_qfq['open'].iloc[i] / df_qfq['close'].iloc[i - 1] < 0.98:
            df_qfq.loc[df_qfq.index[i], 'lose_score'] += 1
        #五日线向上，你低开
        elif df_qfq['savgol_MA5_slope'].iloc[i ] >0 and df_qfq['open'].iloc[i] / df_qfq['close'].iloc[i - 1] < 0.98 and df_qfq['open'].iloc[i ] >df_qfq['close'].iloc[i ]:
            df_qfq.loc[df_qfq.index[i], 'lose_score'] += 1
        #跌5个点第二天不回补
        # if df_qfq['increaseRate'].iloc[i - 1] < -5 and df_qfq['increaseRate'].iloc[i-1] +df_qfq['increaseRate'].iloc[i]< -4:
        #     df_qfq.loc[df_qfq.index[i], 'lose_score'] += 1
        # if df_qfq['increaseRate'].iloc[i - 1] > 4 and df_qfq['open'].iloc[i] / df_qfq['close'].iloc[i - 1] < 0.98 and df_qfq['open'].iloc[i] / df_qfq['close'].iloc[i - 1] > 0.96:
        #     df_qfq.loc[df_qfq.index[i], 'lose_score'] += 1
        # if df_qfq['increaseRate'].iloc[i - 1] > 4 and df_qfq['open'].iloc[i] / df_qfq['close'].iloc[i - 1] < 0.96 and df_qfq['open'].iloc[i] / df_qfq['close'].iloc[i - 1] > 0.93:
        #     df_qfq.loc[df_qfq.index[i], 'lose_score'] += 2
        # if df_qfq['increaseRate'].iloc[i - 1] > 4 and df_qfq['open'].iloc[i] / df_qfq['close'].iloc[i - 1] < 0.93 :
        #     df_qfq.loc[df_qfq.index[i], 'lose_score'] += 4
        #
        # if df_qfq['open'].iloc[i - 1] <df_qfq['close'].iloc[i - 1] and df_qfq['increaseRate'].iloc[i - 1] <4 and df_qfq['open'].iloc[i ] >df_qfq['close'].iloc[i ] and df_qfq['open'].iloc[i] / df_qfq['close'].iloc[i - 1] < 0.96  and df_qfq['open'].iloc[i] / df_qfq['close'].iloc[i - 1] > 0.94:
        #     df_qfq.loc[df_qfq.index[i], 'lose_score'] += 2
        # if df_qfq['open'].iloc[i - 1] <df_qfq['close'].iloc[i - 1] and df_qfq['increaseRate'].iloc[i - 1] <4 and df_qfq['open'].iloc[i ] >df_qfq['close'].iloc[i ]  and df_qfq['open'].iloc[i] / df_qfq['close'].iloc[i - 1] < 0.94  and df_qfq['open'].iloc[i] / df_qfq['close'].iloc[i - 1] > 0.88:
        #     df_qfq.loc[df_qfq.index[i], 'lose_score'] += 3
        # if df_qfq['open'].iloc[i - 1] <df_qfq['close'].iloc[i - 1] and df_qfq['increaseRate'].iloc[i - 1] <4 and df_qfq['open'].iloc[i] / df_qfq['close'].iloc[i - 1] < 0.88 :
        #     df_qfq.loc[df_qfq.index[i], 'lose_score'] += 4


    
    
    # 把date作为日期索引，以符合Backtrader的要求
    df_qfq.index = pd.to_datetime(df_qfq['date'])
    return df_qfq


def format_date(date_int):
    date_str = str(int(date_int))
    # 将字符串日期转换为datetime对象
    date_obj = datetime.strptime(date_str, '%Y%m%d')
    # 将datetime对象格式化为字符串
    return date_obj.strftime('%Y-%m-%d')


#当日收盘价小于前两日的最高价，当日最高价小于前两日的最高价
def is_range_two_hight_price(data,i):
    return data.close[i]<=max(data.close[i-2], data.close[i-1]) and data.high[i]<=max(data.high[i-2], data.high[i-1])


def orderTradeRecord(backTraderInfo,order,strategyName):
    # 如果order为submitted/accepted,返回空
    if order.status in [order.Submitted, order.Accepted]:
        return
    # 指令为buy/sell,报告价格结果
    if order.status in [order.Completed]:
        currStockDetail = next((obj for obj in backTraderInfo.params.stockCodeList if obj.code == order.data._name), None)
        score_period = len(order.params.data)
        if len(order.params.data) > 40:
            score_period = 40
        score_sum = sum([order.params.data.skill_score[-i] for i in range(1, score_period)])
        lose_sum = sum([order.params.data.lose_score[-i] for i in range(1, score_period)])

        if order.isbuy():
            backTraderInfo.log(
                f"买入:股票代码:{order.data._name},\
                        股票名称:{currStockDetail.name},\
                        价格:{order.executed.price},\
                    成本:{order.executed.value},\
                    手续费:{order.executed.comm}"
            )
            backTraderInfo.order_list.append((order.data._name, currStockDetail.name, 'B',
                                    format_date(order.params.data.dateNum[-1]), '', order.executed.size, order.executed.price,
                                    order.executed.comm, 0, order.executed.value,strategyName,score_sum,lose_sum))

        else:

            backTraderInfo.log(
                f"卖出:股票代码:{order.data._name},\
                        n股票名称:{currStockDetail.name},\
                        价格:{order.executed.price},\
                        成本: {order.executed.value},\
                        手续费{order.executed.comm}, \
                        利润百分比{round(order.executed.pnl / order.executed.value * 100, 2)}%,"
            )
            backTraderInfo.order_list.append((order.data._name, currStockDetail.name, 'S',
                                    format_date(order.params.data.dateNum[-1]), '', order.executed.size, order.executed.price,
                                    order.executed.comm, order.executed.pnl, order.executed.value,strategyName,score_sum,lose_sum))

    elif order.status in [order.Canceled, order.Margin, order.Rejected]:
        backTraderInfo.log("交易失败")  # 指令取消/交易失败, 报告结果
    backTraderInfo.order = None


def sellCondition(backTraderInfo,position,data,bt):
    # 满足卖出条件,低开小于三卖出
    if data.open[0] / data.close[-1] < 0.96:
        backTraderInfo.sell(data=data, exectype=bt.Order.Limit, size=position.size, price=data.open[0] * 0.99)
        # 连续两天收阴
    elif data.close[0] < data.open[0] and data.close[-1] < data.open[-1]:
        backTraderInfo.sell(data=data, exectype=bt.Order.Limit, size=position.size, price=data.close[0])
        # 止损线
    elif data.increaseRate[0] < -8 or (position.price * 0.93 > data.close[0]):
        backTraderInfo.sell(data=data, exectype=bt.Order.Limit, size=position.size, price=data.close[0])
    elif is_range_two_hight_price(data, 0) and is_range_two_hight_price(data,
                                                                        -1) :
        backTraderInfo.sell(data=data, exectype=bt.Order.Limit, size=position.size, price=data.close[0])


def backTraderProcess(stockList,batch_size,sdate, edate,start_cash,stake,commfee,BollStrategy):
    for i in range(0, len(stockList), batch_size):
        time.sleep(10)
        batch = stockList[i:i + batch_size]
        cerebro = bt.Cerebro()  # 创建回测系统实例
        # 添加数据
        allStockCerebroInfo(sdate, edate, batch, cerebro)
        cerebro.addstrategy(BollStrategy, nk=13, printlog=True)  # 加载交易策略
        cerebro.broker.setcash(start_cash)  # broker设置资金
        cerebro.broker.setcommission(commission=commfee)  # broker手续费
        cerebro.addsizer(bt.sizers.FixedSize, stake=stake)  # 设置买入数量
        print("期初总资金: %.2f" % start_cash)
        cerebro.run()  # 运行回测
        end_value = cerebro.broker.getvalue()  # 获取回测结束后的总资金
        print("期末总资金: %.2f" % end_value)

# 实体K线，无长上影线和下影线
def kLineShiTi(data,i):
    return data.high[i]-max(data.close[i], data.open[i])+min(data.close[i], data.open[i])-data.low[i]<(data.high[i]-data.low[i])*0.5


def get_up_limit_price(code, price):
    price = Decimal(price)
    if code.startswith(("30", "68", "11", "12")):
        multiply = Decimal('1.2')
    elif code.startswith(("60", "00")):
        multiply = Decimal('1.1')
    else:
        multiply = Decimal('1.3')

    if code.startswith(("11", "12")):
        result = (price * multiply).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
    else:
        result = (price * multiply).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    return result
def is_up_limit(code,lastClosePrice, closePrice):
    return  get_up_limit_price(code,lastClosePrice)-Decimal(str(closePrice))<0.001

