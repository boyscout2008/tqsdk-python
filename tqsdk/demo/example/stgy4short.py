#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'Golden'

'''
常用基本函数和类
'''
import talib

#下地狱：返回近期一波多的收新低阴线
def get_index_m(quote, klines):
    m = 0
    k_low = 0

    df = klines.to_dataframe()
    if len(df) <20:
        return m
    #logger.info("klines.low: %f, klines.close: %f" % (klines.low[-1], klines.close[-1]))
    #STEP1：遍历找出最后一波空的收新低阴线日
    ma5 = talib.MA(df.close, timeperiod=5) 
    ma10 =  talib.MA(df.close, timeperiod=10)
    for i in range(9, 20): #只看最近的一波空，前面数据用于计算MA
        pre3LL =  min(klines.low[i-3:i])  # 前3日最低价
        if klines.close[i] < pre3LL and klines.close[i]<klines.open[i] and klines.close[i] < ma5[i]*0.985 and klines.close[i] < ma10[i]*0.985:
            #logger.info("ma5: %f, ma10: %f, df.close: %f, pre3LL:%f" % (ma5[i], ma10[i], df.close[i], pre3LL))
            m = i
            k_low = klines.close[i]
    

    # STEP2：判断最近4~8日偏空调整，另外趋多日必定收在5日线的阴线，用以确定下地狱信号
    # n-m=6就是5日偏多调整后的主多，首选它，当然亦可n-m=5就开始考虑，但当心是高位滞涨后的空
    # 改进：很多都是不规则第二波空，只要是承压10日线，且是主空或已破位多转空的第二波就可以认为是下地狱
    # 判断n-m>=5， <= 9即可 
    if (m > 10 and m <= 15) and (klines.close[m+1:20]<=ma10[m+1:20]).all(): #and klines.close[-1] <= ma5[len(df)-1]: #8,7,5日偏空调整
        #logger.info("ma5: %f, ma10: %f, df.close: %f" % (ma5[len(df)-1], ma10[len(df)-1], df.close[i]))
        return m, k_low
    else: 
        return 0, 0