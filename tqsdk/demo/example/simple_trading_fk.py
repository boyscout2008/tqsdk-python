#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'Golden'

'''
日内实盘交易风控 - 程序化下单工具
1. 用程序化下单：开多，开空；其他操作如，平仓和撤单用app完成
2. 对开仓价格和手数做风险控制

'''

import datetime, time, sys, os.path
import logging
from datetime import date
from tqsdk import TqApi, TqSim, TqBacktest, TargetPosTask
import operator
import bases
import argparse
import talib

TIME_CELL = 60  # 等时长下单的时间单元, 单位: 秒
TARGET_VOLUME = 5  # 目标交易手数 (>0: 多头, <0: 空头)

#START_HOUR, START_MINUTE = 21, 0  # 计划交易时段起始时间点
#END_HOUR, END_MINUTE = 15, 0  # 计划交易时段终点时间点

rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
curDay = time.strftime('%Y%m%d', time.localtime(time.time()))
curHour = time.strftime('%H', time.localtime(time.time()))
curDate = datetime.datetime.now().weekday()
runningDate = curDay

logger = logging.getLogger()
logger.setLevel(logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument('--SYMBOL')
parser.add_argument('--FANGXIANG') # SELL | BUY
parser.add_argument('--LIMITPRICE')
parser.add_argument('--VOLUME')

args = parser.parse_args()

if args.SYMBOL != None:
    SYMBOL = args.SYMBOL
else:
    SYMBOL = "DCE.i2009"

if args.FANGXIANG != None:
    FANGXIANG = args.FANGXIANG
else:
    exit(-1)

if args.LIMITPRICE != None:
    LIMITPRICE = float(args.LIMITPRICE)
else:
    exit(-1)

if args.VOLUME != None:
    VOLUME = float(args.VOLUME)
else:
    exit(-1)

a = __file__
c = os.path.basename(a) #获取文件名称

# 第二步，创建日志文件和控制台两个handler
log_path = 'E://proj-futures/logs/'
log_name = log_path + runningDate + '-' + SYMBOL + '-' + c + '.log'
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

api = TqApi()

#time_slot_start = datetime.time(START_HOUR, START_MINUTE)  # 计划交易时段起始时间点
#time_slot_end = datetime.time(END_HOUR, END_MINUTE)  # 计划交易时段终点时间点
klines = api.get_kline_serial(SYMBOL, TIME_CELL, data_length=int(10 * 60 * 60 / TIME_CELL))
#target_pos = TargetPosTask(api, SYMBOL)
position = api.get_position(SYMBOL)  # 持仓信息
account = api.get_account()
quote = api.get_quote(SYMBOL)

logger.info("start simple_trading_fk for %s!"%(SYMBOL))

current_volume = 0  # 记录持仓量
traded_volume = 0
cur_trading_date = ''

short_price = 0.0
sum_profit = 0.0
last_kong_index = 0

while True:
    api.wait_update()

    if api.is_changing(position):
        if position["volume_short_today"] ！= 0:
            current_volume = -1 * position["volume_short_today"]
            print("current short volume: %d" % (current_volume))
        elif position["volume_long_today"] ！= 0:
            current_volume = position["volume_long_today"]
            print("current long volume: %d" % (current_volume))
        else:
            current_volume = 0
            print("zhiying or zhishun is finished.")
            

    # 新产生一根K线计算分时均价，判断滞涨止跌信号
    if api.is_changing(klines[-1], "datetime"):
        df = klines.to_dataframe()
        
        trading_date = bases.get_market_day(klines[-1]["datetime"])
        if trading_date != cur_trading_date:
            current_volume  = 0
            traded_volume = 0
            #logger.info("###%s, %s",trading_date, cur_trading_date)
            cur_trading_date = trading_date
            # workaround: ignore the first signal for kline with last day's close
            df["date"] = df.datetime.apply(lambda x: bases.get_market_day(x))
            df = df[(df["date"] == cur_trading_date)]
            if len(df) > 1:
                continue

        df["time"] = df.datetime.apply(lambda x: bases.get_kline_time(x))
        df["date"] = df.datetime.apply(lambda x: bases.get_market_day(x))
        df = df[(df["date"] == cur_trading_date)]

        #基于分钟k线计算的vwap有误差，应该基于秒级计算，实盘修正它？？？还是忽略这点误差？？？
        df = df.assign(vwap = ((df["volume"]*df["close"]).cumsum() / df["volume"].cumsum()).ffill())

        now = datetime.datetime.strptime(quote["datetime"], "%Y-%m-%d %H:%M:%S.%f")  # 当前quote的时间
        curTime = now
        curHour = now.hour
        curMinute = now.minute

        #logger.info("CURRENT PRICES:  close = %f, vwap = %f, day_open = %f at %s!" % (df["close"].iloc[-1], df["vwap"].iloc[-1], df["open"].iloc[0], now))

        close_low_index, close_low = min(enumerate(df["close"]), key=operator.itemgetter(1))
        close_high_index, close_high = max(enumerate(df["close"]), key=operator.itemgetter(1))

        df_zd = df[close_low_index:len(df)]
        df_zz = df[close_high_index:len(df)]

        #简单风控：杜绝追涨杀跌
        if FANGXIANG == "SELL":
            if LIMITPRICE < df["vwap"].iloc[-1]*0.998:
                logger.info("INVALID zhuikong order with price: %f at %s! is it ZHUDUO?" % (LIMITPRICE, now))
            else:
                api.insert_order(symbol=SYMBOL, direction="SELL", offset="OPEN", limit_price=LIMITPRICE, volume=VOLUME)
                logger.info("SHORT order with price: %f at %s!" % (LIMITPRICE, now))
        elif FANGXIANG == "BUY":
            if LIMITPRICE > df["vwap"].iloc[-1]*1.002:
                logger.info("INVALID zhuiduo order with price: %f at %s! is it ZHUKONG" % (LIMITPRICE, now))
            else:
                api.insert_order(symbol=SYMBOL, direction="BUY", offset="OPEN", limit_price=LIMITPRICE, volume=VOLUME)
                logger.info("LONG order with price: %f at %s!" % (LIMITPRICE, now))
        else:
            logger.info("invalid order: %s at %s!" % (FANGXIANG, now))

api.close()
logger.removeHandler(fh)