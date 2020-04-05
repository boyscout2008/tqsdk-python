#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'Golden'

'''
日内交易信号 - 偏空震荡，主空趋势承压10日线做空模型2 （0-|1- 0- 0-）
1. 当前偏空震荡（连续承压10日线） + 日内中大阳反弹（双鬼拍门或一大阳承压）+ 明确阻力位 + 次日开盘高偏离结算价且继续承压10日线
2. 几种形态：2020.4.2这种收盘大背离结算价的；或者未大背离结算价
2.1 大背离结算价的模型较为简单，不需要择机高空了，开盘即可空，主要关注止盈和再开空 --- KAIPANGAO_SHORT
2.2 小背离或未背离结算价的，则要结合开盘价，分时，近两日高点和10日线压力位开空 --- PANZHONGGAO_SHORT

信号提醒及风险控制：
1. 参与时机和点位： 早盘或盘中，10日线压力位 + 开盘价 + 昨日收盘和结算综合考虑
2. 止盈：先或中大空背离止跌要先止盈
3. 风险控制和禁忌：已完成一波两浪空则可能是支撑位止跌期，做空空间要谨慎；全天禁止做多

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

api = TqApi(TqSim())

#time_slot_start = datetime.time(START_HOUR, START_MINUTE)  # 计划交易时段起始时间点
#time_slot_end = datetime.time(END_HOUR, END_MINUTE)  # 计划交易时段终点时间点
klines = api.get_kline_serial(SYMBOL, TIME_CELL, data_length=int(10 * 60 * 60 / TIME_CELL))
target_pos = TargetPosTask(api, SYMBOL)
position = api.get_position(SYMBOL)  # 持仓信息
quote = api.get_quote(SYMBOL)

logger.info("start zhendang_short_model_2 daily strategy for %s!"%(SYMBOL))

current_volume = 0  # 记录持仓量
traded_volume = 0
cur_trading_date = ''
day_open = 0.0

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

        now = datetime.datetime.strptime(quote["datetime"], "%Y-%m-%d %H:%M:%S.%f")  # 当前quote的时间
        curTime = now
        curHour = now.hour
        curMinute = now.minute

        #logger.info("CURRENT PRICES:  close = %f, vwap = %f, day_open = %f at %s!" % (df["close"].iloc[-1], df["vwap"].iloc[-1], df["open"].iloc[0], now))

        close_low_index, close_low = min(enumerate(df["close"]), key=operator.itemgetter(1))
        close_high_index, close_high = max(enumerate(df["close"]), key=operator.itemgetter(1))

        df_zd = df[close_low_index:len(df)]
        # 中大空背离后分时之下止跌平空单
        if len(df) - close_low_index >= 30 and (df_zd["close"]<df_zd["vwap"]).all() \
            and close_low < df_zd["vwap"].iloc[0] *0.99:
            if current_volume < 0:
                logger.info("KONGBEILI_PINCANG with price: %f at %s, zhiying!!!" % (df["close"].iloc[-1], now))
                current_volume  = 0
                target_pos.set_target_volume(0)
            else:
                if traded_volume == 0:
                    logger.info("XIANKONGBEILI at %s, short is forbidden today!" % (now))

        # 高于开盘价，接近阻力位，高于分时开空
        if current_volume == 0 and df["close"].iloc[-1] > df["vwap"].iloc[-1] *1.002 \
            and df["close"].iloc[-1] >=  df["open"].iloc[0] and df["close"].iloc[-1] > LAST_SETTLEMENT*1.006:
            current_volume = -1*TARGET_VOLUME
            traded_volume += TARGET_VOLUME
            target_pos.set_target_volume(current_volume)
            last_kong_index = len(df)
            logger.info("KAIPANGAO_SHORT with price: %f at %s" % (df["close"].iloc[-1], now))

        # 盘中小多或小高再开空
        if  len(df) - last_kong_index > 20 and df["close"].iloc[-1] > df["vwap"].iloc[-1] *1.002 \
            and df["close"].iloc[-1] > LAST_SETTLEMENT*1.003:
            current_volume += -1*TARGET_VOLUME
            traded_volume += TARGET_VOLUME
            target_pos.set_target_volume(current_volume)
            last_kong_index = len(df)
            logger.info("PANZHONGGAO_SHORT with price: %f at %s" %(df["close"].iloc[-1], now))

api.close()
logger.removeHandler(fh)