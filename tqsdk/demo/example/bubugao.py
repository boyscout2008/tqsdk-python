#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'Golden'

'''
步步高 - 实盘
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

#TODO: 用sdk获取当前是否交易日，是否有夜盘

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


#STEP1：交易信号汇总
k_high = 0
last_k_high = 0 
trading_date = ''

parser = argparse.ArgumentParser()
parser.add_argument('--SYMBOL')
args = parser.parse_args()

if args.SYMBOL != None:
    SYMBOL = args.SYMBOL
else:
    SYMBOL = "DCE.i2005" #用于开发时最新主力合约回测，实际通过参数传递比较好

#STEP2-log
logger.info("Starting bubugao strategy for: %s"%SYMBOL)

api = TqApi(TqSim())
klines = api.get_kline_serial(SYMBOL, duration_seconds=60*60*24, data_length=20)
quote = api.get_quote(SYMBOL)

while True:
    api.wait_update()

    # 实盘是只要14：59触发或盘后任何时间触发运行一次即可
    if api.is_changing(klines):
        df = klines.to_dataframe()

        #logger.info("DEBUG: high is %s, close is %f"%(klines[-1]["high"], klines[-1]["close"]))
        trading_date = bases.get_market_day(klines[-1]["datetime"])
        #logger.info("DATE: %s, close: %f"%(bases.get_market_day(klines[-1]["datetime"]), klines[-1]["close"]))

        #STEP3-策略型机会判定
        # STEP3.1: 找出20日内最近一波多的最高收盘价日m：收近4日新高+背离5，10日线+ 收阳线；
        #logger.info("DEBUG: high is %s, close is %f"%(klines[-1]["high"], klines[-1]["close"]))
        index, k_high = stgy4long.get_index_m(quote, klines, logger)
        #logger.info("BUBUGAO date: %s, adjust interval: %d" %(trading_date, 20 - index - 1))
        # STEP3.2：判断最近4~8日偏多调整
        # n-m=6就是5日偏多调整后的主多，首选它，当然亦可n-m=5就开始考虑，但当心是高位滞涨后的空
        # 判断n-m>=5， <= 9即可
        if index == 11 or index == 12 or index == 14: #8,7,5日偏多调整
            logger.info("MYSTRATEGY - GOOD BUBUGAO date: %s, for %s, adjust interval: %d" %(trading_date, SYMBOL, 20 - index - 1))
        elif index == 13 or index == 15: # 6,4日调整，考虑加入其他调整入11日调整？？
            logger.info("MYSTRATEGY - NORMAL BUBUGAO date: %s, for %s, adjust interval: %d" %(trading_date, SYMBOL, 20 - index - 1))

        #实盘只要收盘后跑一次即可确定
        break

api.close()
logger.removeHandler(fh)
