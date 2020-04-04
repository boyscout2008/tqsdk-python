#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'Golden'

'''
日内交易信号 - 偏空震荡趋势承压做空模型2_1 （0-|1- 0- 0-）
1. 它是模型2的延续，在模型2主空破5日线，但未中大背离之前且距离支撑有空间的情况下的中大空趋势
2  它也有两种形态：先相对高滞涨后转中大空，或者震荡做空 --- PANZHONGGAO_SHORT

信号提醒及风险控制：
1. 参与时机和点位： 无先空背离 + 盘中相对高位滞涨或偏空震荡 + 开盘价 + 昨日收盘和结算综合考虑
2. 止盈：中大空背离止跌坚定止盈，震荡空则中大背离直接止盈或尾盘止盈
3. 风险控制和禁忌：先空背离止跌日内禁止做空

实盘验证：
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
log_path = 'E://proj-futures/logs/'
log_name = log_path + runningDate + '_daily.log'
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
parser.add_argument('--YALIWEI')
parser.add_argument('--LAST_CLOSE')
parser.add_argument('--LAST_SETTLEMENT')

args = parser.parse_args()

if args.SYMBOL != None:
    SYMBOL = args.SYMBOL
else:
    SYMBOL = "DCE.i2009"

if args.YALIWEI != None:
    YALIWEI = float(args.YALIWEI)
else:
    exit(-1)

if args.LAST_CLOSE != None:
    LAST_CLOSE = float(args.LAST_CLOSE)
else:
    exit(-1)

if args.LAST_SETTLEMENT != None:
    LAST_SETTLEMENT = float(args.LAST_SETTLEMENT)
else:
    exit(-1)

api = TqApi(TqSim())

#time_slot_start = datetime.time(START_HOUR, START_MINUTE)  # 计划交易时段起始时间点
#time_slot_end = datetime.time(END_HOUR, END_MINUTE)  # 计划交易时段终点时间点
klines = api.get_kline_serial(SYMBOL, TIME_CELL, data_length=int(10 * 60 * 60 / TIME_CELL))
target_pos = TargetPosTask(api, SYMBOL)
position = api.get_position(SYMBOL)  # 持仓信息
quote = api.get_quote(SYMBOL)

logger.info("start zhendang_short_model_2_1 daily strategy for %s!"%(SYMBOL))

current_volume = 0  # 记录持仓量
traded_volume = 0
cur_trading_date = ''

# 交易预警参数
k_count = 0
signal_interval = 10

short_price = 0.0
sum_profit = 0.0
last_kong_index = 0

while True:
    api.wait_update()
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

        close_low_index, close_low = min(enumerate(df["close"]), key=operator.itemgetter(1))
        close_high_index, close_high = max(enumerate(df["close"]), key=operator.itemgetter(1))

        now = datetime.datetime.strptime(quote["datetime"], "%Y-%m-%d %H:%M:%S.%f")  # 当前quote的时间
        curTime = now
        curHour = now.hour
        curMinute = now.minute

        #logger.info("CURRENT PRICES:  close = %f, vwap = %f, day_open = %f at %s!" % (df["close"].iloc[-1], df["vwap"].iloc[-1], df["open"].iloc[0], now))

        df_zd = df[close_low_index:len(df)]
        if len(df) - close_low_index >= 30 and (df_zd["close"]<df_zd["vwap"]*1.003).all() \
            and close_low < df_zd["vwap"].iloc[0] *0.99 and df["close"].iloc[-1] < df_zd["vwap"].iloc[-1]*0.992 \
            and df["close"].iloc[-1] < df["open"].iloc[0]*0.985:
            # 空背离止跌止盈
            if current_volume < 0:
                logger.info("KONGBEILI_ZHIDIE_PINCANG with price: %f at %s, zhiying!!!" % (df["close"].iloc[-1], now))
                current_volume  = 0
                target_pos.set_target_volume(0)
            else: #先中大空背离开盘价和分时和昨结 + 震荡止跌 - 全天禁止做空
                if traded_volume == 0:
                    logger.info("XIANKONGBEILI at %s, short is forbidden today!" % (now))

        # 形态2：震荡做空
        if traded_volume == 0 and df["close"].iloc[-1] > df_zd["vwap"].iloc[-1] and close_low > df["open"].iloc[0]*0.985:
            current_volume += -1*TARGET_VOLUME
            traded_volume += TARGET_VOLUME
            target_pos.set_target_volume(current_volume)
            last_kong_index = len(df)
            logger.info("ZHENDANGKONG_SHORT with price: %f at %s" % (df["close"].iloc[-1], now))            

        # 空背离止盈局部信号
        k_count += 1
        if df["close"].iloc[-1] < df_zd["vwap"].iloc[-1]*0.99 and df["close"].iloc[-1] < df["open"].iloc[0]*0.985:
            if k_count > signal_interval  and current_volume < 0:
                logger.info("KONGBEILI_4_PINCANG with price: %f at %s!" % (df["close"].iloc[-1], now))
                k_count = 0

        #if traded_volume == 0 and close_low <  LAST_SETTLEMENT*0.98 and close_low < df["vwap"].iloc[-1]:

        # #形态1：先高于分时 + 接近或高于开盘价 + 长期震荡滞涨 --- 开空
        df_zz = df[close_high_index:len(df)]
        if len(df) - last_kong_index > 20 and df["close"].iloc[-1] > df["vwap"].iloc[-1] *1.002 \
            and df["close"].iloc[-1] >= df["open"].iloc[0]*0.992 and (df_zz["close"]>df_zz["vwap"]*0.995).all():
            current_volume += -1*TARGET_VOLUME
            traded_volume += TARGET_VOLUME
            target_pos.set_target_volume(current_volume)
            last_kong_index = len(df)
            logger.info("XIANGAO_SHORT with price: %f at %s" % (df["close"].iloc[-1], now))

        # 空背离止跌全部止盈
        if  len(df) - last_kong_index > 20 and df["close"].iloc[-1] > df["vwap"].iloc[-1] *1.002 \
            and df["close"].iloc[-1] > LAST_SETTLEMENT*1.003:
            current_volume += -1*TARGET_VOLUME
            traded_volume += TARGET_VOLUME
            target_pos.set_target_volume(current_volume)
            last_kong_index = len(df)
            logger.info("PANZHONGGAO_SHORT with price: %f at %s" %(df["close"].iloc[-1], now))


api.close()
logger.removeHandler(fh)