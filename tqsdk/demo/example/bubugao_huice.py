#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'Golden'

'''
步步高-回测
'''

import time, datetime, sys, os.path
import logging
from tqsdk import TqApi, TqSim, TqBacktest #, TargetPosTask
from datetime import date
import matplotlib.pyplot as plt
import bases
import stgy4long
import argparse

rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
curDay = time.strftime('%Y%m%d', time.localtime(time.time()))
curHour = time.strftime('%H', time.localtime(time.time()))
curDate = datetime.datetime.now().weekday()
tradingDay = curDay

#这个data根交易日无关，用于标记策略执行时间，实际策略型机会会在策略执行中提醒

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
log_path = 'E://proj-futures/logs_debug/'
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

#STEP1：交易信号汇总
k_high = 0
last_k_high = 0 
trading_date = ''
pre_trading_date = ''


parser = argparse.ArgumentParser()
parser.add_argument('--SYMBOL')
parser.add_argument('--YEAR')
args = parser.parse_args()

if args.SYMBOL != None:
    SYMBOL = args.SYMBOL
else:
    SYMBOL = "DCE.i2005" # fake contract

if args.YEAR != None:
    YEAR = int(args.YEAR)
else:
    YEAR = 2020 #TODO：取当年值

#parse and decide time duration for backtesting
#有些主力合约不分年份，分析月份后2015年开始逐年回测
if SYMBOL.endswith('01'):
    api = TqApi(TqSim(), backtest=TqBacktest(start_dt=date(YEAR-1, 7, 20), end_dt=date(YEAR-1, 12, 1)))
elif SYMBOL.endswith('05'):
    api = TqApi(TqSim(), backtest=TqBacktest(start_dt=date(YEAR-1, 11, 20), end_dt=date(YEAR, 4, 1)))
elif SYMBOL.endswith('09'):
    api = TqApi(TqSim(), backtest=TqBacktest(start_dt=date(YEAR, 3, 20), end_dt=date(YEAR, 8, 1)))
else:
    logger.info("Not supported contract: %s"%SYMBOL)
    exit(1)

#STEP2：策略执行log
logger.info("Starting bubugao strategy for: %s, actually year: %d"%(SYMBOL, YEAR))

klines = api.get_kline_serial(SYMBOL, duration_seconds=60*60*24, data_length=20)
#ticks = api.get_tick_serial(SYMBOL)
quote = api.get_quote(SYMBOL)

while True:
    api.wait_update()

    # 跟踪log信息，日k数据会产生两个信号：一个是开盘时，另一个是收盘；如果想根据收盘k线分析前期趋势，用第二个信号
    # 这样就没有之前认为必须开盘才能分析之前所存在的趋势型机会了。
    #但在实盘就不好这么做了，毕竟只需要在收盘前启动收盘后关闭程序即可。
    if api.is_changing(klines):
        df = klines.to_dataframe()
        
        trading_date = bases.get_market_day(klines[-1]["datetime"])
        if trading_date != pre_trading_date: #忽略k线数据开盘事件
            pre_trading_date = trading_date
            continue

        #STEP3:策略型机会判定
        #logger.info("DATE: %s, close: %f"%(bases.get_market_day(klines[-1]["datetime"]), klines[-1]["close"]))
        # STEP3.1: 找出20日内最近一波多的最高收盘价日m：收近4日新高+背离5，10日线+ 收阳线；
        index, k_high = stgy4long.get_index_m(quote, klines)
        # STEP3.2：判断最近4~8日偏多调整
        # n-m=6就是5日偏多调整后的主多，首选它，当然亦可n-m=5就开始考虑，但当心是高位滞涨后的空
        # 判断n-m>=5， <= 9即可
        if index == 11 or index == 12 or index == 14: #8,7,5日偏多调整
            logger.info("MYSTRATEGY - GOOD BUBUGAO date: %s, for %s, adjust interval: %d" %(trading_date, SYMBOL, 20 - index - 1))
        elif index == 13 or index == 15: # 6,4日调整，考虑加入其他调整入11日调整？？
            logger.info("MYSTRATEGY - NORMAL BUBUGAO date: %s, for %s, adjust interval: %d" %(trading_date, SYMBOL, 20 - index - 1))
        else:
            continue

api.close()
logger.removeHandler(fh)
