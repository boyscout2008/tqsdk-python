#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'Golden'

'''
趋势型短线交易信号 - 下地狱
1. 主空品种（包括多转空）的第二波空机会
2. 调整期一般为5~8天（若是多转空，不排除1~4日短调整夸父逼阴），这里只做蓄势充分的空
算法逻辑类同步步高：
step1：找出20日内最近一波空的最低收盘价日m：收近4日新低+背离5，10日线+ 收阴线；
step2：判断最近4~8日偏空调整，另外趋空日必定收在5日线上，用以确定下地狱信号

回测小结：
1. 下地狱必须遵循：主空或偏空品种，并且第一波空破位后承压10日线调整的第二波空；
2. 对于整体震荡或偏多震荡品种（铁矿16年之后就是），只有多转空机会，这种往往没有规则的下地狱，更多的是逼阴
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

#返回近期一波多的收新低阴线
def get_index_m(quote, klines):
    m = 0
    k_low = 0

    df = klines.to_dataframe()
    if len(df) <20:
        return m
    #logger.info("klines.low: %f, klines.close: %f" % (klines.low[-1], klines.close[-1]))
    #STEP1：遍历找出最后一波空的收新低阴线日
    ma5 = talib.MA(df.close, timeperiod=5) 
    ma10 =  talib.MA(df.close, timeperiod=10)
    for i in range(9, 20): #只看最近的一波空，前面数据用于计算MA
        pre3LL =  min(klines.low[i-3:i])  # 前3日最低价
        if klines.close[i] < pre3LL and klines.close[i]<klines.open[i] and klines.close[i] < ma5[i]*0.985 and klines.close[i] < ma10[i]*0.985:
            #logger.info("ma5: %f, ma10: %f, df.close: %f, pre3LL:%f" % (ma5[i], ma10[i], df.close[i], pre3LL))
            m = i
            k_low = klines.close[i]
    

    # STEP2：判断最近4~8日偏空调整，另外趋多日必定收在5日线的阴线，用以确定下地狱信号
    # n-m=6就是5日偏多调整后的主多，首选它，当然亦可n-m=5就开始考虑，但当心是高位滞涨后的空
    # 改进：很多都是不规则第二波空，只要是承压10日线，且是主空或已破位多转空的第二波就可以认为是下地狱
    # 判断n-m>=5， <= 9即可 
    if (m > 10 and m <= 15) and (klines.close[m+1:20]<=ma10[m+1:20]).all(): #and klines.close[-1] <= ma5[len(df)-1]: #8,7,5日偏空调整
        #logger.info("ma5: %f, ma10: %f, df.close: %f" % (ma5[len(df)-1], ma10[len(df)-1], df.close[i]))
        return m, k_low
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

### 交易信号汇总
k_low = 0
last_k_low = 0 
trading_date = ''
pre_trading_date = ''


parser = argparse.ArgumentParser()
parser.add_argument('--SYMBOL')
args = parser.parse_args()

if args.SYMBOL != None:
    SYMBOL = args.SYMBOL
else:
    SYMBOL = "DCE.i1909"

logger.info("Starting xiadiyu strategy for: %s"%SYMBOL)
# TODO：交易账号替换模拟账号
#SYMBOL = "DCE.p2005"  # 合约代码
api = TqApi(TqSim())
#api = TqApi(TqSim(), backtest=TqBacktest(start_dt=date(2018, 7, 20), end_dt=date(2018, 12, 1))) 
#api = TqApi(TqSim(), backtest=TqBacktest(start_dt=date(2018, 11, 20), end_dt=date(2019, 4, 1)))
#api = TqApi(TqSim(), backtest=TqBacktest(start_dt=date(2019, 3, 20), end_dt=date(2019, 8, 1)))
klines = api.get_kline_serial(SYMBOL, duration_seconds=60*60*24, data_length=20)    
#ticks = api.get_tick_serial(SYMBOL)
quote = api.get_quote(SYMBOL)

while True:
    api.wait_update()

    # 跟踪log信息，日k数据会产生两个信号：一个是开盘时，另一个时收盘；如果想根据收盘k线分析前期趋势，用第二个信号
    # 这样就没有之前认为必须开盘才能分析之前所存在的趋势型机会了。
    # 实盘是只要14：59触发即可
    if api.is_changing(klines):
        df = klines.to_dataframe()

        #logger.info("DATE: %s, close: %f"%(get_market_day(klines[-1]["datetime"]), klines[-1]["close"]))
        trading_date = get_market_day(klines[-1]["datetime"])
        index, k_low = get_index_m(quote, klines)
        #logger.info("xiadiyu date: %s, adjust interval: %d" %(trading_date, 20 - index - 1))
        # TODO：判定趋空日的品质
        if index == 11 or index == 12 or index == 14: #8,7,5日偏空调整
            logger.info("MYSTRATEGY - GOOD XIADIYU date: %s, for %s, adjust interval: %d" %(trading_date, SYMBOL, 20 - index - 1))
        elif index == 13 or index == 15: # 6,4日调整
            logger.info("MYSTRATEGY - NORMAL XIADIYU date: %s, for %s, adjust interval: %d" %(trading_date, SYMBOL, 20 - index - 1))

        #收盘跑一次即可
        break

api.close()
logger.removeHandler(fh)
