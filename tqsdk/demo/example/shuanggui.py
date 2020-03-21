#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'Golden'

'''
趋势型短线交易信号 - 双鬼拍门
1. 主空或偏空品种下跌中继
2. 之前有阴线背离5，10日线，当前连续两天收阳，但承压5，10日线
算法逻辑：
step1：分析近3根k线，第一根是阴线，且小背离5日线；后面两根是阳线，都承压10日线
step2：后面两根阳线要做一些限制：第二根阳线收盘价不能低于昨日收盘价，最高价要至少等于昨日最高价
step3：其他限制？？？

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

### 交易信号汇总
trading_date = ''


parser = argparse.ArgumentParser()
parser.add_argument('--SYMBOL')
args = parser.parse_args()

if args.SYMBOL != None:
    SYMBOL = args.SYMBOL
else:
    SYMBOL = "DCE.i2005"

logger.info("Starting shuanggui strategy for: %s"%SYMBOL)

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
        isShuanggui = stgy4short.parse_klines_sg(quote, klines, logger)
        #logger.info("xiadiyu date: %s, adjust interval: %d" %(trading_date, 20 - index - 1))
        # TODO：判定趋空日的品质
        if isShuanggui:
            logger.info("MYSTRATEGY - Shuanggui date: %s, for %s" %(trading_date, SYMBOL))
        #收盘跑一次即可
        break

api.close()
logger.removeHandler(fh)
