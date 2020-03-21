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

#双鬼拍门：分析当前3根k线是否符合双鬼形态
#形态1:未破位偏空蓄势期承压10日线，或主空反弹期期
#形态2：主空未止跌承压5日线
def parse_klines_sg(quote, klines, logger):

    df = klines.to_dataframe()
    if len(df) <20:
        return False
    #logger.info("klines.low: %f, klines.close: %f" % (klines.low[-1], klines.close[-1]))
    ma5 = talib.MA(df.close, timeperiod=5) 
    ma10 =  talib.MA(df.close, timeperiod=10)

    #STEP1：判断3根k线
    # 倒数第三根是小背离5，10日线的阴线，倒是第二根和第三根是阳线
    if klines.open[-3] > klines.close[-3] and klines.close[-3] < ma10[17]*0.985 and klines.close[-3] < ma10[17]*0.99 \
        and klines.close[-2] > klines.open[-2] and klines.close[-1] >  klines.open[-1]:
        #倒数第二根和第一根是承压10日线，最后一根最高价要高于5日线，接近10日线
        if klines.high[-1] > ma5[19] and  klines.high[-1] >  ma10[19]*0.985 \
            and klines.close[-1] < ma10[19] and klines.close[-2] < ma10[18]:
            #logger.info("close: %f, ma10: %f"%(klines[-1]["close"],ma10[19]))
            return True
        #未止跌 + 倒数第二根和第一根是承压5日线小阳线 + 最后一根最高价要接近5日线
        if klines.close[-3] < klines.low[-4] \
            and klines.close[-1] < ma5[19] and  klines.close[-2] < ma5[18] \
            and klines.high[-1] >  ma5[5]*0.99:
            return True
    return False