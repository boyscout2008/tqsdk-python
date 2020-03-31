#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'Golden'

'''
日内交易信号 - 多背离滞涨开空，空背离止跌开多
1. 第一个日内交易策略，建立实盘和回测代码框架

算法逻辑：

回测小结：
'''

import datetime
from tqsdk import TqApi, TargetPosTask
import bases

TIME_CELL = 60  # 等时长下单的时间单元, 单位: 秒
TARGET_VOLUME = 5  # 目标交易手数 (>0: 多头, <0: 空头)

#START_HOUR, START_MINUTE = 21, 0  # 计划交易时段起始时间点
#END_HOUR, END_MINUTE = 15, 0  # 计划交易时段终点时间点

parser = argparse.ArgumentParser()
parser.add_argument('--SYMBOL')
args = parser.parse_args()

if args.SYMBOL != None:
    SYMBOL = args.SYMBOL
else:
    SYMBOL = "DCE.i2005"


api = TqApi()
print("start beili_zz_zd daily strategy!")

#time_slot_start = datetime.time(START_HOUR, START_MINUTE)  # 计划交易时段起始时间点
#time_slot_end = datetime.time(END_HOUR, END_MINUTE)  # 计划交易时段终点时间点
klines = api.get_kline_serial(SYMBOL, TIME_CELL, data_length=int(10 * 60 * 60 / TIME_CELL))
target_pos = TargetPosTask(api, SYMBOL)
position = api.get_position(SYMBOL)  # 持仓信息


# 添加辅助列: time及date, 分别为K线时间的时:分:秒和其所属的交易日
klines["time"] = klines.datetime.apply(lambda x: bases.get_kline_time(x))
klines["date"] = klines.datetime.apply(lambda x: bases.get_market_day(x))
cur_trading_date = klines["date"][-1]

# 获取在预设交易时间段内的所有K线, 即时间位于 time_slot_start 到 time_slot_end 之间的数据
#if time_slot_end > time_slot_start:  # 判断是否类似 23:00:00 开始， 01:00:00 结束这样跨天的情况
#    klines = klines[(klines["time"] >= time_slot_start) & (klines["time"] <= time_slot_end)]
#else:
#    klines = klines[(klines["time"] >= time_slot_start) | (klines["time"] <= time_slot_end)]

klines = klines[klines["date"] == cur_trading_date]
klines["vwap"] = klines.apply(lambda x: x["close"]*x["volume"]/len(x))
#相同的数组，返回的时间索引应该是最早的那个吧？？？
close_low_time, close_low = min(enumerate(klines), key=operator.itemgetter(1))
close_high_time, close_high = max(enumerate(klines), key=operator.itemgetter(1))



# 交易

current_volume = 0  # 记录持仓量
while True:
    api.wait_update()
    # 新产生一根K线计算分时均价，判断滞涨止跌信号

    if api.is_changing(klines.iloc[-1], "datetime"):
        trading_date = bases.get_market_day(klines[-1]["datetime"])
        if trading_date != cur_trading_date:
            cur_trading_date = trading_date
            klines = klines[klines["date"] == cur_trading_date]

        klines["time"] = klines.datetime.apply(lambda x: bases.get_kline_time(x))
        klines["date"] = klines.datetime.apply(lambda x: bases.get_market_day(x))           
        klines["vwap"] = klines.apply(lambda x: x["close"]*x["volume"]/len(x))
        close_low_time, close_low = min(enumerate(klines), key=operator.itemgetter(1))
        close_high_time, close_high = max(enumerate(klines), key=operator.itemgetter(1))
        
        if len(klines) < 35:
            continue

        #判断是否滞涨：最高点至今已有30mins + 最近30分钟收盘都高于且背离分时
        klines_zz = klines[klines["time"] >= close_high_time]
        if klines["time"] - close_high_time >= 30 and (klines_zz["close"]>klines["vwap"]).all() \
            and close_high > klines[klines["time"] == cur_trading_date]["close"] *1.01:
            print("多背离滞涨，开空: %d" % TARGET_VOLUME)
            current_volume = -1*TARGET_VOLUME；
            target_pos.set_target_volume(current_volume)

        #判断是否止跌：最低点至今已有30mins + 最近30分钟收盘都低于且背离分时

api.close()