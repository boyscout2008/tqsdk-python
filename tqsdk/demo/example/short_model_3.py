#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'Golden'

'''
日内交易信号 - 承压做空模型
1. 震荡趋势多中大背离或明确滞涨后阻力位做空 （0+- 0- 0|0-）
   一波多 + 明确滞涨或单日滞涨  + 当日收阳 + 次日先或中高背离滞涨后开空
2. 偏空趋势或主空趋势（佛回头，下地狱，双鬼等），承压5，10日线做空
有三种模型：
1. XIAN_XIANGDUIGAO_ZHENDANG_18MINS_SHORT - 适用于已背离结算价和接近阻力位 + 明确滞涨 + 次日高位震荡局部滞涨后开空
2. XIAN_XIAODUOorGAO_ZHIZHANG_SHORT - k线无大背离5均线，距离阻力位有小空间或无背离结算价，需要冲高确认阻力（适用于偏多品种及第一波多）
3. ZHENDANG_KONG_ZHIZHANG_18MINS_SHORT - 开盘20分钟内就有日内高点，全天主空，适用于偏空趋势，或蓄势不足多背离和非主多高开品种等

信号提醒及风险控制：
1. 参与时机和点位： 无先空背离 + 盘中相对高位滞涨或偏空震荡 + 阻力位 + 开盘价 + 昨日收盘和结算综合考虑
2. 止盈：中大空背离止跌坚定止盈，或者大背离分时止盈
3. 风险控制和禁忌：先空背离止跌日内禁止做空，偏多品种和需要确认冲高背离结算价确认阻力的禁止追空。

实盘验证：
'''

#TODOs:
# 1. 区分三种做空形态，给不同的偏向的品种监控不同的做空信号，避免混淆
# 2. 抓住一些非强多高开和日内先多假突破多背离后的空机会
# 3. 策略更完善，有微信通知，程序活动监控和异常重启等功能。
# 4. 以后每天的操作至少介入时机和点位必须通过量化策略来规范。

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

logger.info("start zhendang_short_model_3 daily strategy for %s!"%(SYMBOL))

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

        logger.info("CURRENT PRICES:  close = %f, vwap = %f, day_open = %f at %s!" % (df["close"].iloc[-1], df["vwap"].iloc[-1], df["open"].iloc[0], now))


        if not (int(curHour) > 13 and int(curHour) < 15):# 先或中, 不参与14：00之后尾盘行情
            df_zz = df[close_high_index:len(df)]
            df_zd = df[close_low_index:len(df)]

            #形态1：开盘即在阻力位和中等以上背离昨日结算价的震荡做空
            # 形态1.1：但先相对高后的空
            #算法：无先空 + 接近阻力位 + 相对高位震荡或偏空震荡则日内高于分时开空 （一般是开盘，可能在盘中出现）
            if close_low > df["open"].iloc[0]*0.985 and (close_high > YALIWEI*0.992 or close_high > df["open"].iloc[0])\
                and (df_zz["close"]>df_zz["vwap"]*0.995).all() and close_high > df_zz["vwap"].iloc[0] *1.002:
                if len(df) - close_high_index == 30: # 先强阻力位日内相对高位震荡 + 明确滞涨，挂分时之上价格做空
                    current_volume += -1*TARGET_VOLUME
                    traded_volume += TARGET_VOLUME
                    #target_pos.set_target_volume(current_volume)
                    logger.info("XIAN_XIANGDUIGAO_ZHENDANG_ZHIZHANG_SHORT above price: %f at %s" % (df["close"].iloc[-1], now))
                elif len(df) - close_high_index == 18: # 相对高位震荡 + 局部滞涨
                    current_volume += -1*TARGET_VOLUME
                    traded_volume += TARGET_VOLUME
                    #target_pos.set_target_volume(current_volume)
                    logger.info("XIAN_XIANGDUIGAO_ZHENDANG_18MINS_SHORT above price: %f at %s" % (df["close"].iloc[-1], now))
                elif 0: #len(df) - close_high_index == 3 and len(df) > 60: # 偏空震荡过分时即开空，见形态1.2
                    current_volume += -1*TARGET_VOLUME
                    traded_volume += TARGET_VOLUME
                    #target_pos.set_target_volume(current_volume)
                    logger.info("XIAN_PIANKONG_ZHENDANG_3MINS_SHORT above price: %f at %s" % (df["close"].iloc[-1], now))
            # 形态1.2：震荡做空，高点只在开盘半小时内出现，之后再无新高点 除了开盘直接开空外，策略只负责发现盘中相对高点做空机会
            # 无先大空 + 接近阻力位 + 高于分时开空
            if len(df) > 20 and close_low > df["open"].iloc[0]*0.985 and (close_high > YALIWEI*0.992 or close_high > df["open"].iloc[0]):
                #close_low_index_20min, close_low_20min = min(enumerate(df["close"][20:]), key=operator.itemgetter(1))
                close_high_index_20min, close_high_20min = max(enumerate(df["close"][20:]), key=operator.itemgetter(1))
                df_20min_hou_zz = df[close_high_index_20min+20:len(df)]
                if (df_20min_hou_zz["close"]>df_20min_hou_zz["vwap"]*0.995).all() and close_high_20min > df_20min_hou_zz["vwap"].iloc[0]:
                    if len(df) - close_high_index_20min - 20 == 18 and close_high_20min < close_high:
                        logger.info("ZHENDANG_KONG_ZHIZHANG_18MINS_SHORT above price: %f at %s" % (df["close"].iloc[-1], now))
                    elif len(df) - close_high_index_20min - 20 == 30 and close_high_20min < close_high:
                        logger.info("ZHENDANG_KONG_ZHIZHANG_30MINS_SHORT above price: %f at %s" % (df["close"].iloc[-1], now))

            #形态2：距离阻力位有小空间，昨日收阳但无背离结算价，当日需先高或小多滞涨才好空
            #算法：无先空 + 接近阻力位 + 小背离分时（先或中出现）
            if close_low > df["open"].iloc[0]*0.985 and (close_high > YALIWEI*0.992 or close_high > df["open"].iloc[0]) \
                and (df_zz["close"]>df_zz["vwap"]).all() and close_high > df_zz["vwap"].iloc[0] *1.005:
                if len(df) - close_high_index == 30: # 先强阻力位日内相对高位震荡 + 明确滞涨，挂分时之上价格做空
                    current_volume += -1*TARGET_VOLUME
                    traded_volume += TARGET_VOLUME
                    #target_pos.set_target_volume(current_volume)
                    logger.info("XIAN_XIAODUOorGAO_ZHIZHANG_SHORT above price: %f at %s" % (df["close"].iloc[-1], now))
                elif len(df) - close_high_index == 18: # 相对高位震荡 + 局部滞涨
                    current_volume += -1*TARGET_VOLUME
                    traded_volume += TARGET_VOLUME
                    #target_pos.set_target_volume(current_volume)
                    logger.info("XIAN_XIANGDUOorGAO_ZHENDANG_18MINS_SHORT above price: %f at %s" % (df["close"].iloc[-1], now))
                elif len(df) - close_high_index == 3 and len(df) > 60: # 震荡挂小多位开空
                    current_volume += -1*TARGET_VOLUME
                    traded_volume += TARGET_VOLUME
                    #target_pos.set_target_volume(current_volume)
                    logger.info("XIAN_XIAODUO_ZHENDANG_3MINS_SHORT above price: %f at %s" % (df_zz["vwap"].iloc[0] *1.008, now))

            # 止盈和风控
            if (df_zd["close"]<df_zd["vwap"]).all() and close_low < df_zd["vwap"].iloc[0] *0.996:
                #先空,禁止做空
                if len(df) - close_low_index == 30:
                    if (close_high < YALIWEI*0.995 or close_high < df["open"].iloc[0]) and close_low < df["open"].iloc[0]*0.985:
                        logger.info("XIAN_KONG_ZHIDIE_30mins at %s, JINZHI_zuokong or CHAODUANDUO" % (now))
                    else:
                        logger.info("KONGBEILI_ZHIDIE_30mins at %s, ZHIYING" % (now))
                    #logger.info("%f, %f" % (YALIWEI, close_high))
                elif len(df) - close_low_index == 20:
                    if (close_high < YALIWEI*0.995 or close_high < df["open"].iloc[0]) and close_low < df["open"].iloc[0]*0.985:
                        logger.info("XIAN_KONG_ZHIDIE_20mins at %s, JINZHI_zuokong or CHAODUANDUO" % (now))
                    else:
                        logger.info("KONGBEILI_ZHIDIE_20mins at %s, ZHIYING" % (now))


api.close()
logger.removeHandler(fh)