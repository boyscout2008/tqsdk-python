#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'Golden'

'''
日内做多交易信号 - 开盘即直接震荡小低或小空触及强支撑位主多模型
1. 适用于
   1.1 主多或偏多品种的多趋势：一波多未大背离和滞涨 + （收阴或主多中） + 接近支撑位 + 次日先小低或小空触及支撑位止跌做多
   1.2 非偏空震荡品种一波蓄势不足的空背离后，次日先相对低位走稳做多
2. 这里只捕捉先低做多信号，偏多走稳的追多信号请配合long_model_zhuduo.py使用

信号提醒：
1. 参与时机和点位： 长期相对低位止跌 + 分时之下小低或小空做多；或者开盘小空触及支撑做多
2. 止盈：中大多背离滞涨止盈，小多背离局部止盈等待再次多机会

风险控制：
1. 先大多背离滞涨止盈；后续视品种情况而定：偏多品种偏多调整走稳后可再做多
2. 不做空，谨慎追多

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
import winsound

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
parser.add_argument('--ZHICHENG')
parser.add_argument('--LAST_CLOSE')
parser.add_argument('--LAST_SETTLEMENT')

args = parser.parse_args()

if args.SYMBOL != None:
    SYMBOL = args.SYMBOL
else:
    SYMBOL = "DCE.i2009"

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

logger.info("start %s daily strategy for %s!"%(c, SYMBOL))

current_volume = 0  # 记录持仓量
traded_volume = 0
cur_trading_date = ''

# 交易预警参数
k_count = 0
signal_interval = 10

short_price = 0.0
sum_profit = 0.0
last_kong_index = 0
kaipan_di = False

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

        logger.info("CURRENT PRICES:  close = %f, vwap = %f, day_open = %f at %s!" % (df["close"].iloc[-1], df["vwap"].iloc[-1], df["open"].iloc[0], now))


        if not (int(curHour) > 11 and int(curHour) < 15):# 先或中低, 不涉及13：00之后的空转多行情
            df_zz = df[close_high_index:len(df)]
            df_zd = df[close_low_index:len(df)]

            # 开盘半小时小空小背离触及支撑做多
            if len(df) <= 30 and close_low < df["open"].iloc[0]*0.992 and close_low < df_zd["vwap"].iloc[0]*0.997 and not kaipan_di:
                kaipan_di = True
                logger.info("KAIPAN_XIAOKONG_ZHICHENG_LONG below price: %f at %s, or wait 10mins after zhan shang fenshi" % (close_low, now))
                    winsound.PlaySound('p2.wav', winsound.SND_FILENAME)

            # 长期低于分时但无新低：则分时之下小低或小空局部止跌做多
            # 无先多背离 + 接近分时或低于分时止跌开多
            if len(df) > 30 and (close_high < df["open"].iloc[0]*1.01 and close_high < df_zz["vwap"].iloc[0]*1.01):
                df_30mins = df[len(df) - 30 :len(df)]

                close_low_index_30mins, close_low_30mins = min(enumerate(df_30mins["close"]), key=operator.itemgetter(1))
                close_high_index_30mins, close_high_30mins = max(enumerate(df_30mins["close"]), key=operator.itemgetter(1))

                #低点低于开盘价 + 最近半小时小低止跌, 每隔10分钟报一次低多信号
                if close_low < df["close"].iloc[0]  and (df_30mins['close'] < df_30mins['vwap']*1.002).all() \
                    and (len(df) - close_low_30mins)%10 == 0:
                    logger.info("XIAN_XIAODI_ZHIDIE_30MINS_LONG below price: %f at %s" % (df['vwap'].iloc[-1], now))
                    winsound.PlaySound('p2.wav', winsound.SND_FILENAME)

            # 止盈和风控
            if (df_zd["close"] > df_zd["vwap"]*1.006).all() and close_high > df_zz["vwap"].iloc[0] *1.015:
                #先大多高位滞涨,禁止追多
                if len(df) - close_high_index == 30:
                     logger.info("DA_DUO_ZHIZHANG_30mins at %s, ZHIYING and wait next good long signal" % (now))

                elif len(df) - close_low_index == 20:
                    logger.info("DA_DUO_ZHIZHANG_20mins at %s, ZHIYING and wait next good long signal" % (now))
            elif (df_zd["close"] > df_zd["vwap"]).all() and close_high > df_zz["vwap"].iloc[0] *1.01:
                #先小多滞涨,局部止盈
                if len(df) - close_high_index == 30:
                     logger.info("XIAO_DUO_ZHIZHANG_30mins at %s, JUBU_ZHIYING and wait next long signal" % (now))


api.close()
logger.removeHandler(fh)