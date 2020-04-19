#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'Golden'

'''
日内交易信号 - 开盘即有日内低点的强支撑位主多模型
1. 适用于
   1.1 主多品种的趋多日主多（标准步步高，弩末等）
   1.2 偏多震荡品种，一波空止跌后弩末趋多
   1.3 主多品种低开触及支撑位，或一波急空背离后局部止跌反抽主多
2. 如果自己对趋多把握大，该策略意义不大；但亦可用于抓自己把握不大相对低位追涨机会

信号提醒：
1. 参与时机和点位： 开盘即可多，或者等待盘中局部调整受支撑后再相对低位追多
2. 止盈：中大多背离滞涨止盈，小多背离局部止盈等待再次多机会

风险控制：
1. 先大多背离滞涨止盈；后续视品种情况而定：强主多品种相对低位可再做多；偏多品种则日内禁止再做多
2. 不做空，可追多 - 风险较小

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
parser.add_argument('--ZHICHENG')
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

if args.ZHICHENG != None:
    ZHICHENG = float(args.ZHICHENG)
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

long_price_30mins = 0.0
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

            #低点只在开盘半小时出现，策略负责发现盘中的相对低位做多机会
            # 无先大多背离 + 接近分时或低于分时止跌开多
            if len(df) > 30 and (close_high < df["open"].iloc[0]*1.02 and close_high < df_zz["vwap"].iloc[0]*1.015):
                #df_20mins = df[len(df) - 20 :len(df)]
                df_30mins = df[len(df) - 30 :len(df)]

                close_low_index_30mins, close_low_30mins = min(enumerate(df_30mins["close"]), key=operator.itemgetter(1))
                close_high_index_30mins, close_high_30mins = max(enumerate(df_30mins["close"]), key=operator.itemgetter(1))

                #最近半小时偏多走稳则追多,考虑分时计算误差;每隔10分钟报一次做多信号
                if (df_30mins['close'] > df_30mins['vwap']*0.998).all() and (df_30mins['close'] < df_30mins['vwap']*1.02).all() \
                    and len(df) - close_high_index == 40:
                    logger.info("ZHUDUO_PIANDUO_ZOUWEN_30MINS_LONG above price: %f at %s" % (df_30mins['vwap'].iloc[-1], now))
                    if long_price_30mins == 0:
                        long_price_30mins = df["close"].iloc[-1]
                #小低背离止跌后做多
                if (df_30mins['close'] < df_30mins['vwap']*1.002).all() and df_30mins['close'].iloc[0] <= close_low_30mins \
                    and (len(df) - close_low_30mins)%10 == 0:
                    logger.info("ZHUDUO_XIAODI_ZHIDIE_30MINS_LONG with price: %f at %s" % (df_30mins['close'].iloc[-1], now))
                    if long_price_30mins == 0:
                        long_price_30mins = df["close"].iloc[-1]

            # 止盈和风控
            if (df_zz["close"] > df_zz["vwap"]).all() and close_high > df_zz["vwap"].iloc[0] *1.01:
                #大多高位滞涨,禁止追多
                if len(df) - close_high_index == 30:
                    if close_high > df["open"].iloc[0]*1.015 and (df_zz["close"] > df_zz["vwap"]).all()*1.008:
                        logger.info("XIAN_DADUO_ZHIZHANG_30mins at %s, JINZHI_ZHUIDUO or CHAODUANKONG" % (now))
                    else:
                        logger.info("DUO_ZHIZHANG_30mins at %s, ZHIYING and jinshen wait next good long signal" % (now))
                    if long_price_30mins != 0:
                        sum_profit += df["close"].iloc[-1] - long_price_30mins
                        long_price_30mins = 0.0
                elif len(df) - close_high_index == 20:
                    if close_high > df["open"].iloc[0]*1.015 and (df_zz["close"] > df_zz["vwap"]).all()*1.008:
                        logger.info("XIAN_DADUO_ZHIZHANG_30mins at %s, JINZHI_ZHUIDUO or CHAODUANKONG" % (now))
                    else:
                        logger.info("DUO_ZHIZHANG_30mins at %s, ZHIYING and jinshen wait next good long signal" % (now))
                    #if long_price_30mins != 0:
                    #    sum_profit += df["close"].iloc[-1] - long_price_30mins
                    #    long_price_30mins = 0.0

        if int(curHour) == 14 and int(curMinute) == 45:
            # 强制平仓，并统计利润
            if long_price_30mins != 0:
                sum_profit += df["close"].iloc[-1] - long_price_30mins
                long_price_30mins = 0.0
            logger.info("######LONG profit at %s is %f." % (now, sum_profit))


api.close()
logger.removeHandler(fh)