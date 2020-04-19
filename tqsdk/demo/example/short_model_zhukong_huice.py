#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'Golden'

'''
日内交易信号 - 开盘即有日内高位的主空模型
1. 适用于
   1.1 偏多品种一波多未明确滞涨时的高开或主多拔高滞涨后开空
   1.2 偏多品种一波蓄势不足的多背离后次日主空
   1.3 偏空品种趋空日做空（标准佛回头，下地狱等）

信号提醒：
1. 参与时机和点位： 开盘即可空，这里主要提醒盘中反复的相对高空机会
2. 止盈：中大空背离止跌局部止盈，或者大背离分时局部止盈；等待反弹承压后再做空

风险控制：
1. 先空背离止跌日内禁止做空
2. 不做多，可追空 - 风险较小

回测验证：
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
parser.add_argument('--YEAR')
parser.add_argument('--MONTH')
parser.add_argument('--DAY')
parser.add_argument('--YALIWEI')
parser.add_argument('--LAST_CLOSE')
parser.add_argument('--LAST_SETTLEMENT')

args = parser.parse_args()

if args.SYMBOL != None:
    SYMBOL = args.SYMBOL
else:
    SYMBOL = "DCE.i2005"

if args.YEAR != None:
    YEAR = int(args.YEAR)
else:
    exit(-1)

if args.MONTH != None:
    MONTH = int(args.MONTH)
else:
    exit(-1)

if args.DAY != None:
    DAY = int(args.DAY)
else:
    exit(-1)

if args.YALIWEI != None:
    YALIWEI = float(args.YALIWEI)
else:
    exit(-1)

if args.LAST_CLOSE != None:
    LAST_CLOSE = float(args.LAST_CLOSE)
else:
    LAST_CLOSE = 0

if args.LAST_SETTLEMENT != None:
    LAST_SETTLEMENT = float(args.LAST_SETTLEMENT)
else:
    LAST_SETTLEMENT = 0

a = __file__
c = os.path.basename(a) #获取文件名称

# 第二步，创建日志文件和控制台两个handler
log_path = 'E://proj-futures/logs_debug/'
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

api = TqApi(TqSim(), backtest=TqBacktest(start_dt=date(YEAR, MONTH, DAY), end_dt=date(YEAR, MONTH, DAY)))


logger.info("start %s daily strategy for %s in %d.%d.%d!"%(c, SYMBOL, YEAR, MONTH, DAY))

#time_slot_start = datetime.time(START_HOUR, START_MINUTE)  # 计划交易时段起始时间点
#time_slot_end = datetime.time(END_HOUR, END_MINUTE)  # 计划交易时段终点时间点
klines = api.get_kline_serial(SYMBOL, TIME_CELL, data_length=int(10 * 60 * 60 / TIME_CELL))
target_pos = TargetPosTask(api, SYMBOL)
position = api.get_position(SYMBOL)  # 持仓信息
quote = api.get_quote(SYMBOL)


current_volume = 0  # 记录持仓量
cur_trading_date = ''
traded_volume = 0

# 交易预警参数
k_count = 0
signal_interval = 10

# 盈利亏损统计
short_price_18mins = 0.0
short_price_30mins = 0.0
sum_profit = 0.0

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

        if not (int(curHour) > 13 and int(curHour) < 15):# 先或中, 不参与14：00之后尾盘行情
            df_zz = df[close_high_index:len(df)]
            df_zd = df[close_low_index:len(df)]

            # 形态1.2：震荡做空，高点只在开盘半小时内出现，之后再无新高点 除了开盘直接开空外，策略只负责发现盘中相对高点做空机会
            # 无先大空 + 接近阻力位 + 高于分时开空
            if len(df) > 20 and close_low > df["open"].iloc[0]*0.98 and (close_high > YALIWEI*0.992 or close_high > df["open"].iloc[0]):
                #close_low_index_20min, close_low_20min = min(enumerate(df["close"][20:]), key=operator.itemgetter(1))
                close_high_index_2, close_high_2 = max(enumerate(df["close"][close_low_index:len(df)]), key=operator.itemgetter(1))
                df_jubu_zz = df[close_high_index_2+close_low_index:len(df)]
                if (df_jubu_zz["close"]>df_jubu_zz["vwap"]*0.996).all() and close_high_2 > df_jubu_zz["vwap"].iloc[0]*0.998:
                    if len(df) - close_high_index_2 - close_low_index == 18:
                        logger.info("ZHUKONG_ZHIZHANG_18MINS_SHORT above price: %f at %s" % (df["close"].iloc[-1], now))
                        if short_price_18mins == 0:
                            short_price_18mins = df["close"].iloc[-1]
                    elif len(df) - close_high_index_2 - close_low_index == 30:
                        logger.info("ZHUKONG_ZHIZHANG_30MINS_SHORT above price: %f at %s" % (df["close"].iloc[-1], now))
                        if short_price_30mins == 0:
                            short_price_30mins = df["close"].iloc[-1]


            # 止盈和风控
            if (df_zd["close"]<df_zd["vwap"]).all() and close_low < df_zd["vwap"].iloc[0] *0.996:
                #先空,禁止做空
                if len(df) - close_low_index == 30:
                    if (close_high < YALIWEI*0.995 or close_high < df["open"].iloc[0]) and close_low < df["open"].iloc[0]*0.985:
                        logger.info("XIAN_KONG_ZHIDIE_30mins at %s, ZHIYING, dengdai zaiciKONG signal" % (now))
                    else:
                        logger.info("KONGBEILI_ZHIDIE_30mins at %s, ZHIYING for next short signal" % (now))
                    if short_price_30mins != 0:
                        sum_profit += short_price_30mins - df["close"].iloc[-1]
                        short_price_30mins = 0.0
                    #logger.info("%f, %f" % (YALIWEI, close_high))
                elif len(df) - close_low_index == 20:
                    if (close_high < YALIWEI*0.995 or close_high < df["open"].iloc[0]) and close_low < df["open"].iloc[0]*0.985:
                        logger.info("XIAN_KONG_ZHIDIE_20mins at %s, ZHIYING, dengdai zaiciKONG signal" % (now))
                    else:
                        logger.info("KONGBEILI_ZHIDIE_20mins at %s, ZHIYING for next short signal" % (now))
                    if short_price_18mins != 0:
                        sum_profit += short_price_18mins - df["close"].iloc[-1]
                        short_price_18mins = 0.0

        if int(curHour) == 14 and int(curMinute) == 45:
            # 强制平仓，并统计利润
            if short_price_30mins != 0:
                sum_profit += short_price_30mins - df["close"].iloc[-1]
                short_price_30mins = 0.0
            if short_price_18mins != 0:
                sum_profit += short_price_18mins - df["close"].iloc[-1]
                short_price_18mins = 0.0
            logger.info("SHORT profit at %s is %f." % (now, sum_profit))


api.close()
logger.removeHandler(fh)