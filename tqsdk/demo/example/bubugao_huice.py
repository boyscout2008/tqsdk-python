#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'Golden'

'''
日内交易信号
'''

import time, datetime, sys, os.path
import logging
from tqsdk import TqApi, TqSim, TqBacktest #, TargetPosTask
#from tqsdk.ta import MA
from datetime import date
import matplotlib.pyplot as plt
import base
import talib
import argparse


def get_kline_time(kline_datetime):
    """获取k线的时间(不包含日期)"""
    kline_time = datetime.datetime.fromtimestamp(kline_datetime//1000000000).time()  # 每根k线的时间
    return kline_time

def get_market_day(kline_datetime):
    """获取k线所对应的交易日"""
    kline_dt = datetime.datetime.fromtimestamp(kline_datetime//1000000000)  # 每根k线的日期和时间
    if kline_dt.hour >= 18:  # 当天18点以后: 移到下一个交易日
        kline_dt = kline_dt + datetime.timedelta(days=1)
    while kline_dt.weekday() >= 5:  # 是周六或周日,移到周一
        kline_dt = kline_dt + datetime.timedelta(days=1)
    return kline_dt.date()

#返回近期一波多的收新高阳线
def get_index_m(quote, klines):
    m = 0
    k_high = 0

    #if len(klines) < 20:
    #    return m
    df = klines.to_dataframe()
    if len(df) <20:
        return m
    #logger.info("klines.high: %f, klines.close: %f" % (klines.high[-1], klines.close[-1]))
    #STEP1：遍历找出最后一波多的收新高阳线日
    ma5 = talib.MA(df.close, timeperiod=5) 
    ma10 =  talib.MA(df.close, timeperiod=10)
    for i in range(9, 20): #只看最近的一波多，前面数据用于计算MA
        pre3HH =  max(klines.high[i-3:i])  # 前3日最高价
        if klines.close[i] > pre3HH and klines.close[i]>klines.open[i] and klines.close[i] > ma5[i]*1.015 and klines.close[i] > ma10[i]*1.015:
            #logger.info("ma5: %f, ma10: %f, df.close: %f, pre3HH:%f" % (ma5[i], ma10[i], df.close[i], pre3HH))
            m = i
            k_high = klines.close[i]
    

    # STEP2：判断最近4~8日偏多调整，另外趋多日必定收在5日线上，用以确定步步高信号
    # n-m=6就是5日偏多调整后的主多，首选它，当然亦可n-m=5就开始考虑，但当心是高位滞涨后的空
    # 判断n-m>=5， <= 9即可 
    if (m > 10 and m <= 15) and (klines.close[m+1:20]>=ma10[m+1:20]).all() and klines.close[-1] >= ma5[len(df)-1]: #8,7,5日偏多调整
        #logger.info("ma5: %f, ma10: %f, df.close: %f" % (ma5[len(df)-1], ma10[len(df)-1], df.close[i]))
        return m, k_high
    else: 
        return 0, 0

# 周期参数
NDAYS = 6  # 5天不收新高，亦可降低至4

rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
curDay = time.strftime('%Y%m%d', time.localtime(time.time()))
curHour = time.strftime('%H', time.localtime(time.time()))
curDate = datetime.datetime.now().weekday()
tradingDay = curDay

#TODO: 用sdk获取当前是否交易日，是否有夜盘

if curDate>4: # weekend
    pass#exit(0)
elif curDate==4: # friday
    if int(curHour)>=15:
        tradingDay = (datetime.datetime.now() + datetime.timedelta(days=3)).strftime('%Y%m%d')
else:
    if int(curHour)>=15:
        tradingDay =  (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y%m%d')


logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 第二步，创建日志文件和控制台两个handler
log_path = 'E://proj-futures-2019/log/'
log_name = log_path + tradingDay + '.log'
logfile = log_name
fh = logging.FileHandler(logfile, mode='a+')
fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # 输出到console的log等级的开关
# 第三步，定义handler的输出格式
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# 第四步，将logger添加到handler里面
logger.addHandler(fh)
logger.addHandler(ch)

#logger.info(time.localtime( time.time()))
#curTime = time.strftime('%H:%M', time.localtime(time.time()))
#logger.info("program start_time: "+curTime)

### 交易信号汇总
k_high = 0
last_k_high = 0 
trading_date = ''
pre_trading_date = ''


parser = argparse.ArgumentParser()
parser.add_argument('--SYMBOL')
args = parser.parse_args()

if args.SYMBOL != None:
    SYMBOL = args.SYMBOL
else:
    SYMBOL = "DCE.i2005"

logger.info("Starting bubugao strategy for: %s"%SYMBOL)
# TODO：交易账号替换模拟账号
#SYMBOL = "DCE.p2005"  # 合约代码
#api = TqApi(TqSim())
api = TqApi(TqSim(), backtest=TqBacktest(start_dt=date(2019, 11, 20), end_dt=date(2020, 3, 8))) 
klines = api.get_kline_serial(SYMBOL, duration_seconds=60*60*24, data_length=20)
#ticks = api.get_tick_serial(SYMBOL)
quote = api.get_quote(SYMBOL)

#index = get_index_m(quote, klines)

while True:
    api.wait_update()
    
    #curTime = time.strftime('%H:%M', time.localtime(time.time()))
    #curHour = time.strftime('%H', time.localtime(time.time()))
    #curMinute = time.strftime('%M', time.localtime(time.time()))


    # 跟踪log信息，日k数据会产生两个信号：一个是开盘时，另一个是收盘；如果想根据收盘k线分析前期趋势，用第二个信号
    # 这样就没有之前认为必须开盘才能分析之前所存在的趋势型机会了。
    #但在实盘就不好这么做了，毕竟只需要在收盘前启动收盘后关闭程序即可。
    if api.is_changing(klines):
        df = klines.to_dataframe()
        
        trading_date = get_market_day(klines[-1]["datetime"])
        if trading_date != pre_trading_date: #忽略k线数据开盘事件
            pre_trading_date = trading_date
            continue

        now = datetime.datetime.strptime(quote["datetime"], "%Y-%m-%d %H:%M:%S.%f")  # 当前quote的时间
        curTime = now
        curHour = now.hour
        curMinute = now.minute

        #logger.info("DATE: %s, close: %f"%(get_market_day(klines[-1]["datetime"]), klines[-1]["close"]))
        #df_30mins = df[-30:]
        #curClose = klines[-1]["close"]
        # STEP1: 找出20日内最近一波多的最高收盘价日m：收近4日新高+背离5，10日线+ 收阳线；
        #logger.info("BBB: %s, %f"%(klines[-1]["high"], klines[-1]["close"]));
        index, k_high = get_index_m(quote, klines)
        #logger.info("BUBUGAO date: %s, adjust interval: %d" %(trading_date, 20 - index - 1))
        # STEP2：判断最近4~8日偏多调整
        # n-m=6就是5日偏多调整后的主多，首选它，当然亦可n-m=5就开始考虑，但当心是高位滞涨后的空
        # 判断n-m>=5， <= 9即可
        if index == 11 or index == 12 or index == 14: #8,7,5日偏多调整
            logger.info("GOOD BUBUGAO date: %s, for %s, adjust interval: %d" %(trading_date, SYMBOL, 20 - index - 1))
        elif index == 13 or index == 15: # 6,4日调整，考虑加入其他调整入11日调整？？
            logger.info("NORMAL BUBUGAO date: %s, for %s, adjust interval: %d" %(trading_date, SYMBOL, 20 - index - 1))
        else:
            continue
        #if  index > 10 and index <= 15: #and last_k_high != k_high:  #最多8日调整，最少4日调整
            #logger.info("date: %s, df.open: %f, k_high: %f" % (get_market_day(klines[-1]["datetime"]), klines[-1]["close"], k_high))
            #last_k_high = k_high

api.close()
logger.removeHandler(fh)
