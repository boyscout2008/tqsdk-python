# 有效回测日期

#先相对高滞涨（当前即使强阻力位，背离昨日结算价，确认滞涨后即可空）
#可以是一波多滞涨后的强阻力位或偏空趋势反弹承压10日线的中阳

# 先小多或相对高（距离阻力位有小空间或未背离昨日结算价，需要有个上冲过程）
#可以是一波多滞涨收阳调整k线或偏空趋势承压5，10日线的双鬼
#偏空品种2波多明确滞涨 + 阳线 --- 接收先相对高做空信号 辅助小多后滞涨和震荡空做空信号 
#/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i1605 --YEAR 2016 --MONTH 1 --DAY 6 --YALIWEI 328
# 1.7佛回头后次日开盘直接空 --- 接受盘中震荡空信号
#/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i1605 --YEAR 2016 --MONTH 1 --DAY 8 --YALIWEI 320
# 已是第三波多进入主多模式 --- 依旧回测2日滞涨 + 中阳震荡模型 --- 接受先相对高或小多局部滞涨做空信号
#/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i1605 --YEAR 2016 --MONTH 2 --DAY 16 --YALIWEI 342
# 主多品种连续大多背离2日滞涨 + 收阳 --- 接受先相对高或小多局部滞涨做空信号
# ***实测第一次接受的相对高信号不可靠，对于偏多或主多品种，只能接受小多局部滞涨做空信号***
#/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i1605 --YEAR 2016 --MONTH 2 --DAY 25 --YALIWEI 376
#/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i1605 --YEAR 2016 --MONTH 3 --DAY 11 --YALIWEI 441
#/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i1609 --YEAR 2016 --MONTH 4 --DAY 26 --YALIWEI 490

#偏空品种第一波多2日阳滞涨 --- 接受先相对高或小多滞涨后做空信号
#/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i1605 --YEAR 2015 --MONTH 9 --DAY 7 --YALIWEI 395

#偏空品种2波蓄势不足的多背离 + 未滞涨做空 --- 接受3种信号
#/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i1601 --YEAR 2015 --MONTH 9 --DAY 17 --YALIWEI 414
#偏空品种蓄势不足两波多 + 单日滞涨 + 高位阴线 --- 接受3种信号
#/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i1601 --YEAR 2015 --MONTH 9 --DAY 17 --YALIWEI 410



#震荡空（开盘20分钟内既有最高价，盘中承压分时主空或震荡做空）
#可以是蓄势不足2波背离多后不滞涨的急空，或者一波多明确滞涨中大阳调整+强阻力位后次日主空；或者趋空日承压主空；或者非强多高开拔高后急空
:<<!
/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i2005 --YEAR 2020 --MONTH 1 --DAY 9 --YALIWEI 685 
/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i2005 --YEAR 2019 --MONTH 12 --DAY 12 --YALIWEI 662 
/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i2005 --YEAR 2019 --MONTH 12 --DAY 16 --YALIWEI 669 
/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i2009 --YEAR 2020 --MONTH 4 --DAY 13 --YALIWEI 609 
/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i2009 --YEAR 2020 --MONTH 4 --DAY 15 --YALIWEI 609 
/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i2001 --YEAR 2019 --MONTH 11 --DAY 20 --YALIWEI 638
/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i2005 --YEAR 2019 --MONTH 12 --DAY 12 --YALIWEI 662
/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i2005 --YEAR 2020 --MONTH 1 --DAY 7 --YALIWEI 670 
/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i1901 --YEAR 2018 --MONTH 8 --DAY 10 --YALIWEI 517 
/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i1901 --YEAR 2018 --MONTH 8 --DAY 14 --YALIWEI 517 
/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i1901 --YEAR 2018 --MONTH 9 --DAY 19 --YALIWEI 508 
/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i1901 --YEAR 2018 --MONTH 10 --DAY 15 --YALIWEI 519 
/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i1901 --YEAR 2018 --MONTH 10 --DAY 23 --YALIWEI 527 
/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i1901 --YEAR 2018 --MONTH 10 --DAY 29 --YALIWEI 540 
/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i1901 --YEAR 2018 --MONTH 10 --DAY 31 --YALIWEI 540
!
#/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i1901 --YEAR 2018 --MONTH 8 --DAY 16 --YALIWEI 508
#/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i1809 --YEAR 2018 --MONTH 5 --DAY 21 --YALIWEI 480
#/d/Anaconda3/python short_model_3_huice.py --SYMBOL DCE.i2009 --YEAR 2020 --MONTH 4 --DAY 15 --YALIWEI 607

#/d/Anaconda3/python short_model_3_huice.py --SYMBOL CZCE.AP010 --YEAR 2020 --MONTH 4 --DAY 15 --YALIWEI 8327 
#无效风控日期
#/d/Anaconda3/python short_model_3.py --SYMBOL DCE.i2009 --YALIWEI 603 --LAST_CLOSE 599.5 --LAST_SETTLEMENT 596.5

/d/Anaconda3/python short_model_3.py --SYMBOL CZCE.AP010 --YALIWEI 8300 &
/d/Anaconda3/python short_model_3.py --SYMBOL DCE.jd2006 --YALIWEI 3400 &