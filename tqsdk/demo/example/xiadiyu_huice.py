#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'Golden'

'''
趋势型短线交易信号 - 下地狱
1. 主空品种（包括多转空）的第二波空机会
2. 调整期一般为5~8天（若是多转空，不排除1~4日短调整夸父逼阴），这里只做蓄势充分的空
3. 程序发现机会，人为判断是否为主空或多转空品种的第一波破位空后的下跌中继决定是否为真的下地狱
算法逻辑类同步步高：
step1：找出20日内最近一波空的最低收盘价日m：收近4日新低+背离5，10日线+ 收阴线；
step2：判断最近4~8日偏空调整，另外趋空日必定收在5日线上，用以确定下地狱信号
'''

import time, datetime, sys, os.path
import logging
from tqsdk import TqApi, TqSim, TqBacktest #, TargetPosTask
#from tqsdk.ta import MA
from datetime import date
import matplotlib.pyplot as plt
import bases
import stgy4short
import argparse

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
log_path = 'E://proj-futures/logs/'
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

#STEP1: 交易信号汇总
k_low = 0
last_k_low = 0 
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
logger.info("Starting xiadiyu strategy for: %s, actually year: %d"%(SYMBOL, YEAR))

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
        
        trading_date = bases.get_market_day(klines[-1]["datetime"])
        if trading_date != pre_trading_date: #忽略k线数据开盘事件
            pre_trading_date = trading_date
            continue

        #STEP3-策略型机会判定
        #logger.info("DATE: %s, close: %f"%(bases.get_market_day(klines[-1]["datetime"]), klines[-1]["close"]))
        index, k_low = stgy4short.get_index_m(quote, klines)
        #logger.info("xiadiyu date: %s, adjust interval: %d" %(trading_date, 20 - index - 1))
        # TODO：判定趋空日的品质
        if index == 11 or index == 12 or index == 14: #8,7,5日偏空调整
            logger.info("GOOD XIADIYU date: %s, for %s, adjust interval: %d" %(trading_date, SYMBOL, 20 - index - 1))
        elif index == 13 or index == 15: # 6,4日调整
            logger.info("NORMAL XIADIYU date: %s, for %s, adjust interval: %d" %(trading_date, SYMBOL, 20 - index - 1))
        else:
            continue
            #logger.info("NOTHING for: %s"%SYMBOL)

api.close()
logger.removeHandler(fh)
