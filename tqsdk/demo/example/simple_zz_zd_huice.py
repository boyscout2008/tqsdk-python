#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'Golden'

'''
日内交易信号 - 多背离滞涨开空，空背离止跌开多
1. 第一个日内交易策略，建立实盘和回测代码框架

算法逻辑：

回测小结：
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

# 第二步，创建日志文件和控制台两个handler
log_path = 'E://proj-futures/logs_debug/'
log_name = log_path + runningDate + '.log'
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

parser = argparse.ArgumentParser()
parser.add_argument('--SYMBOL')
parser.add_argument('--YEAR')
args = parser.parse_args()

if args.SYMBOL != None:
    SYMBOL = args.SYMBOL
else:
    SYMBOL = "DCE.i2005"

if args.YEAR != None:
    YEAR = int(args.YEAR)
else:
    YEAR = 2020 #TODO：取当年值

#parse and decide time duration for backtesting
#有些主力合约不分年份，分析月份后2015年开始逐年回测
if SYMBOL.endswith('01'):
    api = TqApi(TqSim(), backtest=TqBacktest(start_dt=date(YEAR-1, 7, 20), end_dt=date(YEAR-1, 12, 15)))
elif SYMBOL.endswith('05'):
    api = TqApi(TqSim(), backtest=TqBacktest(start_dt=date(YEAR-1, 11, 20), end_dt=date(YEAR-1, 12, 1)))
    #api = TqApi(TqSim(), backtest=TqBacktest(start_dt=date(YEAR-1, 12, 1), end_dt=date(YEAR, 3, 30)))
elif SYMBOL.endswith('09'):
    api = TqApi(TqSim(), backtest=TqBacktest(start_dt=date(YEAR, 3, 20), end_dt=date(YEAR, 8, 15)))
else:
    logger.info("Not supported contract: %s"%SYMBOL)
    exit(1)

logger.info("start beili_zz_zd daily strategy for %s in %d!"%(SYMBOL, YEAR))

#time_slot_start = datetime.time(START_HOUR, START_MINUTE)  # 计划交易时段起始时间点
#time_slot_end = datetime.time(END_HOUR, END_MINUTE)  # 计划交易时段终点时间点
klines = api.get_kline_serial(SYMBOL, TIME_CELL, data_length=int(10 * 60 * 60 / TIME_CELL))
target_pos = TargetPosTask(api, SYMBOL)
position = api.get_position(SYMBOL)  # 持仓信息
quote = api.get_quote(SYMBOL)


current_volume = 0  # 记录持仓量
cur_trading_date = ''
day_open = 0.0

long_price = 0.0
short_price = 0.0
sum_profit = 0.0

while True:
    api.wait_update()
    # 新产生一根K线计算分时均价，判断滞涨止跌信号
    if api.is_changing(klines[-1], "datetime"):
        df = klines.to_dataframe()
        
        trading_date = bases.get_market_day(klines[-1]["datetime"])
        if trading_date != cur_trading_date:
            cur_trading_date = trading_date
            day_open = klines[-1]["open"]

        df["time"] = df.datetime.apply(lambda x: bases.get_kline_time(x))
        df["date"] = df.datetime.apply(lambda x: bases.get_market_day(x))  
        df = df[(df["date"] == cur_trading_date)]

        df = df.assign(vwap = ((df["volume"]*df["close"]).cumsum() / df["volume"].cumsum()).ffill())

        close_low_index, close_low = min(enumerate(df["close"]), key=operator.itemgetter(1))
        close_high_index, close_high = max(enumerate(df["close"]), key=operator.itemgetter(1))
        if len(df) < 35:
            continue

        now = datetime.datetime.strptime(quote["datetime"], "%Y-%m-%d %H:%M:%S.%f")  # 当前quote的时间
        curTime = now
        curHour = now.hour
        curMinute = now.minute
        #分时之上平多单
        if current_volume > 0 and df_zz["close"].iloc[-1] > df_zz["vwap"].iloc[-1] *1.004:
            current_volume = 0
            target_pos.set_target_volume(0) 
            sum_profit += df_zz["close"].iloc[-1] - long_price
            logger.info("pinduodan at price: %f, total profit: %f" % (df_zz["close"].iloc[-1], sum_profit))    
        # 分时之下平空单
        elif current_volume < 0 and df_zz["close"].iloc[-1] < df_zz["vwap"].iloc[-1] *0.996:
            current_volume = 0
            target_pos.set_target_volume(0)
            sum_profit += short_price - df_zz["close"].iloc[-1]
            logger.info("pingkongdan at price: %f, total profit: %f" % (df_zz["close"].iloc[-1], sum_profit))
        else: # 判断多背离滞涨空背离止跌： 30min + 全背离
            if current_volume != 0 and int(curHour)==14 and int(curMinute)>40:# 14:40之后强制平仓
                if current_volume > 0:
                    sum_profit += df_zz["close"].iloc[-1] - long_price
                else:
                    sum_profit += short_price - df_zz["close"].iloc[-1]
                current_volume = 0
                target_pos.set_target_volume(0)
                logger.info("qiangzhipingcang at price: %f, total profit: %f" % (df_zz["close"].iloc[-1], sum_profit))

            if int(curHour) == 14 and int(curMinute) > 10 : # 14:10之后不开仓
                continue

            df_zz = df[close_high_index:len(df)]
            df_zd = df[close_low_index:len(df)]
            if current_volume == 0 and len(df) - close_high_index >= 30 and (df_zz["close"]>df_zz["vwap"]).all() \
                and close_high > df_zz["vwap"].iloc[0] *1.01:
                logger.info("duobeili, short with price: %f at %s" % (df_zz["close"].iloc[-1], now))
                short_price = df_zz["close"].iloc[-1]
                current_volume = -1*TARGET_VOLUME
                target_pos.set_target_volume(current_volume)
            elif current_volume == 0 and len(df) - close_low_index >= 30 and (df_zd["close"]<df_zd["vwap"]).all() \
                and close_low < df_zd["vwap"].iloc[0] *0.996:
                logger.info("kongbeili, long with price: %f at %s" % (df_zz["close"].iloc[-1], now))
                long_price = df_zz["close"].iloc[-1]
                current_volume = TARGET_VOLUME
                target_pos.set_target_volume(current_volume)

api.close()
logger.removeHandler(fh)