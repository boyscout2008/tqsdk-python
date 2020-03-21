#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'Golden'

'''
常用基本函数和类
'''
import time, datetime
from datetime import date

def get_kline_time(kline_datetime):
    """获取k线的时间(不包含日期)"""
    kline_time = datetime.datetime.fromtimestamp(kline_datetime//1000000000).time()  # 每根k线的时间
    return kline_time

def get_market_day(kline_datetime):
    """获取k线所对应的交易日"""
    kline_dt = datetime.datetime.fromtimestamp(kline_datetime//1000000000)  # 每根k线的日期和时间
    if kline_dt.hour >= 18:  # 当天18点以后: 移到下一个交易日
        kline_dt = kline_dt + datetime.timedelta(days=1)
    while kline_dt.weekday() >= 5:  # 是周六或周日,移到周一
        kline_dt = kline_dt + datetime.timedelta(days=1)
    return kline_dt.date()