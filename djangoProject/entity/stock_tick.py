class stock_tick:
    time=''
    price=0,
    vol=0,
    buySellFlag=''
    # 定义构造方法
    def __init__(self, time, price, vol,buySellFlag):
        self.time = time
        self.price = price
        self.vol = vol
        self.buySellFlag = buySellFlag

    def toStr(self):
        return  "时间:%s 价格:%d  量:%d  买卖标识:%s" % (self.time, self.price,self.vol,self.buySellFlag)