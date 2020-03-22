#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'Golden'

'''
趋势型短线交易信号 - 夸父逼阴
1. 主空或偏空品种一波空已经启动，次日再次做中大阴；或1~2小中继后继续做空
2. 基本条件是未到中强支撑位，有较大做空空间；并且开盘未背离5日线
3. 两种形态：刚破局部支撑位且向下做空空间较大；第二种是局部支撑1~2日小中继

算法逻辑：
step1：输入2个支撑位参数：转空支撑位，破位后向下中强支撑位
step2：开始空破位转空支撑位（多转空品种）或接近转空支撑位（震荡和偏空品种），但这波空空间不大不到位
step3: 判断当前阴线开盘对5，10日均线无大背离，不同波动时期判断标准不同

回测小结：
1. 需要事先判断当前处于主空或多转空时期的初级阶段，定期更新转空支撑位和中强支撑位
2. 所以它比其他品种而言，除了要删选输入品种外，还要有两个支撑位输入
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
zhicheng1 = 0.0
zhicheng2 = 0.0

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
logger.info("Starting biyin strategy for: %s with zhicheng1: %s, zhicheng2: %s"%(SYMBOL, ZC1, ZC2))
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

        #STEP3：策略型机会判定
        isBiyin = stgy4short.parse_klines_by(quote, klines, ZC1, ZC2, logger)
        #logger.info("xiadiyu date: %s, adjust interval: %d" %(trading_date, 20 - index - 1))
        # TODO：判定趋空日的品质
        if isBiyin:
            logger.info("MYSTRATEGY - biyin date: %s, for %s" %(trading_date, SYMBOL))
        #收盘跑一次即可
        break

api.close()
logger.removeHandler(fh)
