#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'Golden'


'''
趋势型短线交易信号 - 佛回头
1. 主空或偏空品种充分反弹后转空蓄势期
2. 两种形态：
2.1 近期8根k线，有破5，10日线的，但大多在5，10日线上；当日刚好小阴穿破5日线；
2.2 近期5根K线，先是阴线破5，10日线，再是小阳线承压10日线

算法逻辑：
形态1：
step1：分析近8根k线，第1~6根必须大多在5，10日线上，少量破5，10日线的；5日线高于10日线；
step2：当日穿破5日线，但收缩量小阴
形态2：
step1：

回测小结：
1. 双鬼的标准比较难评判，原则就是上述两点：主空偏空品种，外加承压阳线确认阻力后，次日先相对高才是做空机会
2. 本策略只负责发现形态，具体是否有做空机会要自己根据波段和次日是否有先相对高再次确认阻力位而定
'''

import time, datetime, sys, os.path
import logging
from tqsdk import TqApi, TqSim, TqBacktest #, TargetPosTask
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
    api = TqApi(TqSim(), backtest=TqBacktest(start_dt=date(YEAR-1, 7, 20), end_dt=date(YEAR-1, 12, 15)))
elif SYMBOL.endswith('05'):
    api = TqApi(TqSim(), backtest=TqBacktest(start_dt=date(YEAR-1, 11, 20), end_dt=date(YEAR, 4, 15)))
elif SYMBOL.endswith('09'):
    api = TqApi(TqSim(), backtest=TqBacktest(start_dt=date(YEAR, 3, 20), end_dt=date(YEAR, 8, 15)))
else:
    logger.info("Not supported contract: %s"%SYMBOL)
    exit(1)

#STEP2：策略执行log
logger.info("Starting fohuitou strategy for: %s, actually year: %s"%(SYMBOL, YEAR))

klines = api.get_kline_serial(SYMBOL, duration_seconds=60*60*24, data_length=20)    
#ticks = api.get_tick_serial(SYMBOL)
quote = api.get_quote(SYMBOL)

while True:
    api.wait_update()

    # 跟踪log信息，日k数据会产生两个信号：一个是开盘时，另一个时收盘；如果想根据收盘k线分析前期趋势，用第二个信号
    # 这样就没有之前认为必须开盘才能分析之前所存在的趋势型机会了。
    # 实盘是只要14：59或盘后任何时间触发运行即可，一次退出；
    # 想尾盘参与策略型机会则收盘前运行回报策略型机会，次日择机参与则盘后任何时间运行即可
    if api.is_changing(klines):
        df = klines.to_dataframe()

        #logger.info("DATE: %s, close: %f"%(get_market_day(klines[-1]["datetime"]), klines[-1]["close"]))
        trading_date = bases.get_market_day(klines[-1]["datetime"])
        if trading_date != pre_trading_date: #忽略k线数据开盘事件
            pre_trading_date = trading_date
            continue

        #STEP3：策略型机会判定
        isFohuitou_xiaoyin = stgy4short.parse_klines_fht_xiaoyin(quote, klines, logger)
        isFohuitou_xiaoyang = stgy4short.parse_klines_fht_xiaoyang(quote, klines, logger)
        if isFohuitou_xiaoyin:
            logger.info("MYSTRATEGY - fohuitou_xiaoyin date: %s, for %s" %(trading_date, SYMBOL))
        elif isFohuitou_xiaoyang:
            logger.info("MYSTRATEGY - fohuitou_xiaoyang date: %s, for %s" %(trading_date, SYMBOL))
        else:
            continue

api.close()
logger.removeHandler(fh)
