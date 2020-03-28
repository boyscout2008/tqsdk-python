#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'Golden'

'''
震荡品种策略函数：两波多后的大空，一波两浪多后的空
实测和效果见策略执行文件
'''
import talib


#两波多后的空策略
def dual_bo_duo(quote, klines, logger):
    m = 0
    k_high = 0.0
    k_highest = 0.0

    df = klines.to_dataframe()
    if len(df) < 20:
        return m
    #logger.info("klines.high: %f, klines.close: %f" % (klines.high[-1], klines.close[-1]))
    ma5 = talib.MA(df.close, timeperiod=5) 
    ma10 =  talib.MA(df.close, timeperiod=10)

    #STEP1： 明确当前一波收新高多中 --- 收阳收新高
    if klines.close[-1] > max(klines.high[-9:-1]) and klines.close[-1] > klines.open[-1]:
        #STEP2：找出这波多之前是否存在另一波多 --- 至少前1(主多)+4（调整）站稳在10日之上 + 5日线高于10日线 + 之前有背离5日线的阳线
        if (klines.close[14:20] > ma10[14:20]).all() and (ma10[16:20] < ma5[16:20]).all() and (klines.close[0:15] > ma5[0:15]*1.02).any():
            return True

    return False