#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'Golden'

'''
主多品种策略函数：步步高，弩末，追阳
实测和效果见策略执行文件
'''
import talib

#步步高策略：返回近期一波多的收新高阳线
def get_index_m(quote, klines):
    m = 0
    k_high = 0

    df = klines.to_dataframe()
    if len(df) <20:
        return m
    #logger.info("klines.high: %f, klines.close: %f" % (klines.high[-1], klines.close[-1]))
    #STEP1：遍历找出最后一波多的收新高阳线日
    ma5 = talib.MA(df.close, timeperiod=5) 
    ma10 =  talib.MA(df.close, timeperiod=10)
    for i in range(9, 20): #只看最近的一波多，前面数据用于计算MA
        pre3HH =  max(klines.high[i-3:i])  # 前3日最高价
        if klines.close[i] > pre3HH and klines.close[i]>klines.open[i] and klines.close[i] > ma5[i]*1.015 and klines.close[i] > ma10[i]*1.015:
            #logger.info("ma5: %f, ma10: %f, df.close: %f, pre3HH:%f" % (ma5[i], ma10[i], df.close[i], pre3HH))
            m = i
            k_high = klines.close[i]
    

    # STEP2：判断最近4~8日偏多调整，另外趋多日必定收在5日线上，用以确定步步高信号
    # n-m=6就是5日偏多调整后的主多，首选它，当然亦可n-m=5就开始考虑，但当心是高位滞涨后的空
    # 判断n-m>=5， <= 9即可 
    if (m > 10 and m <= 15) and (klines.close[m+1:20]>=ma10[m+1:20]).all() and klines.close[-1] >= ma5[len(df)-1]: #8,7,5日偏多调整
        #logger.info("ma5: %f, ma10: %f, df.close: %f" % (ma5[len(df)-1], ma10[len(df)-1], df.close[i]))
        return m, k_high
    else: 
        return 0, 0