#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'Golden'

'''
趋势型短线交易信号 - 震荡两波多后的大空
1. 优选中长线偏空品种，两波多空间基本到位，向下也有空间
2. 算法等同于步步高，两者区别在于每日更新策略输入品种时做删选，同时甄别是第二波多

算法逻辑：
STEP1：收新高阳线
STEP2: 至少前4+1走稳在10日之上 + 至少5天有另一波多背离5日线2%以上

回测小结：
1. 需要实现判断当前中长线趋势还是偏空，或者两波多空间到位，向下也就有空间了；
2. 规避准主多品种风险
'''

import time, datetime, sys, os.path
import logging
from tqsdk import TqApi, TqSim, TqBacktest #, TargetPosTask
from datetime import date
import matplotlib.pyplot as plt
import bases
import stgy4zd
import argparse

rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
curDay = time.strftime('%Y%m%d', time.localtime(time.time()))
curHour = time.strftime('%H', time.localtime(time.time()))
curDate = datetime.datetime.now().weekday()
tradingDay = curDay

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

#STEP1:交易信号汇总
trading_date = ''

parser = argparse.ArgumentParser()
parser.add_argument('--SYMBOL')
parser.add_argument('--ZC1')
parser.add_argument('--ZC2')
args = parser.parse_args()

if args.SYMBOL != None:
    SYMBOL = args.SYMBOL
else:
    SYMBOL = "DCE.i2005"

if args.ZC1 != None:
    ZC1 = float(args.ZC1)
else:
    ZC1 = 0.0

if args.ZC2 != None:
    ZC2 = float(args.ZC2)
else:
    ZC2 = 0.0

#STEP2：log
logger.info("Starting liangboduo strategy for: %s"%SYMBOL)
api = TqApi(TqSim())
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

        #STEP3-策略型机会判定
        #logger.info("DEBUG: high is %s, close is %fLIANGBODUO"%(klines[-1]["high"], klines[-1]["close"]))
        is_dualboduo = stgy4zd.dual_bo_duo(quote, klines, logger)
        if is_dualboduo:
            logger.info("MYSTRATEGY - LIANGBODUO date: %s, for %s" %(trading_date, SYMBOL))
        #实盘只要收盘后跑一次即可确定
        break

api.close()
logger.removeHandler(fh)
